from celery import shared_task

from datetime import datetime
import requests

# @shared_task
# def fetch_hourly_data_function(s):
#     return s

# @shared_task
# def add(x, y):
#     return x + y

# @shared_task
# def fetch_and_store_temperatures(latitude, longitude, travel_date):

#     from .models import WeatherData

#     url = "https://api.open-meteo.com/v1/forecast"
#     params = {
#         "latitude": latitude,
#         "longitude": longitude,
#         "hourly": "temperature_2m",
#         "start": travel_date + "T14:00:00Z",  # Set the time to 2 PM on the travel date
#         "end": travel_date + "T14:00:00Z",  # Only fetch data for 2 PM on the travel date
#     }

@shared_task
def fetch_and_store_temperatures(latitude, longitude, travel_date):
    from .models import WeatherData
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m",
        "start": travel_date + "T14:00:00Z",  # Set the time to 2 PM on the travel date
        "end": travel_date + "T14:00:00Z",  # Only fetch data for 2 PM on the travel date
    }
    
    response = requests.get(url, params=params)
    data = response.json()

    # Extract temperature at 2 PM for the specified date
    temperature = data.get("hourly", {}).get("temperature_2m", [])
    if temperature:
        temperature = temperature[0]["value"]  # Get the temperature at 2 PM on the travel date
    else:
        temperature = None

    # Store data in the database (WeatherData model)
    WeatherData.objects.create(latitude=latitude, longitude=longitude, date=travel_date, temperature=temperature)

    return f"Weather data for {travel_date} fetched and stored successfully!"

