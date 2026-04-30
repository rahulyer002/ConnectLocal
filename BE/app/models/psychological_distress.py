from sqlalchemy import Column, Integer, String, Float
from app.database import Base


class PsychologicalDistress(Base):
    __tablename__ = "psychological_distress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    age_group = Column(String)
    psychological_distress_percent = Column(Float)
    year = Column(String)
    source = Column(String)