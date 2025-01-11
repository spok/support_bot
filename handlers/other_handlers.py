from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from database.database import bot_db
from lexicon.lexicon import LEXICON


router = Router()


# Хэндлер обрабатывает использование меню пользователями, не являющимися админами
@router.message(Command(commands=['send', 'chats', 'workspaces', 'courses', 'admins']),
                ~F.from_user.id.in_(bot_db.get_admins_id()))
async def use_user_command(message: Message):
    await message.answer(text=LEXICON['no_access'])