from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                        InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

buttuns = ['📋 Menu', '📊 Info', '⚙️ Settings']

async def reply_fruits():
    keyboard = InlineKeyboardBuilder()
    for fruit in buttuns:
        keyboard.add(InlineKeyboardButton(text=fruit, callback_data=f'{fruit}'))
    return keyboard.adjust(2).as_markup()

async def reply_menu():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='🌤 Weather', callback_data='weather'),
                 InlineKeyboardButton(text='🧮 Calculator', callback_data='calculator'),
                 InlineKeyboardButton(text='🎲 Random', callback_data='random'))
    return keyboard.adjust(2).as_markup()


number = ['1','2','3','4','5','6','7','8','9','+','0','=']

async def reply_cal():
    keyboard = InlineKeyboardBuilder()
    for n in number:
        keyboard.add(InlineKeyboardButton(text=n, callback_data=f'{n}'))
    return keyboard.adjust(3).as_markup()

async def reply_set():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="🔔 Notifications", callback_data="toggle_notif"),
        InlineKeyboardButton(text="🌙 Theme", callback_data="toggle_theme"),
    )
    return keyboard.adjust(1).as_markup()

keyboard_number = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='📞 Number', request_contact=True)]], resize_keyboard=True)
keyboard_location = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='🗺️ Location', request_location=True)]], resize_keyboard=True)