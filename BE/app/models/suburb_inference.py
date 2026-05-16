"""
Precomputed elderly-friendliness inference per suburb.

Populated once by `app.etl.load_data.load_suburb_inference()` after all the
underlying tables (osm_bench, tree, gtfs_stop, landmark, open_space, etc.)
have been loaded. Served at request time via /api/suburbs/{id}/inference
as a single indexed PK lookup — ~5ms typical.

Re-run the loader whenever the underlying counts change.
"""
from sqlalchemy import Column, BigInteger, String, Float, Integer, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class SuburbInference(Base):
    __tablename__ = "suburb_inference"

    suburb_id = Column(BigInteger, primary_key=True)

    # Sub-scores 0-100 (log-normalized counts of underlying data)
    score_rest      = Column(Float)  # bench density
    score_relief    = Column(Float)  # accessible toilet density
    score_amenities = Column(Float)  # wheelchair-accessible venues
    score_shade     = Column(Float)  # tree_count × avg shade
    score_transit   = Column(Float)  # stops + wheelchair-stop fraction
    score_social    = Column(Float)  # welcoming spaces + parks

    # Composite + classification
    outing_score          = Column(Float, index=True)
    persona               = Column(String(64), index=True)
    data_completeness_pct = Column(Float)

    # Narrative — sub-score names where score >= 75 / < 25
    strengths = Column(JSON)   # e.g. ["rest", "amenities"]
    gaps      = Column(JSON)   # e.g. ["shade"]

    # Peer suburbs — 3 nearest by Euclidean distance in score-space
    # Stored as JSON list of {id, name, score, reason}
    peer_suburbs = Column(JSON)

    # Per-capita ratios (services per 100 elderly residents)
    benches_per_100_elderly   = Column(Float)
    toilets_per_100_elderly   = Column(Float)
    wc_places_per_100_elderly = Column(Float)

    # Convenience counts (avoid joins at request time)
    elderly_total     = Column(Integer)
    elderly_pct       = Column(Float)
    welcoming_spaces  = Column(Integer)
    wc_place_count    = Column(Integer)
    wc_social_count   = Column(Integer)
    wc_essentials_count = Column(Integer)
    wc_healthcare_count = Column(Integer)
    bench_count       = Column(Integer)
    toilet_count      = Column(Integer)
    tree_count        = Column(Integer)
    stop_count        = Column(Integer)
    wc_stop_count     = Column(Integer)
    stop_modes        = Column(Integer)
    green_space_count = Column(Integer)
    avg_tree_shade    = Column(Float)
    dist_to_cbd_km    = Column(Float)

    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self) -> dict:
        return {
            "suburb_id":          self.suburb_id,
            "scores": {
                "rest":      self.score_rest,
                "relief":    self.score_relief,
                "amenities": self.score_amenities,
                "shade":     self.score_shade,
                "transit":   self.score_transit,
                "social":    self.score_social,
            },
            "outing_score":          self.outing_score,
            "persona":               self.persona,
            "data_completeness_pct": self.data_completeness_pct,
            "strengths":             self.strengths or [],
            "gaps":                  self.gaps or [],
            "peer_suburbs":          self.peer_suburbs or [],
            "per_capita": {
                "benches_per_100_elderly":   self.benches_per_100_elderly,
                "toilets_per_100_elderly":   self.toilets_per_100_elderly,
                "wc_places_per_100_elderly": self.wc_places_per_100_elderly,
            },
            "counts": {
                "elderly_total":       self.elderly_total,
                "elderly_pct":         self.elderly_pct,
                "welcoming_spaces":    self.welcoming_spaces,
                "wc_place_count":      self.wc_place_count,
                "wc_social_count":     self.wc_social_count,
                "wc_essentials_count": self.wc_essentials_count,
                "wc_healthcare_count": self.wc_healthcare_count,
                "bench_count":         self.bench_count,
                "toilet_count":        self.toilet_count,
                "tree_count":          self.tree_count,
                "stop_count":          self.stop_count,
                "wc_stop_count":       self.wc_stop_count,
                "stop_modes":          self.stop_modes,
                "green_space_count":   self.green_space_count,
                "avg_tree_shade":      self.avg_tree_shade,
                "dist_to_cbd_km":      self.dist_to_cbd_km,
            },
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
        }

    def to_dict_compact(self) -> dict:
        """Slim payload for ranking lists — name comes from join, not stored here."""
        return {
            "suburb_id":    self.suburb_id,
            "outing_score": self.outing_score,
            "persona":      self.persona,
            "elderly_pct":  self.elderly_pct,
            "scores": {
                "rest":      self.score_rest,
                "relief":    self.score_relief,
                "amenities": self.score_amenities,
                "shade":     self.score_shade,
                "transit":   self.score_transit,
                "social":    self.score_social,
            },
        }
