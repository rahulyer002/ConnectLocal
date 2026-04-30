from sqlalchemy import Column, Integer, String, Float, BigInteger
from app.database import Base

class Tree(Base):
    __tablename__ = "tree"
    tree_id = Column(Integer, primary_key=True)
    common_name = Column(String)
    genus = Column(String)
    dbh_cm = Column(Float)
    useful_life_years = Column(Float)
    useful_life_label = Column(String)
    age_description = Column(String)
    located_in = Column(String)
    precinct = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    shade_score = Column(Float)
    suburb_id = Column(BigInteger)