from pydantic import BaseModel, Field
from datetime import datetime , date
from typing import List, Optional
from enum import Enum


class CityRequest(BaseModel):
    name: str
    country: str = "US"

class EmailSettings(BaseModel):
    recipients: List[str]
    schedule: str
    enabled: bool
    sender_email: Optional[str] = None
    sender_password: Optional[str] = None

class WeatherCondition(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    POOR = "poor"
    DANGEROUS = "dangerous"

class Trail(BaseModel):
    id: int
    name: str
    location: str
    latitude: float
    longitude: float
    elevation: int
    difficulty: str
    description: str

class WeatherData(BaseModel):
    temperature_max: float
    temperature_min : float
    precipitation: float
    wind_speed: float
    wind_direction: int
    weather_code: int
    condition: WeatherCondition
    date: date

class HikeWeather(BaseModel):
    trail : str
    weather : WeatherData

class HikeBooking(BaseModel):
    id: Optional[int] = None
    user_email: str
    trail_id: int
    hike_date: date
    created_at: Optional[datetime] = None
    notification_sent: bool = False

class HikeBookingRequest(BaseModel):
    user_email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    trail_id: int
    hike_date: date
