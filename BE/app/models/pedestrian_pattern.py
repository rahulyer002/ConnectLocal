from sqlalchemy import Column, Integer, String, Float, BigInteger, Boolean
from app.database import Base

class PedestrianPattern(Base):
    __tablename__ = "pedestrian_pattern"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_id = Column(Integer)
    day_of_week = Column(Integer)
    hour = Column(Integer)
    avg_count = Column(Float)
    median_count = Column(Float)
    p25_count = Column(Float)
    p75_count = Column(Float)
    max_count = Column(Integer)
    sample_count = Column(Integer)
    day_name = Column(String)
    crowd_level = Column(String)
    is_quiet_hour = Column(Boolean)
    sensor_description = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    suburb_id = Column(BigInteger)
    suburb_name = Column(String)
    location_type = Column(String)