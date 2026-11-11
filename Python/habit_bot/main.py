import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher

from database import init_db
from handlers import router

TOKEN = "8581185689:AAF2HXQ7uE54THxzM-7Ma1LwDl3rV8xLChc" # Replace with your Telegram Bot Token from BotFather

async def main():
    # Initialize SQLite database asynchronously
    await init_db()
    
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    
    # Include routing logic
    dp.include_router(router)
    
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    print("🤖 Bot is starting up and listening for updates...")
    
    # Run polling loop
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped gracefully.")