from sqlalchemy import Column, Integer, String, Float, BigInteger, Boolean
from app.database import Base


class OpenSpace(Base):
    __tablename__ = "open_space"

    space_id = Column(Integer, primary_key=True)
    suburb_id = Column(BigInteger)
    space_name = Column(String, nullable=False)
    space_type = Column(String)
    category = Column(String)
    area_ha = Column(Float)
    public_access = Column(Boolean)
    managed_by = Column(String)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    walkability_score = Column(Float)
    has_toilet_nearby = Column(Boolean)
    comfort_score = Column(Float)
    # NEW — merged from processed/open_space_shade.csv
    shade_score_100 = Column(Float)
    nearby_tree_count = Column(Integer)