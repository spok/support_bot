from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import (CallbackQuery, Message, ReplyKeyboardRemove)
from database.database import bot_db, escape_markdown
from lexicon.lexicon import LEXICON
import keyboards.keyboards as kb


router = Router()

# Класс состояний для настройки администраторов
class FSMAddAdmin(StatesGroup):
    select_action = State()         # Состояние ожидания выбора действия
    add_id = State()                # Состояние ожидания ввода идентификатора администратора
    add_name = State()              # Состояние ожидания ввода названия администратора
    del_admin = State()             # Состояние ожидания выбора администратора для удаления


# ==========================================================
# ======== Хендлеры для работы с администраторами ==========
# ==========================================================

# Хэндлер для обработки входа в меню чатов
@router.message(Command(commands='admins'), F.from_user.id.in_(bot_db.get_admins_id()), StateFilter(default_state))
async def menu_admins(message: Message, state: FSMContext):
    await message.answer(text=LEXICON['select_action_admins'], reply_markup=kb.kb_menu_admin())
    # Переходим в состояние меню чата
    await state.set_state(FSMAddAdmin.select_action)


# Хендлер для обработки выбора добавления администратора
@router.callback_query(StateFilter(FSMAddAdmin.select_action), F.from_user.id.in_(bot_db.get_admins_id()),
                F.data.in_(['add_admin']))
async def get_admin_id(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(text=LEXICON['input_id_admin'], reply_markup=kb.kb_cancel())
    # Устанавливаем состояние ожидания ввода идентификатора чата
    await state.set_state(FSMAddAdmin.add_id)


# Хэндлер для обработки введенного идентификатора
@router.message(StateFilter(FSMAddAdmin.add_id), F.from_user.id.in_(bot_db.get_admins_id()), F.text.isdigit())
async def get_id_admin(message: Message, state: FSMContext):
    # Cохраняем введенный идентификатор
    await state.update_data(id=int(message.text))
    # Отправляем сообщение для ввода названия админа
    await message.answer(text=LEXICON['input_name_admin'], reply_markup=kb.kb_cancel())
    # Переходим в состояние ввода названия админа
    await state.set_state(FSMAddAdmin.add_name)


# Хэндлер для обработки введенного названия админа
@router.message(StateFilter(FSMAddAdmin.add_name), F.from_user.id.in_(bot_db.get_admins_id()))
async def get_name_admin(message: Message, state: FSMContext):
    # Cохраняем введенное название админа
    await state.update_data(name=message.text)
    # Сохраняем админа в базе данных
    data = await state.get_data()
    id_admin = data.get("id")
    name_admin = data.get("name")
    bot_db.add_admin(id=id_admin, name=name_admin)
    # Отправляем сообщение подтверждающее добавление админа
    new_text = LEXICON['add_admin_message'] + f'*{name_admin}*, _id: {id_admin}_'
    await message.answer(text=new_text, parse_mode='MarkdownV2')
    # Очищаем данные и выходим из состояния
    await state.clear()


# Хендлер для обработки удаления администратора
@router.callback_query(StateFilter(FSMAddAdmin.select_action), F.from_user.id.in_(bot_db.get_admins_id()),
                F.data.in_(['del_admin']))
async def select_del_admin(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    markup = kb.kb_delete_admin(bot_db.admins)
    await callback.message.answer(text=LEXICON['select_del_admin_message'], reply_markup=markup)
    # Устанавливаем состояние ожидания ввода идентификатора чата
    await state.set_state(FSMAddAdmin.del_admin)


# Хендлер для удаления администратора
@router.callback_query(StateFilter(FSMAddAdmin.del_admin), F.from_user.id.in_(bot_db.get_admins_id()))
async def del_admin(callback: CallbackQuery, state: FSMContext):
    admin_name = callback.data
    await callback.message.delete()
    if admin_name != "cancel":
        # Обработка удаления админа
        del_name = bot_db.del_admin(admin_name)
        new_text = LEXICON['del_admin_message'] + f'*{escape_markdown(del_name)}*'
        await callback.message.answer(text=new_text, parse_mode='MarkdownV2')
    # Выходим из состояния
    await state.clear()


# Хендлер для обработки нажатия кнопки отмены в меню администратора
@router.callback_query(StateFilter(FSMAddAdmin.select_action),
                       F.from_user.id.in_(bot_db.get_admins_id()), F.data.in_(['cancel']))
async def cancel_admin_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()


# Хендлер для обработки нажатия кнопки отмены при вводе данных админа
@router.callback_query(StateFilter(FSMAddAdmin.add_id, FSMAddAdmin.add_name),
                       F.from_user.id.in_(bot_db.get_admins_id()), F.data.in_(['cancel']))
async def cancel_other(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=callback.message.text + " ")
    await callback.message.answer(text=LEXICON['cancel_del_admin'])
    await state.clear()


# Хэндлер для обработки ввода текста при активном меню администраторов
@router.message(StateFilter(FSMAddAdmin.select_action), F.from_user.id.in_(bot_db.get_admins_id()))
async def menu_admins(message: Message, state: FSMContext):
    await message.answer(text=LEXICON['wrong_message_menu'])
    # Переходим в состояние меню чата
    await state.set_state(FSMAddAdmin.select_action)
