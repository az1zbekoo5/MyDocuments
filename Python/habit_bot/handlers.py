from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select, delete
from datetime import date

from database import async_session_maker, User, Task, Habit, HabitLog
from keyboards import get_main_menu, get_tasks_keyboard, get_habits_keyboard

router = Router()

class Form(StatesGroup):
    setting_timezone = State()
    creating_task = State()
    creating_habit_title = State()
    creating_habit_target = State()

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    async with async_session_maker() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            user = User(telegram_id=message.from_user.id, timezone="UTC")
            session.add(user)
            await session.commit()
            
    welcome_text = (
        f"👋 **Welcome back, {message.from_user.first_name}!**\n\n"
        "Your private workspace for tracking tasks and micro-habits effectively.\n"
        "Use the rich panel below to navigate your dashboard:"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")

@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "🎛️ **Main Dashboard Hub**\nSelect a module below:",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

# --- DASHBOARD & STATS ---
@router.callback_query(F.data == "menu_dashboard")
async def cb_dashboard(callback: CallbackQuery):
    uid = callback.from_user.id
    today_str = str(date.today())
    
    async with async_session_maker() as session:
        # Fetch private records isolated by telegram_id
        tasks = (await session.scalars(select(Task).where(Task.telegram_id == uid))).all()
        habits = (await session.scalars(select(Habit).where(Habit.telegram_id == uid))).all()
        logs = (await session.scalars(select(HabitLog).where(HabitLog.telegram_id == uid, HabitLog.log_date == today_str))).all()
        
    completed_tasks = sum(1 for t in tasks if t.is_completed)
    total_tasks = len(tasks)
    
    achieved_habits = sum(1 for l in logs if l.is_achieved)
    total_habits = len(habits)
    
    dashboard_text = (
        f"📊 **Daily Progress Dashboard** (`{today_str}`)\n\n"
        f"📌 **Tasks Status:** `{completed_tasks}/{total_tasks}` completed\n"
        f"📈 **Habits Streak Score:** `{achieved_habits}/{total_habits}` reached today\n\n"
        "_Consistency is key to compounding improvements!_"
    )
    await callback.message.edit_text(dashboard_text, reply_markup=get_main_menu(), parse_mode="Markdown")

# --- TASK MANAGEMENT ---
@router.callback_query(F.data == "menu_tasks")
async def cb_menu_tasks(callback: CallbackQuery):
    uid = callback.from_user.id
    async with async_session_maker() as session:
        tasks = (await session.scalars(select(Task).where(Task.telegram_id == uid))).all()
    await callback.message.edit_text("📝 **Your To-Do List:**\nTap a checkbox to check/uncheck items:", reply_markup=get_tasks_keyboard(tasks), parse_mode="Markdown")

@router.callback_query(F.data.startswith("toggle_task_"))
async def cb_toggle_task(callback: CallbackQuery):
    tid = int(callback.data.split("_")[2])
    uid = callback.from_user.id
    async with async_session_maker() as session:
        task = await session.get(Task, tid)
        if task and task.telegram_id == uid: # Security check for privacy isolation
            task.is_completed = not task.is_completed
            await session.commit()
        tasks = (await session.scalars(select(Task).where(Task.telegram_id == uid))).all()
    await callback.message.edit_reply_markup(reply_markup=get_tasks_keyboard(tasks))

@router.callback_query(F.data.startswith("del_task_"))
async def cb_delete_task(callback: CallbackQuery):
    tid = int(callback.data.split("_")[2])
    uid = callback.from_user.id
    async with async_session_maker() as session:
        task = await session.get(Task, tid)
        if task and task.telegram_id == uid:
            await session.delete(task)
            await session.commit()
        tasks = (await session.scalars(select(Task).where(Task.telegram_id == uid))).all()
    await callback.message.edit_reply_markup(reply_markup=get_tasks_keyboard(tasks))

@router.callback_query(F.data == "add_task_prompt")
async def cb_add_task_prompt(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.creating_task)
    await callback.message.answer("✍️ Send me the title/description for your new task:")

@router.message(Form.creating_task)
async def process_task_creation(message: Message, state: FSMContext):
    uid = message.from_user.id
    async with async_session_maker() as session:
        new_task = Task(telegram_id=uid, title=message.text, is_completed=False)
        session.add(new_task)
        await session.commit()
        tasks = (await session.scalars(select(Task).where(Task.telegram_id == uid))).all()
        
    await state.clear()
    await message.answer("✅ **Task created successfully!**", reply_markup=get_tasks_keyboard(tasks), parse_mode="Markdown")

# --- HABIT MANAGEMENT ---
@router.callback_query(F.data == "menu_habits")
async def cb_menu_habits(callback: CallbackQuery):
    uid = callback.from_user.id
    today_str = str(date.today())
    async with async_session_maker() as session:
        habits = (await session.scalars(select(Habit).where(Habit.telegram_id == uid))).all()
        logs = (await session.scalars(select(HabitLog).where(HabitLog.telegram_id == uid, HabitLog.log_date == today_str))).all()
    await callback.message.edit_text("🎯 **Your Active Habits:**\nClick to record progress increment:", reply_markup=get_habits_keyboard(habits, logs), parse_mode="Markdown")

@router.callback_query(F.data.startswith("habit_prog_"))
async def cb_habit_progress(callback: CallbackQuery):
    hid = int(callback.data.split("_")[2])
    uid = callback.from_user.id
    today_str = str(date.today())
    
    async with async_session_maker() as session:
        habit = await session.get(Habit, hid)
        if not habit or habit.telegram_id != uid:
            return
            
        # Find or create today's log record
        log = await session.scalar(
            select(HabitLog).where(HabitLog.habit_id == hid, HabitLog.log_date == today_str)
        )
        if not log:
            log = HabitLog(habit_id=hid, telegram_id=uid, log_date=today_str, current_progress=0, is_achieved=False)
            session.add(log)
            
        log.current_progress += 1
        if log.current_progress >= habit.target_value:
            log.is_achieved = True
        await session.commit()
        
        habits = (await session.scalars(select(Habit).where(Habit.telegram_id == uid))).all()
        logs = (await session.scalars(select(HabitLog).where(HabitLog.telegram_id == uid, HabitLog.log_date == today_str))).all()
        
    await callback.message.edit_reply_markup(reply_markup=get_habits_keyboard(habits, logs))

@router.callback_query(F.data.startswith("del_habit_"))
async def cb_delete_habit(callback: CallbackQuery):
    hid = int(callback.data.split("_")[2])
    uid = callback.from_user.id
    today_str = str(date.today())
    async with async_session_maker() as session:
        habit = await session.get(Habit, hid)
        if habit and habit.telegram_id == uid:
            await session.delete(habit)
            await session.commit()
        habits = (await session.scalars(select(Habit).where(Habit.telegram_id == uid))).all()
        logs = (await session.scalars(select(HabitLog).where(HabitLog.telegram_id == uid, HabitLog.log_date == today_str))).all()
    await callback.message.edit_reply_markup(reply_markup=get_habits_keyboard(habits, logs))

@router.callback_query(F.data == "add_habit_prompt")
async def cb_add_habit_prompt(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.creating_habit_title)
    await callback.message.answer("🎯 Enter the name of your habit (e.g., *Drink Water*, *Read Pages*):", parse_mode="Markdown")

@router.message(Form.creating_habit_title)
async def process_habit_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(Form.creating_habit_target)
    await message.answer("🔢 Enter the measurable target value for this habit daily (numeric format, e.g., `2` or `10`):", parse_mode="Markdown")

@router.message(Form.creating_habit_target)
async def process_habit_target(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("⚠️ Please enter a valid number for your target.")
        return
        
    data = await state.get_data()
    uid = message.from_user.id
    
    async with async_session_maker() as session:
        new_habit = Habit(telegram_id=uid, title=data["title"], target_value=int(message.text))
        session.add(new_habit)
        await session.commit()
        habits = (await session.scalars(select(Habit).where(Habit.telegram_id == uid))).all()
        logs = (await session.scalars(select(HabitLog).where(HabitLog.telegram_id == uid, HabitLog.log_date == str(date.today())))).all()
        
    await state.clear()
    await message.answer("✅ **Habit successfully scheduled!**", reply_markup=get_habits_keyboard(habits, logs), parse_mode="Markdown")

# --- SETTINGS / TIMEZONE ---
@router.callback_query(F.data == "menu_settings")
async def cb_settings(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.setting_timezone)
    async with async_session_maker() as session:
        user = await session.get(User, callback.from_user.id)
        tz = user.timezone if user else "UTC"
    
    await callback.message.edit_text(
        f"⚙️ **User Settings**\nCurrent Timezone: `{tz}`\n\n"
        "Please type your correct Timezone string (e.g., `UTC`, `America/New_York`, `Europe/London`, `Asia/Tashkent`):",
        parse_mode="Markdown"
    )

@router.message(Form.setting_timezone)
async def process_timezone(message: Message, state: FSMContext):
    uid = message.from_user.id
    new_tz = message.text.strip()
    async with async_session_maker() as session:
        user = await session.get(User, uid)
        if user:
            user.timezone = new_tz
            await session.commit()
    await state.clear()
    await message.answer(f"✅ Timezone updated successfully to `{new_tz}`!", reply_markup=get_main_menu(), parse_mode="Markdown")