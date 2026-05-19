import math
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.models.suburb import Suburb
from app.models.landmark import Landmark
from app.models.open_space import OpenSpace
from app.models.category import Category


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Straight-line distance in km between two lat/lon points."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 2)


# ─── Suburbs ──────────────────────────────────────────────────────────────────

def get_suburb_profile(db: Session, suburb_name: str) -> dict | None:
    row = db.query(Suburb).filter(
        func.lower(Suburb.suburb_name).contains(suburb_name.lower().strip())
    ).first()

    if not row:
        return None

    population_65_plus = (
        (row.population_65_74 or 0) +
        (row.population_75_84 or 0) +
        (row.population_85_plus or 0)
    )
    elderly_pct = round(
        (population_65_plus / row.population_total * 100), 1
    ) if row.population_total else None

    return {
        "suburb_id": row.suburb_id,
        "suburb_name": row.suburb_name,
        "centroid_lat": row.centroid_lat,
        "centroid_lng": row.centroid_lng,
        "population_total": row.population_total,
        "population_65_74": row.population_65_74,
        "population_75_84": row.population_75_84,
        "population_85_plus": row.population_85_plus,
        "population_65_plus": population_65_plus,
        "elderly_pct": elderly_pct,
        "need_assistance": row.need_assistance,
        "landmark_count": row.landmark_count,
    }


def search_suburbs(db: Session, query: str, limit: int = 10) -> list[dict]:
    """
    Find suburbs whose name STARTS WITH the user's query (case-insensitive).
    "carl" → Carlton, Carlton North. NOT Macleod (contains 'cl') or Caulfield.
    Ordered alphabetically so the user sees a predictable list.
    """
    q = (query or "").lower().strip()
    if not q:
        return []
    rows = (
        db.query(Suburb)
        .filter(func.lower(Suburb.suburb_name).startswith(q))
        .order_by(Suburb.suburb_name.asc())
        .limit(limit)
        .all()
    )

    return [
        {
            "suburb_id": r.suburb_id,
            "suburb_name": r.suburb_name,
            "centroid_lat": r.centroid_lat,
            "centroid_lng": r.centroid_lng,
        }
        for r in rows
    ]


# ─── Landmarks ────────────────────────────────────────────────────────────────

def get_landmarks_nearby(
    db: Session,
    lat: float,
    lon: float,
    radius_km: float = 2.0,
    theme: str = None,
    limit: int = 20,
) -> list[dict]:
    query = db.query(Landmark)

    if theme:
        query = query.filter(
            func.lower(Landmark.theme).contains(theme.lower())
        )

    landmarks = query.all()

    results = []
    for r in landmarks:
        dist = haversine(lat, lon, r.lat, r.lng)
        if dist <= radius_km:
            results.append({
                "landmark_id": r.landmark_id,
                "name": r.name,
                "theme": r.theme,
                "sub_theme": r.sub_theme,
                "lat": r.lat,
                "lng": r.lng,
                "suburb_name": r.suburb_name,
                "distance_km": dist,
            })

    results.sort(key=lambda x: x["distance_km"])
    return results[:limit]


def get_landmark_themes(db: Session) -> list[dict]:
    rows = db.query(Landmark.theme).distinct().all()
    return [{"theme": r.theme} for r in rows if r.theme]


# ─── Open Spaces ──────────────────────────────────────────────────────────────

def get_open_spaces_nearby(
    db: Session,
    lat: float,
    lon: float,
    radius_km: float = 2.0,
    category: str = None,
    has_toilet: bool = None,
    limit: int = 20,
) -> list[dict]:
    query = db.query(OpenSpace)

    if category:
        query = query.filter(
            func.lower(OpenSpace.category).contains(category.lower())
        )
    if has_toilet is not None:
        query = query.filter(OpenSpace.has_toilet_nearby == has_toilet)

    spaces = query.all()

    results = []
    for r in spaces:
        dist = haversine(lat, lon, r.lat, r.lng)
        if dist <= radius_km:
            results.append({
                "space_id": r.space_id,
                "space_name": r.space_name,
                "space_type": r.space_type,
                "category": r.category,
                "lat": r.lat,
                "lng": r.lng,
                "public_access": r.public_access,
                "managed_by": r.managed_by,
                "walkability_score": round(r.walkability_score, 4) if r.walkability_score else None,
                "has_toilet_nearby": r.has_toilet_nearby,
                "comfort_score": r.comfort_score,
                "distance_km": dist,
            })

    results.sort(key=lambda x: x["distance_km"])
    return results[:limit]


# ─── Categories ───────────────────────────────────────────────────────────────

def get_categories(db: Session, senior_only: bool = False) -> list[dict]:
    query = db.query(Category)
    if senior_only:
        query = query.filter(Category.senior_tag == True)

    rows = query.order_by(Category.category_id).all()

    return [
        {
            "category_id": r.category_id,
            "parent_id": int(r.parent_id) if r.parent_id else None,
            "name": r.name,
            "senior_tag": r.senior_tag,
        }
        for r in rows
    ]