import requests
import datetime as dt
from config import WEATHER_API

BASE_URL = 'http://api.openweathermap.org/data/2.5/weather?'

# GET DATA
def get_info(city: str):
    url = f"{BASE_URL}appid={WEATHER_API}&q={city}"

    response = requests.get(url).json()

    if response.get("cod") != 200:
        return None

    temp_kelvin = response['main']['temp']
    temp_celsius = temp_kelvin - 273.15
    feel_like_kelvin = response['main']['feels_like']
    feel_like_celsius = feel_like_kelvin - 273.15
    wind_speed = response['wind']['speed']
    humidity = response['main']['humidity']
    description = response['weather'][0]['description']
    city_name = response['name']
    offset = dt.timedelta(seconds=response['timezone'])
    tz = dt.timezone(offset)
    sunrise = dt.datetime.fromtimestamp(response['sys']['sunrise'], tz)
    sunset = dt.datetime.fromtimestamp(response['sys']['sunset'], tz)

    sunrise_time = sunrise.strftime("%H:%M:%S")
    sunset_time = sunset.strftime("%H:%M:%S")
    return {
        "city": city_name,
        "temp": round(temp_celsius, 2),
        "feels_like": round(feel_like_celsius, 2),
        "wind": wind_speed,
        "humidity": humidity,
        "description": description,
        "sunrise": sunrise_time,
        "sunset": sunset_time
    }
