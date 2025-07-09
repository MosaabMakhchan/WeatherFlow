from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from functions.fetch_weather import fetch_weather_data
from functions.scheduler import daily_weather_report
from models.models import CityRequest, EmailSettings, WeatherResponse

app = FastAPI(title="Weather Dashboard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# API Routes
@app.get("/")
async def root():
    return {"message": "Weather Dashboard API"}

@app.get("/cities")
async def get_cities():
    """Get all cities"""
    return list(cities_data.keys())

@app.post("/cities")
async def add_city(city_request: CityRequest):
    """Add a new city"""
    city_name = f"{city_request.name}, {city_request.country}"
    
    # Validate city exists by fetching weather data
    try:
        weather_data = await fetch_weather_data(city_name)
        cities_data[city_name] = {
            "added_at": datetime.now().isoformat(),
            "country": city_request.country
        }
        return {"message": f"City {city_name} added successfully"}
    except HTTPException as e:
        raise e

@app.delete("/cities/{city_name}")
async def remove_city(city_name: str):
    """Remove a city"""
    if city_name not in cities_data:
        raise HTTPException(status_code=404, detail="City not found")
    
    del cities_data[city_name]
    return {"message": f"City {city_name} removed successfully"}

@app.get("/weather")
async def get_all_weather():
    """Get current weather for all cities"""
    weather_results = []
    
    for city in cities_data.keys():
        try:
            weather_data = await fetch_weather_data(city)
            weather_results.append({
                "city": city,
                "temperature": weather_data['main']['temp'],
                "description": weather_data['weather'][0]['description'],
                "humidity": weather_data['main']['humidity'],
                "wind_speed": weather_data['wind']['speed'],
                "timestamp": datetime.now()
            })
        except Exception as e:
            print(f"Error fetching weather for {city}: {str(e)}")
            continue
    
    return weather_results

@app.get("/weather/{city_name}")
async def get_city_weather(city_name: str):
    """Get weather for specific city"""
    if city_name not in cities_data:
        raise HTTPException(status_code=404, detail="City not found")
    
    try:
        weather_data = await fetch_weather_data(city_name)
        return WeatherResponse(
            city=city_name,
            temperature=weather_data['main']['temp'],
            description=weather_data['weather'][0]['description'],
            humidity=weather_data['main']['humidity'],
            wind_speed=weather_data['wind']['speed'],
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/email-settings")
async def get_email_settings():
    """Get email settings (without sensitive data)"""
    safe_settings = email_settings.copy()
    safe_settings.pop('sender_password', None)
    return safe_settings

@app.post("/email-settings")
async def update_email_settings(settings: EmailSettings):
    """Update email settings"""
    global email_settings
    
    # Update settings
    email_settings['recipients'] = settings.recipients
    email_settings['schedule'] = settings.schedule
    email_settings['enabled'] = settings.enabled
    
    if settings.sender_email:
        email_settings['sender_email'] = settings.sender_email
    if settings.sender_password:
        email_settings['sender_password'] = settings.sender_password
    
    # Update scheduler
    scheduler.remove_all_jobs()
    if settings.enabled:
        hour, minute = settings.schedule.split(':')
        scheduler.add_job(
            daily_weather_report,
            CronTrigger(hour=int(hour), minute=int(minute)),
            id='daily_weather_report'
        )
    
    return {"message": "Email settings updated successfully"}

@app.post("/test-email")
async def test_email():
    """Test email functionality"""
    if not email_settings['enabled']:
        raise HTTPException(status_code=400, detail="Email is not enabled")
    
    await daily_weather_report()
    return {"message": "Test email sent"}

if __name__ == "__main__":
    # import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    pass