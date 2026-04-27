from sqlalchemy import Column, Integer, String, Float, BigInteger, Boolean
from app.database import Base


class Landmark(Base):
    __tablename__ = "landmark"

    landmark_id = Column(Integer, primary_key=True)
    suburb_id = Column(BigInteger)
    suburb_name = Column(String)
    name = Column(String, nullable=False)
    theme = Column(String)
    sub_theme = Column(String)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    is_welcoming_space = Column(Boolean)
    clue_small_area = Column(String)