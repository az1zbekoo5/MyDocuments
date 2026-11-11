from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

import apps.keyboards as kb

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    await message.answer(f'Hello {message.from_user.first_name}\nChoose any action 👇:', reply_markup= await kb.start())