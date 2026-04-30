from sqlalchemy import Column, String
from app.database import Base

class GtfsRoute(Base):
    __tablename__ = "gtfs_route"
    route_id = Column(String, primary_key=True)
    agency_id = Column(String)
    route_short_name = Column(String)
    route_long_name = Column(String)
    route_type = Column(String)
    route_color = Column(String)
    route_text_color = Column(String)
    mode = Column(String)
    mode_label = Column(String)