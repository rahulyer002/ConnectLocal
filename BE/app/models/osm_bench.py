from sqlalchemy import Column, String, Float, BigInteger
from app.database import Base


class OsmBench(Base):
    """OpenStreetMap public benches — ~10K rows after Victoria bbox filter."""
    __tablename__ = "osm_bench"

    osm_id = Column(String, primary_key=True)
    name = Column(String)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    suburb_id = Column(BigInteger, index=True)
    suburb_name = Column(String)
