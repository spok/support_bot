from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import (CallbackQuery, Message, ReplyKeyboardRemove)
from database.database import bot_db
from lexicon.lexicon import LEXICON
import keyboards.keyboards as kb


router = Router()


# Класс состояний для добавления воркспейсов
class FSMAddWorkspace(StatesGroup):
    select_action = State()         # Состояние ожидания выбора действия
    add_name = State()              # Состояние ожидания ввода названия воркспейса
    del_workspace = State()         # Состояние ожидания выбора воркспейса для удаления


# ======================================================
# ======== Хендлеры для работы с воркспейсами ==========
# ======================================================

# Хэндлер для обработки входа в меню управления воркспейсами
@router.message(Command(commands='workspaces'), F.from_user.id.in_(bot_db.get_admins_id()), StateFilter(default_state))
async def menu_workspace(message: Message, state: FSMContext):
    await message.answer(text=LEXICON['select_action_workspace'], reply_markup=kb.kb_menu_workspace())
    # Переходим в состояние меню чата
    await state.set_state(FSMAddWorkspace.select_action)


# Хендлер для обработки нажатия кнопки отмены в меню чатов
@router.callback_query(StateFilter(FSMAddWorkspace.select_action),
                       F.from_user.id.in_(bot_db.get_admins_id()), F.data.in_(['cancel']))
async def cancel_workspace_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()


# Хэндлер для обработки ввода текста при активном меню чата
@router.message(StateFilter(FSMAddWorkspace.select_action), F.from_user.id.in_(bot_db.get_admins_id()))
async def message_menu_workspace(message: Message, state: FSMContext):
    await message.answer(text=LEXICON['wrong_message_menu'])
    # Переходим в состояние меню чата
    await state.set_state(FSMAddWorkspace.select_action)


# Хендлер для обработки выбора добавления курса
@router.callback_query(StateFilter(FSMAddWorkspace.select_action), F.from_user.id.in_(bot_db.get_admins_id()),
                F.data.in_(['add_workspace']))
async def get_workspace_name(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(text=LEXICON['input_workspace_name'], reply_markup=kb.kb_cancel())
    # Устанавливаем состояние ожидания ввода названия воркспейса
    await state.set_state(FSMAddWorkspace.add_name)


# Хэндлер для обработки введенного названия админа
@router.message(StateFilter(FSMAddWorkspace.add_name), F.from_user.id.in_(bot_db.get_admins_id()))
async def add_workspace(message: Message, state: FSMContext):
    # Cохраняем введенное название курса
    name_workspace = message.text
    # Сохраняем курс в базе данных
    if bot_db.check_workspace(name_workspace):
        new_text = LEXICON['workspace_exists']
    else:
        new_text = LEXICON['add_workspace_message'] + f'*{name_workspace}*'
        bot_db.add_workspaces(name=name_workspace)
    # Отправляем сообщение подтверждающее добавление админа
    await message.answer(text=new_text, parse_mode='MarkdownV2')
    # Очищаем данные и выходим из состояния
    await state.clear()


# Хендлер для обработки удаления воркспейса
@router.callback_query(StateFilter(FSMAddWorkspace.select_action), F.from_user.id.in_(bot_db.get_admins_id()),
                F.data.in_(['del_workspace']))
async def select_del_workspace(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    markup = kb.kb_delete_workspace(bot_db.workspaces)
    await callback.message.answer(text=LEXICON['select_del_workspace'], reply_markup=markup)
    await state.set_state(FSMAddWorkspace.del_workspace)


# Хендлер для удаления воркспейса
@router.callback_query(StateFilter(FSMAddWorkspace.del_workspace), F.from_user.id.in_(bot_db.get_admins_id()))
async def del_workspace(callback: CallbackQuery, state: FSMContext):
    workspace_name = callback.data
    await callback.message.delete()
    if workspace_name != "cancel":
        # Обработка удаления курса
        bot_db.del_workspace(workspace_name)
        new_text = LEXICON['del_workspace_message'] + f'*{workspace_name}*'
        await callback.message.answer(text=new_text, parse_mode='MarkdownV2')
    # Выходим из состояния
    await state.clear()


# Хэндлер для обработки ввода текста при активном меню курсов
@router.message(StateFilter(FSMAddWorkspace.select_action), F.from_user.id.in_(bot_db.get_admins_id()))
async def menu_workspace(message: Message, state: FSMContext):
    await message.answer(text=LEXICON['wrong_message_menu'])
    # Переходим в состояние меню чата
    await state.set_state(FSMAddWorkspace.select_action)


# Хендлер для обработки нажатия кнопки отмены при вводе данных чата
@router.callback_query(StateFilter(FSMAddWorkspace.add_name),
                       F.from_user.id.in_(bot_db.get_admins_id()), F.data.in_(['cancel']))
async def cancel_other(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text=callback.message.text + " ")
    await callback.message.answer(text=LEXICON['cancel_other'])
    await state.clear()
