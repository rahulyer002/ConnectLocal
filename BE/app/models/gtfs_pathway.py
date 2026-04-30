from sqlalchemy import Column, String, Boolean, Float
from app.database import Base


class GtfsPathway(Base):
    __tablename__ = "gtfs_pathway"

    pathway_id = Column(String, primary_key=True)
    from_stop_id = Column(String)
    to_stop_id = Column(String)
    pathway_mode = Column(String)
    pathway_mode_label = Column(String)
    has_elevator = Column(Boolean)
    has_stairs = Column(Boolean)
    is_bidirectional = Column(String)
    traversal_time = Column(Float)