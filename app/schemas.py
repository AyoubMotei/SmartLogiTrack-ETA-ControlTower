from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Input for prediction
class TripFeatures(BaseModel):
    trip_distance: float
    pickup_hour: int
    day_of_week: int
    month: int

# Output for prediction
class PredictionResponse(BaseModel):
    estimated_duration: float
   

# Analytics Response
class AvgDurationByHour(BaseModel):
    pickuphour: int
    avgduration: float

class PaymentAnalysis(BaseModel):
    payment_type: int
    total_trips: int
    avg_duration: float

# Auth
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    disabled: Optional[bool] = None
