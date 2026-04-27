from sqlalchemy import Column, Integer, String, Float, Boolean
from app.database import Base


class Category(Base):
    __tablename__ = "category"

    category_id = Column(Integer, primary_key=True)
    parent_id = Column(Float)
    name = Column(String, nullable=False)
    senior_tag = Column(Boolean)