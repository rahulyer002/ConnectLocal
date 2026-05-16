"""
Inference service — computes elderly-friendliness scores per suburb.

Two responsibilities:
  1. compute_all(db)             — batch computation across every suburb,
                                   called once by load_data.load_suburb_inference()
  2. get_for_suburb(db, sid)     — fast PK lookup at request time

The scores are deliberately simple log-normalised aggregates of existing
data. They are NOT a ground-truth measure of elderly wellbeing — they are
a fast comparative signal across suburbs. The "strengths" / "gaps" labels
are computed from the same numbers so the narrative stays internally
consistent.
"""
import math
from typing import Optional
from collections import Counter

import numpy as np
from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.models.suburb import Suburb
from app.models.suburb_inference import SuburbInference
from app.models.osm_bench import OsmBench
from app.models.osm_accessible_toilet import OsmAccessibleToilet
from app.models.osm_wheelchair_place import OsmWheelchairPlace
from app.models.tree import Tree
from app.models.gtfs_stop import GtfsStop
from app.models.landmark import Landmark
from app.models.open_space import OpenSpace


CBD_LAT, CBD_LNG = -37.8180, 144.9690

WELCOMING_THEMES = {
    "Community Use",
    "Health Services",
    "Education Centre",
    "Mixed Use",
}

SUB_SCORE_NAMES = ["rest", "relief", "amenities", "shade", "transit", "social"]

STRENGTH_THRESHOLD = 75.0
GAP_THRESHOLD = 25.0


# ─── Aggregation helpers ────────────────────────────────────────────────────

def _count_by_suburb(db: Session, model, extra_filter=None) -> dict[int, int]:
    """Return {suburb_id: count} for any model with a suburb_id column."""
    q = db.query(model.suburb_id, func.count()).group_by(model.suburb_id)
    if extra_filter is not None:
        q = q.filter(extra_filter)
    return {sid: c for sid, c in q.all() if sid is not None}


def _wc_place_breakdown(db: Session) -> dict[int, Counter]:
    """{suburb_id: Counter({'social': N, 'essentials': M, ...})}."""
    rows = db.query(
        OsmWheelchairPlace.suburb_id,
        OsmWheelchairPlace.amenity_category,
        func.count(),
    ).group_by(
        OsmWheelchairPlace.suburb_id, OsmWheelchairPlace.amenity_category,
    ).all()
    out: dict[int, Counter] = {}
    for sid, cat, n in rows:
        if sid is None:
            continue
        out.setdefault(sid, Counter())[cat or "other"] = n
    return out


def _wheelchair_stops_by_suburb(db: Session) -> dict[int, int]:
    """Stops where is_wheelchair_accessible = True, by suburb."""
    return _count_by_suburb(db, GtfsStop, extra_filter=GtfsStop.is_wheelchair_accessible.is_(True))


def _stop_modes_by_suburb(db: Session) -> dict[int, int]:
    rows = db.query(GtfsStop.suburb_id, func.count(func.distinct(GtfsStop.mode))) \
             .group_by(GtfsStop.suburb_id).all()
    return {sid: m for sid, m in rows if sid is not None}


def _avg_tree_shade_by_suburb(db: Session) -> dict[int, Optional[float]]:
    rows = db.query(Tree.suburb_id, func.avg(Tree.shade_score)) \
             .group_by(Tree.suburb_id).all()
    return {sid: (float(s) if s is not None else None) for sid, s in rows if sid is not None}


def _welcoming_by_suburb(db: Session) -> dict[int, int]:
    """Landmarks whose theme falls in our welcoming-theme allow-list."""
    rows = db.query(Landmark.suburb_id, func.count()) \
             .filter(Landmark.theme.in_(list(WELCOMING_THEMES))) \
             .group_by(Landmark.suburb_id).all()
    return {sid: c for sid, c in rows if sid is not None}


# ─── Score math ─────────────────────────────────────────────────────────────

def _log_normalize(values: list[float]) -> list[float]:
    """Map a heavy-tailed array to 0..100 using log(1+x) and 5th/95th percentile clipping."""
    arr = np.array([v if v is not None else 0.0 for v in values], dtype=float)
    arr = np.log1p(arr)
    lo = float(np.quantile(arr, 0.05))
    hi = float(np.quantile(arr, 0.95))
    if hi == lo:
        return [50.0] * len(values)
    z = np.clip((arr - lo) / (hi - lo), 0.0, 1.0)
    return [round(float(v) * 100, 1) for v in z]


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _assign_persona(row: dict) -> str:
    """Coarse rule-based clustering. Order matters: first match wins."""
    dist = row.get("dist_to_cbd_km")
    stops = row.get("stop_count") or 0
    welcoming = row.get("welcoming_spaces") or 0
    greens = row.get("green_space_count") or 0
    trees = row.get("tree_count") or 0
    avg_shade = row.get("avg_tree_shade") or 0
    elderly_pct = row.get("elderly_pct") or 0
    wc_places = row.get("wc_place_count") or 0

    if dist is not None and dist < 5 and stops > 30:
        return "Urban Core"
    if welcoming >= 3 and greens >= 1:
        return "Community Hub"
    if trees > 1000 and avg_shade > 0.001:
        return "Leafy Retreat"
    if elderly_pct > 25:
        return "Elderly-Heavy"
    if dist is not None and dist > 30 and stops < 5:
        return "Outer / Limited Transit"
    if stops > 10 and wc_places > 50:
        return "Service Rich"
    return "Suburban Mixed"


def _compute_peers(score_matrix: np.ndarray, ids: list[int], names: dict[int, str],
                   outing_scores: list[float], top_k: int = 3) -> list[list[dict]]:
    """For each suburb, return the top_k most similar suburbs by Euclidean
    distance in the 6-dim score vector. Excludes self.
    """
    score_index_by_metric = {n: i for i, n in enumerate(SUB_SCORE_NAMES)}
    diffs = score_matrix[:, None, :] - score_matrix[None, :, :]
    dist = np.sqrt((diffs * diffs).sum(axis=2))
    np.fill_diagonal(dist, np.inf)
    order = np.argsort(dist, axis=1)[:, :top_k]

    peer_lists: list[list[dict]] = []
    for i, idx_row in enumerate(order):
        peers = []
        my_vec = score_matrix[i]
        for j in idx_row:
            their_vec = score_matrix[j]
            metric_diffs = np.abs(my_vec - their_vec)
            best_metric = SUB_SCORE_NAMES[int(np.argmin(metric_diffs))]
            peers.append({
                "suburb_id":    int(ids[j]),
                "suburb_name":  names.get(int(ids[j]), ""),
                "outing_score": outing_scores[j],
                "reason":       f"Similar {best_metric} score",
            })
        peer_lists.append(peers)
    return peer_lists


# ─── The batch compute entry point ──────────────────────────────────────────

def compute_all(db: Session) -> list[dict]:
    """Compute inference rows for every suburb. Returns a list of dicts
    ready to insert into suburb_inference."""
    suburbs = db.query(Suburb).all()
    if not suburbs:
        return []

    ids = [int(s.suburb_id) for s in suburbs]
    names = {int(s.suburb_id): s.suburb_name for s in suburbs}

    benches    = _count_by_suburb(db, OsmBench)
    toilets    = _count_by_suburb(db, OsmAccessibleToilet)
    wc_places  = _count_by_suburb(db, OsmWheelchairPlace)
    trees      = _count_by_suburb(db, Tree)
    stops      = _count_by_suburb(db, GtfsStop)
    greens     = _count_by_suburb(db, OpenSpace)
    landmarks  = _count_by_suburb(db, Landmark)
    welcoming  = _welcoming_by_suburb(db)
    wc_stops   = _wheelchair_stops_by_suburb(db)
    stop_modes = _stop_modes_by_suburb(db)
    avg_shade  = _avg_tree_shade_by_suburb(db)
    wc_break   = _wc_place_breakdown(db)

    bench_arr  = [benches.get(sid, 0)   for sid in ids]
    toilet_arr = [toilets.get(sid, 0)   for sid in ids]
    wcplc_arr  = [wc_places.get(sid, 0) for sid in ids]
    shade_arr  = [trees.get(sid, 0) * (avg_shade.get(sid) or 0) for sid in ids]
    stop_arr   = [stops.get(sid, 0)     for sid in ids]
    wcstop_arr = [wc_stops.get(sid, 0)  for sid in ids]
    welcome_arr = [welcoming.get(sid, 0) for sid in ids]
    green_arr  = [greens.get(sid, 0)    for sid in ids]
    wc_soc_arr = [(wc_break.get(sid, {}).get("social", 0)) for sid in ids]
    wc_ess_arr = [(wc_break.get(sid, {}).get("essentials", 0)) for sid in ids]

    score_rest      = _log_normalize(bench_arr)
    score_relief    = _log_normalize(toilet_arr)
    score_amenities = _log_normalize(wcplc_arr)
    score_shade     = _log_normalize(shade_arr)

    transit_count = _log_normalize(stop_arr)
    transit_wc    = _log_normalize(wcstop_arr)
    score_transit = [round(0.6 * a + 0.4 * b, 1) for a, b in zip(transit_count, transit_wc)]

    social_a = _log_normalize([w + s + e for w, s, e in zip(welcome_arr, wc_soc_arr, wc_ess_arr)])
    social_b = _log_normalize(green_arr)
    score_social = [round(0.5 * a + 0.5 * b, 1) for a, b in zip(social_a, social_b)]

    score_matrix = np.array(list(zip(
        score_rest, score_relief, score_amenities, score_shade, score_transit, score_social
    )), dtype=float)
    weights = np.array([0.20, 0.20, 0.15, 0.10, 0.20, 0.15])
    outing_scores = [round(float(v), 1) for v in (score_matrix * weights).sum(axis=1)]

    peer_lists = _compute_peers(score_matrix, ids, names, outing_scores)

    data_signal_keys = [benches, toilets, wc_places, trees, stops, greens, landmarks, welcoming]

    rows = []
    for i, s in enumerate(suburbs):
        sid = int(s.suburb_id)
        elderly_total = (s.population_65_74 or 0) + (s.population_75_84 or 0) + (s.population_85_plus or 0)
        pop_total = s.population_total or 0
        elderly_pct = round(elderly_total / pop_total * 100, 2) if pop_total > 0 else None
        dist_cbd = _haversine_km(s.centroid_lat, s.centroid_lng, CBD_LAT, CBD_LNG) \
            if (s.centroid_lat is not None and s.centroid_lng is not None) else None

        signals_present = sum(1 for d in data_signal_keys if sid in d and d[sid] > 0)
        completeness = round(signals_present / len(data_signal_keys) * 100, 1)

        sub_scores = {
            "rest": score_rest[i], "relief": score_relief[i], "amenities": score_amenities[i],
            "shade": score_shade[i], "transit": score_transit[i], "social": score_social[i],
        }
        strengths = [k for k, v in sub_scores.items() if v >= STRENGTH_THRESHOLD]
        gaps      = [k for k, v in sub_scores.items() if v < GAP_THRESHOLD]

        b = bench_arr[i]; t = toilet_arr[i]; p = wcplc_arr[i]
        ratio = lambda n: round(n / elderly_total * 100, 2) if elderly_total > 0 else None

        row = dict(
            suburb_id=sid,
            score_rest=score_rest[i], score_relief=score_relief[i],
            score_amenities=score_amenities[i], score_shade=score_shade[i],
            score_transit=score_transit[i], score_social=score_social[i],
            outing_score=outing_scores[i],
            persona=None,
            data_completeness_pct=completeness,
            strengths=strengths,
            gaps=gaps,
            peer_suburbs=peer_lists[i],
            benches_per_100_elderly=ratio(b),
            toilets_per_100_elderly=ratio(t),
            wc_places_per_100_elderly=ratio(p),
            elderly_total=elderly_total,
            elderly_pct=elderly_pct,
            welcoming_spaces=welcome_arr[i],
            wc_place_count=p,
            wc_social_count=wc_soc_arr[i],
            wc_essentials_count=wc_ess_arr[i],
            wc_healthcare_count=wc_break.get(sid, {}).get("healthcare", 0),
            bench_count=b,
            toilet_count=t,
            tree_count=trees.get(sid, 0),
            stop_count=stop_arr[i],
            wc_stop_count=wcstop_arr[i],
            stop_modes=stop_modes.get(sid, 0),
            green_space_count=green_arr[i],
            avg_tree_shade=avg_shade.get(sid),
            dist_to_cbd_km=round(dist_cbd, 2) if dist_cbd is not None else None,
        )
        row["persona"] = _assign_persona(row)
        rows.append(row)

    return rows


# ─── Request-time helpers ───────────────────────────────────────────────────

def get_for_suburb(db: Session, suburb_id: int) -> Optional[SuburbInference]:
    return db.query(SuburbInference).filter(SuburbInference.suburb_id == suburb_id).first()


def get_rankings(db: Session, metric: str, persona: Optional[str], top: int) -> list[SuburbInference]:
    col = getattr(SuburbInference, metric)
    q = db.query(SuburbInference).filter(col.isnot(None))
    if persona:
        q = q.filter(SuburbInference.persona == persona)
    return q.order_by(col.desc()).limit(top).all()


def suburb_name_map(db: Session, ids: list[int]) -> dict[int, str]:
    if not ids:
        return {}
    rows = db.query(Suburb.suburb_id, Suburb.suburb_name).filter(Suburb.suburb_id.in_(ids)).all()
    return {int(sid): name for sid, name in rows}
