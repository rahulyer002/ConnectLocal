from sqlalchemy import Column, String, Float, BigInteger, Boolean
from app.database import Base


class OsmWheelchairPlace(Base):
    """OpenStreetMap wheelchair-accessible venues — cafes, libraries, pharmacies, community centres etc."""
    __tablename__ = "osm_wheelchair_place"

    osm_id = Column(String, primary_key=True)
    name = Column(String)
    amenity = Column(String)                       # raw OSM tag: cafe, library, pharmacy, ...
    amenity_category = Column(String, index=True)  # our buckets: essentials/social/healthcare/aged_care_social/transit/other
    wheelchair = Column(String)
    operator = Column(String)
    opening_hours = Column(String)
    description = Column(String)
    is_accessible = Column(Boolean, default=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    suburb_id = Column(BigInteger, index=True)
    suburb_name = Column(String)
