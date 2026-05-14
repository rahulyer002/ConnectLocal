from sqlalchemy import Column, String, Float, BigInteger, Boolean
from app.database import Base


class OsmAccessibleToilet(Base):
    """OpenStreetMap accessible toilets — 25× the coverage of /api/greenspace/toilets (which is CoM LGA only)."""
    __tablename__ = "osm_accessible_toilet"

    osm_id = Column(String, primary_key=True)
    name = Column(String)
    wheelchair = Column(String)            # yes / no / limited / designated / null
    toilets_wheelchair = Column(String)    # toilet-specific OSM tag
    opening_hours = Column(String)
    operator = Column(String)
    is_accessible = Column(Boolean, default=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    suburb_id = Column(BigInteger, index=True)
    suburb_name = Column(String)
