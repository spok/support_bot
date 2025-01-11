from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import (CallbackQuery, Message, ReplyKeyboardRemove)
from database.database import bot_db
from lexicon.lexicon import LEXICON
import keyboards.keyboards as kb


router = Router()

# Класс состояний для отправки рассылки
class FSMAddMessage(StatesGroup):
    add_text = State()              # Состояние ожидания ввода текста сообщения
    add_workspace = State()         # Состояние ожидания ввода воркспейса
    add_course = State()            # Состояние ожидания ввода учебного курса
    add_chats = State()             # Состояние ожидания ввода чатов
    confirmation = State()          # Состояние ожидания подтверждения отправки сообщения


# Хэндлер обрабатывает использование меню пользователями, не являющимися админами
@router.message(Command(commands=['send', 'chats', 'workspaces', 'courses', 'admins']),
                ~F.from_user.id.in_(bot_db.get_admins_id()))
async def use_user_command(message: Message):
    await message.answer(text=LEXICON['no_access'])