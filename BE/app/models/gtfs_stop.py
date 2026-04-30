from sqlalchemy import Column, Integer, String, Float, BigInteger, Boolean
from app.database import Base

class GtfsStop(Base):
    __tablename__ = "gtfs_stop"
    stop_id = Column(String, primary_key=True)
    stop_name = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    mode = Column(String)
    location_type = Column(String)
    parent_station = Column(String)
    wheelchair_boarding = Column(String)
    is_wheelchair_accessible = Column(Boolean)
    is_wheelchair_inaccessible = Column(Boolean)
    routes_served = Column(String)
    route_count = Column(Integer)
    suburb_id = Column(BigInteger)
    suburb_name = Column(String)