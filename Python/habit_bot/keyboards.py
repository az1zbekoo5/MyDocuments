from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Dashboard & Stats", callback_data="menu_dashboard")],
        [InlineKeyboardButton(text="📝 Manage Tasks", callback_data="menu_tasks"),
         InlineKeyboardButton(text="🎯 Manage Habits", callback_data="menu_habits")],
        [InlineKeyboardButton(text="⚙️ Settings (Timezone)", callback_data="menu_settings")]
    ])

def get_tasks_keyboard(tasks) -> InlineKeyboardMarkup:
    keyboard = []
    for t in tasks:
        status = "☑️" if t.is_completed else "◻️"
        keyboard.append([
            InlineKeyboardButton(text=f"{status} {t.title}", callback_data=f"toggle_task_{t.id}"),
            InlineKeyboardButton(text="🗑️", callback_data=f"del_task_{t.id}")
        ])
    keyboard.append([InlineKeyboardButton(text="➕ Add Task", callback_data="add_task_prompt")])
    keyboard.append([InlineKeyboardButton(text="🔙 Back to Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_habits_keyboard(habits, today_logs) -> InlineKeyboardMarkup:
    log_map = {log.habit_id: log for log in today_logs}
    keyboard = []
    for h in habits:
        log = log_map.get(h.id)
        progress = log.current_progress if log else 0
        achieved = log.is_achieved if log else False
        
        status = "🟩" if achieved else "🟧"
        keyboard.append([
            InlineKeyboardButton(text=f"{status} {h.title} ({progress}/{h.target_value})", callback_data=f"habit_prog_{h.id}"),
            InlineKeyboardButton(text="🗑️", callback_data=f"del_habit_{h.id}")
        ])
    keyboard.append([InlineKeyboardButton(text="➕ Add Habit", callback_data="add_habit_prompt")])
    keyboard.append([InlineKeyboardButton(text="🔙 Back to Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)