# Scheduled task function
from functions.email import send_weather_email
from functions.fetch_weather import fetch_weather_data


email_settings = {
    "recipients": [],
    "schedule": "09:00",
    "enabled": False,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "",
    "sender_password": ""
}
cities_data = {}


async def daily_weather_report():
    """Generate and send daily weather report"""
    if not email_settings['enabled']:
        return
    
    weather_data = {}
    for city in cities_data.keys():
        try:
            data = await fetch_weather_data(city)
            weather_data[city] = {
                'temperature': data['main']['temp'],
                'description': data['weather'][0]['description']
            }
        except Exception as e:
            print(f"Error fetching weather for {city}: {str(e)}")
    
    if weather_data:
        send_weather_email(weather_data)