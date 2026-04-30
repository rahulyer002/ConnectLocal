from sqlalchemy import Column, Integer, String, Float, BigInteger, Boolean
from app.database import Base

class MicroClimateSensor(Base):
    __tablename__ = "microclimate_sensor"
    site_id = Column(Integer, primary_key=True)
    gatewayhub_id = Column(String)
    site_status = Column(String)
    is_active = Column(Boolean)
    start_reading = Column(String)
    end_reading = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    suburb_id = Column(BigInteger)
    suburb_name = Column(String)