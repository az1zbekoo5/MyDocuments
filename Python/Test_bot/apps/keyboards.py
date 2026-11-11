from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton,
                           ReplyKeyboardMarkup, KeyboardButton)
from aiogram.utils.keyboard import KeyboardBuilder, InlineKeyboardBuilder

start_cmd = ['Weather', 'Random', 'Calculator']
async def start():
    keyboard = InlineKeyboardBuilder()
    for s in start_cmd:
        keyboard.add(InlineKeyboardButton(text=s, callback_data=f'{start_cmd}'))
    return keyboard.adjust(2).as_markup()