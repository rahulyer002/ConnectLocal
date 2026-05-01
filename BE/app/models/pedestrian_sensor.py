from sqlalchemy import Column, Integer, String, Float, BigInteger
from app.database import Base

class PedestrianSensor(Base):
    __tablename__ = "pedestrian_sensor"
    sensor_id = Column(Integer, primary_key=True)
    sensor_name = Column(String)
    sensor_description = Column(String)
    location_type = Column(String)
    status = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    direction_1 = Column(String)
    direction_2 = Column(String)
    suburb_id = Column(BigInteger)
    suburb_name = Column(String)