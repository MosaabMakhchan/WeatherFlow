from fastapi import FastAPI, HTTPException
import httpx
import os

app = FastAPI()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "your_api_key_here")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

@app.get("/weather")
async def get_weather():
    city = "London,UK"  # hardcoded for minimal test
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                OPENWEATHER_BASE_URL,
                params={"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"}
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "city": city,
                "temperature": data["main"]["temp"],
                "description": data["weather"][0]["description"]
            }
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="Weather API error")
