from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import random

import apps.keyboards as kb

router = Router()
user_states = {}
user_calc = {}
user_settings = {}

class Reg(StatesGroup):
    name = State()
    number = State()
    location = State()

@router.message(CommandStart())
async def start(message:Message, state:FSMContext):
    await state.set_state(Reg.name)
    await message.answer('Please enter your name:')

@router.message(Reg.name)
async def state_two(message:Message, state:FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg.number)
    await message.answer('Now enter your phone number:', reply_markup= kb.keyboard_number)

@router.message(Reg.number)
async def state_three(message:Message, state:FSMContext):
    contact_data = message.contact.phone_number if message.contact else message.text
    await state.update_data(number=contact_data)
    await state.set_state(Reg.location)
    await message.answer('Last one, your loaction:', reply_markup= kb.keyboard_location)
    
@router.message(Reg.location)
async def state_four(message:Message, state:FSMContext):
    loc_data = f"{message.location.latitude}, {message.location.longitude}" if message.location else message.text
    await state.update_data(location=loc_data)
    await message.answer('Thank you registration end.\n👇 Now choose one of them:', reply_markup=await kb.reply_fruits())
    await state.clear()

@router.callback_query(F.data == '📋 Menu')
async def menu(callback:CallbackQuery):
    await callback.answer('Choosen')
    await callback.message.edit_text('Choose an action:', 
                            reply_markup=await kb.reply_menu())
    

@router.callback_query(F.data == 'weather')
async def weather(callback:CallbackQuery):
    user_states[callback.from_user.id] = 'waiting_city'
    await callback.answer('')
    await callback.message.edit_text('Enter City name:')

@router.message(F.text)
async def catch_city_name(message: Message):
    if user_states.get(message.from_user.id) != "waiting_city":
        return
    city = message.text.strip()
    user_states[message.from_user.id] = None
    await message.answer(f"Got it! Looking up weather for {city}...")


@router.callback_query(F.data == 'calculator')
async def calculator(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_calc[user_id] = "" 
    await callback.answer()
    await callback.message.reply(f'Expression: ', 
        reply_markup=await kb.reply_cal()
    )

@router.callback_query(F.data.in_(['1','2','3','4','5','6','7','8','9','+','0','=']))
async def calculator_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    value = callback.data
    await callback.answer('')
    
    expr = user_calc.get(user_id, "")

    if value == "=":
        if not expr:
            await callback.message.answer("Expression is empty!")
            return
            
        try:
            result = eval(expr)
            await callback.message.answer(f"{expr} = {result}")
        except Exception:
            await callback.message.answer("Error in expression")
        user_calc[user_id] = ""
    else:
        expr += value
        user_calc[user_id] = expr
        try:
            await callback.message.edit_text(
                f"Expression: {expr}", 
                reply_markup=await kb.reply_cal()
            )
        except Exception:
            pass


@router.callback_query(F.data == 'random')
async def random_num (callback:CallbackQuery):
    num = random.randint(0,1000)
    await callback.answer('')
    await callback.message.answer(f'Here is your random number between 0 and 1000.\nNumber: {num}')

@router.callback_query(F.data == '📊 Info')
async def info(callback:CallbackQuery):
    await callback.message.edit_text(f'Your full name: {callback.message.from_user.first_name}\nYour ID: {callback.message.from_user.id}')

@router.callback_query(F.data == '⚙️ Settings')
async def settings(callback: CallbackQuery):
    user_id = callback.from_user.id

    if user_id not in user_settings:
        user_settings[user_id] = {"notif": False, "theme": "dark"}
        
    current = user_settings[user_id]
    notif_text = "YES" if current["notif"] else "NO"
    
    await callback.answer()
    await callback.message.edit_text(
        f'Notification: {notif_text}\nTheme: {current["theme"]}', 
        reply_markup=await kb.reply_set()
    )


@router.callback_query(F.data == "toggle_notif")
async def toggle_notif(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    if user_id not in user_settings:
        user_settings[user_id] = {"notif": False, "theme": "dark"}
        
    user_settings[user_id]["notif"] = not user_settings[user_id]["notif"]
    
    current = user_settings[user_id]
    notif_text = "YES" if current["notif"] else "NO"
    
    await callback.answer(f"Notifications: {notif_text}")
    
    try:
        await callback.message.edit_text(
            f'Notification: {notif_text}\nTheme: {current["theme"]}', 
            reply_markup=await kb.reply_set()
        )
    except Exception:
        pass


@router.callback_query(F.data == "toggle_theme")
async def toggle_theme(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    if user_id not in user_settings:
        user_settings[user_id] = {"notif": False, "theme": "dark"}
        
    old_theme = user_settings[user_id]["theme"]
    new_theme = "dark" if old_theme == "light" else "light"
    user_settings[user_id]["theme"] = new_theme
    
    current = user_settings[user_id]
    notif_text = "YES" if current["notif"] else "NO"
    
    await callback.answer(f"Theme: {new_theme}")

    try:
        await callback.message.edit_text(
            f'Notification: {notif_text}\nTheme: {current["theme"]}', 
            reply_markup=await kb.reply_set()
        )
    except Exception:
        pass