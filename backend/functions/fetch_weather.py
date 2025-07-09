import httpx
import os
from fastapi import HTTPException

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "your_api_key_here")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

async def fetch_weather_data(city: str) -> dict:
    """Fetch weather data from OpenWeatherMap API"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                OPENWEATHER_BASE_URL,
                params={
                    "q": city,
                    "appid": OPENWEATHER_API_KEY,
                    "units": "metric"
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Error fetching weather data: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="Weather API error")
