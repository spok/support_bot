from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import CallbackQuery, Message
from database.database import bot_db, escape_markdown
from lexicon.lexicon import LEXICON
import keyboards.keyboards as kb


router = Router()


# Класс состояний для добавления учебного курса
class FSMAddGroup(StatesGroup):
    select_action = State()         # Состояние ожидания выбора действия
    add_name = State()              # Состояние ожидания ввода названия курса
    del_course = State()         # Состояние ожидания выбора курса для удаления


# =================================================
# ======== Хендлеры для работы с курсами ==========
# =================================================

# Хэндлер для обработки входа в меню управления курсами
@router.message(Command(commands='groups'), F.from_user.id.in_(bot_db.get_admins_id()), StateFilter(default_state))
async def menu_groups(message: Message, state: FSMContext):
    await message.answer(text=LEXICON['menu_group'], reply_markup=kb.kb_menu_group())
    # Переходим в состояние меню чата
    await state.set_state(FSMAddGroup.select_action)


# Хендлер для обработки нажатия кнопки отмены в меню чатов
@router.callback_query(StateFilter(FSMAddGroup.select_action),
                       F.from_user.id.in_(bot_db.get_admins_id()), F.data.in_(['cancel']))
async def cancel_course_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()


# Хэндлер для обработки ввода текста при активном меню чатов
@router.message(StateFilter(FSMAddGroup.select_action), F.from_user.id.in_(bot_db.get_admins_id()))
async def message_menu_course(message: Message, state: FSMContext):
    await message.answer(text=LEXICON['wrong_message_menu'])
    await state.set_state(FSMAddGroup.select_action)


# Хендлер для обработки выбора добавления группы
@router.callback_query(StateFilter(FSMAddGroup.select_action), F.from_user.id.in_(bot_db.get_admins_id()),
                       F.data.in_(['add_group']))
async def get_group_name(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(text=LEXICON['input_group_name'], reply_markup=kb.kb_cancel())
    await state.set_state(FSMAddGroup.add_name)


# Хэндлер для обработки введенного названия группы
@router.message(StateFilter(FSMAddGroup.add_name), F.from_user.id.in_(bot_db.get_admins_id()))
async def add_group(message: Message, state: FSMContext):
    # Cохраняем введенное название курса
    name_group = message.text
    # Сохраняем курс в базе данных
    if bot_db.check_group(name_group):
        new_text = LEXICON['group_exists']
    else:
        new_text = LEXICON['add_group_message'] + f'*{escape_markdown(name_group)}*'
        bot_db.add_group(name=name_group)
    # Отправляем сообщение подтверждающее добавление группы
    await message.answer(text=new_text, parse_mode='MarkdownV2')
    # Очищаем данные и выходим из состояния
    await state.clear()


# Хендлер для обработки нажатия кнопки отмены при запросе названия группы
@router.callback_query(StateFilter(FSMAddGroup.add_name),
                       F.from_user.id.in_(bot_db.get_admins_id()), F.data.in_(['cancel']))
async def cancel_add_group_hame(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text=callback.message.text + " ")
    await callback.message.answer(text=LEXICON['cancel_other'])
    await state.clear()


# Хендлер для обработки удаления группы
@router.callback_query(StateFilter(FSMAddGroup.select_action), F.from_user.id.in_(bot_db.get_admins_id()),
                       F.data.in_(['del_group']))
async def select_del_group(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    markup = kb.kb_delete_group(bot_db.groups)
    await callback.message.answer(text=LEXICON['select_del_course'], reply_markup=markup)
    # Устанавливаем состояние ожидания удаления группы
    await state.set_state(FSMAddGroup.del_course)


# Хендлер для удаления группы
@router.callback_query(StateFilter(FSMAddGroup.del_course), F.from_user.id.in_(bot_db.get_admins_id()),
                       F.data.startswith("group"))
async def del_group(callback: CallbackQuery, state: FSMContext):
    group_name: str = callback.data
    await callback.message.delete()
    if group_name != "cancel":
        # Обработка удаления курса
        del_name: str = bot_db.del_group(group_name)
        new_text = LEXICON['del_group_message'] + f'*{escape_markdown(del_name)}*'
        await callback.message.answer(text=new_text, parse_mode='MarkdownV2')
    # Выходим из состояния
    await state.clear()