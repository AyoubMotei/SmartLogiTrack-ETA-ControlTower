from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from .database import Base

class ETAPrediction(Base):
    __tablename__ = "eta_predictions"

    id = Column(Integer, primary_key=True, index=True)
    trip_distance = Column(Float)
    pickup_hour = Column(Integer)
    day_of_week = Column(Integer)
    month = Column(Integer)
    estimated_duration = Column(Float)
    model_version = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
