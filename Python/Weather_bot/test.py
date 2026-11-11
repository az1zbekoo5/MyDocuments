import requests
import datetime as dt

BASE_URL = 'http://api.openweathermap.org/data/2.5/'
WEATHER_API = "81ecc4ad2ba7b1cd3a232363a6b3057b"

# GET DATA
def get_info(city: str):
    url = f"{BASE_URL}weather?appid={WEATHER_API}&q={city}"

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


city = input("Enter city name: ")
data = get_info(city)

print(
    f"🌤 {data['city']}\n\n"
    f"🌡 Temperature: {data['temp']}°C\n"
    f"🤔 Feels like: {data['feels_like']}°C\n"
    f"🌥 Condition: {data['description']}\n"
    f"💨 Wind: {data['wind']} m/s\n"
    f"💧 Humidity: {data['humidity']}%\n\n"
    f"🌅 Sunrise: {data['sunrise']}\n"
    f"🌇 Sunset: {data['sunset']}"
)

# url = f"{BASE_URL}forecast?q={city}&appid={WEATHER_API}"
# response = requests.get(url).json()

# time = response['list'][0]['dt_txt']
# dt_txt = response['list'][0]['main']['temp']
# dt_xtx = dt_txt - 273.15

# print(
#     f"Date: {time}\n"
#     f"🌡 Temperature: {dt_xtx:.2f}"
# )

