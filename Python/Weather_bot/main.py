import asyncio

from aiogram import Bot, Dispatcher, html, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import requests
import datetime as dt
from config import BOT_TOKEN
from config import WEATHER_API
#from weatherApp import get_info

BOT_TOKEN = "8581185689:AAF2HXQ7uE54THxzM-7Ma1LwDl3rV8xLChc"
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather?'

dp = Dispatcher()
router = Router()
bot = Bot(token=BOT_TOKEN)
dp.include_router(router)

#----------------------------------------------------------------------------------------------------------------------------------
#    FUNCTIONS
#----------------------------------------------------------------------------------------------------------------------------------

def get_info(city: str):
    url = f"{BASE_URL}appid={WEATHER_API}&q={city}"

    response = requests.get(url).json()

    if response.get("cod") != 200:
        return None

    temp_kelvin = response['main']['temp'] # temperature in kelvin
    temp_celsius = temp_kelvin - 273.15
    feel_like_kelvin = response['main']['feels_like'] # Feels like in kelvin
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

#----------------------------------------------------------------------------------------------------------------------------------
#    COMMAND
#----------------------------------------------------------------------------------------------------------------------------------

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello {html.bold(message.from_user.full_name)}!\nSend me city name to get information about weather!")

#----------------------------

@router.message(F.text)
async def weather_handler(message: Message):
    city = message.text.strip()
    data = get_info(city)

    if not data:
        await message.answer("City not found.")
        return

    text = (
        f"🌤 {data['city']}\n\n"
        f"🌡 Temperature: {data['temp']}°C\n"
        f"🤔 Feels like: {data['feels_like']}°C\n"
        f"🌥 Condition: {data['description']}\n"
        f"💨 Wind: {data['wind']} m/s\n"
        f"💧 Humidity: {data['humidity']}%\n\n"
        f"🌅 Sunrise: {data['sunrise']}\n"
        f"🌇 Sunset: {data['sunset']}"
    )
    await message.answer(text)

#----------------------------------------------------------------------------------------------------------------------------------
#    POLLING
#----------------------------------------------------------------------------------------------------------------------------------
async def main() -> None:
    bot = Bot(
        token=BOT_TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())