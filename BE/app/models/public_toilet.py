from sqlalchemy import Column, Integer, String, Float, BigInteger, Boolean
from app.database import Base

class PublicToilet(Base):
    __tablename__ = "public_toilet"
    toilet_id = Column(Integer, primary_key=True)
    suburb_id = Column(BigInteger)
    suburb_name = Column(String)
    name = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    has_female = Column(Boolean)
    has_male = Column(Boolean)
    has_wheelchair = Column(Boolean)
    has_baby_facility = Column(Boolean)
    operator = Column(String)