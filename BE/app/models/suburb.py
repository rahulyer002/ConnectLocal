from sqlalchemy import Column, Integer, String, Float, BigInteger
from app.database import Base


class Suburb(Base):
    __tablename__ = "suburb"

    suburb_id = Column(BigInteger, primary_key=True)
    suburb_name = Column(String, nullable=False)
    centroid_lat = Column(Float, nullable=False)
    centroid_lng = Column(Float, nullable=False)
    population_total = Column(Integer)
    population_65_74 = Column(Integer)
    population_75_84 = Column(Integer)
    population_85_plus = Column(Integer)
    need_assistance = Column(Integer)
    landmark_count = Column(Integer)