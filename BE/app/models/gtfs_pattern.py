from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class GtfsPattern(Base):
    __tablename__ = "gtfs_pattern"
    id = Column(Integer, primary_key=True, autoincrement=True)
    stop_id = Column(String)
    hour = Column(Integer)
    departure_count = Column(Integer)
    mode = Column(String)
    avg_departures_per_hour = Column(Float)