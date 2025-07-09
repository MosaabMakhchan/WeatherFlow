import json
import orjson
from datetime import date
from typing import List
from fastapi import FastAPI, HTTPException
import httpx
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from fastapi.middleware.cors import CORSMiddleware

from database.in_memory_db import get_all_trails
from models.models import HikeWeather, Trail, WeatherCondition, WeatherData

app = FastAPI(title="TrailCast App", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up the Open-Meteo client
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)


class WeatherService:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    
    @staticmethod
    async def get_weather(latitude : float , logitude : float , target_date : date) -> WeatherData:
        params = {
            "latitude": latitude,
            "longitude": logitude,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,wind_direction_10m_dominant,weather_code",
            "start_date": target_date.isoformat(),
            "end_date": target_date.isoformat(),
            "timezone": "auto"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(WeatherService.BASE_URL , params=params)
            response.raise_for_status()
            
            result_json = response.json()

            daily_data = result_json["daily"]
            temperature_max = daily_data["temperature_2m_max"][0]
            temperature_min = daily_data["temperature_2m_min"][0]
            precipitation = daily_data["precipitation_sum"][0]
            wind_speed_max = daily_data["wind_speed_10m_max"][0]
            wind_directioin = daily_data["wind_direction_10m_dominant"][0]
            weather_code = daily_data["weather_code"][0]
            avg_temp = (temperature_max + temperature_min)/2

            condition = WeatherService.evaluate_hiking_conditions(
                avg_temp, precipitation, wind_speed_max, weather_code
            )
            print("here", target_date)


            return WeatherData(
                temperature_max = temperature_max,
                temperature_min = temperature_max,
                precipitation= precipitation,
                wind_speed= wind_speed_max,
                wind_direction= wind_directioin,
                date= target_date,
                weather_code= weather_code,
                condition=condition,
            )
        
    @staticmethod
    def evaluate_hiking_conditions(temp: float, precipitation: float, wind_speed: float, weather_code: int) -> WeatherCondition:
        
        # Dangerous conditions
        if weather_code in [95, 96, 99]:  # Thunderstorms
            return WeatherCondition.DANGEROUS
        if wind_speed > 60:  # Very strong winds
            return WeatherCondition.DANGEROUS
        if precipitation > 20:  # Heavy rain
            return WeatherCondition.DANGEROUS
        
        # Poor conditions
        if weather_code in [51, 53, 55, 61, 63, 65, 71, 73, 75]:  # Rain/Snow
            return WeatherCondition.POOR
        if wind_speed > 40:
            return WeatherCondition.POOR
        if temp < -10 or temp > 35:
            return WeatherCondition.POOR
        
        # Moderate conditions
        if precipitation > 5:
            return WeatherCondition.MODERATE
        if wind_speed > 25:
            return WeatherCondition.MODERATE
        if temp < 0 or temp > 30:
            return WeatherCondition.MODERATE
        
        # Good conditions
        if weather_code in [1, 2, 3]:  # Partly cloudy
            return WeatherCondition.GOOD
        if 5 <= temp <= 25:
            return WeatherCondition.GOOD
        
        # Excellent conditions
        if weather_code == 0:  # Clear sky
            return WeatherCondition.EXCELLENT
        if 10 <= temp <= 20 and precipitation == 0 and wind_speed < 15:
            return WeatherCondition.EXCELLENT
        
        return WeatherCondition.MODERATE
    

@app.get("/get_trails",response_model=List[Trail])
async def get_trails():
    result = get_all_trails()
    return result


@app.get("/get_weather_trails")
async def get_weather_trails():
    trails = get_all_trails()
    weather_list = []

    for trail in trails:
        try:
            weather = await WeatherService.get_weather(
                trail.latitude,
                trail.longitude,
                target_date=date.today()
            )

            trail_weather = HikeWeather(
                    trail = trail.name,
                    weather = weather
                )
            weather_list.append(
                trail_weather
            )

        except httpx.HTTPError as e:
            weather_list.append({
                "trail": trail.name,
                "error": f"Failed to fetch weather: {str(e)}"
            })

    return weather_list