from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import (CallbackQuery, Message, ReplyKeyboardRemove)
from database.database import bot_db, escape_markdown
from lexicon.lexicon import LEXICON
import keyboards.keyboards as kb


router = Router()


# Класс состояний для добавления учебного курса
class FSMAddCourse(StatesGroup):
    select_action = State()         # Состояние ожидания выбора действия
    add_name = State()              # Состояние ожидания ввода названия курса
    del_course = State()         # Состояние ожидания выбора курса для удаления


# =================================================
# ======== Хендлеры для работы с курсами ==========
# =================================================

# Хэндлер для обработки входа в меню управления курсами
@router.message(Command(commands='courses'), F.from_user.id.in_(bot_db.get_admins_id()), StateFilter(default_state))
async def menu_course(message: Message, state: FSMContext):
    await message.answer(text=LEXICON['select_action_course'], reply_markup=kb.kb_menu_course())
    # Переходим в состояние меню чата
    await state.set_state(FSMAddCourse.select_action)


# Хендлер для обработки нажатия кнопки отмены в меню курсов
@router.callback_query(StateFilter(FSMAddCourse.select_action),
                       F.from_user.id.in_(bot_db.get_admins_id()), F.data.in_(['cancel']))
async def cancel_course_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()


# Хэндлер для обработки ввода текста при активном меню курса
@router.message(StateFilter(FSMAddCourse.select_action), F.from_user.id.in_(bot_db.get_admins_id()))
async def message_menu_course(message: Message, state: FSMContext):
    await message.answer(text=LEXICON['wrong_message_menu'])
    await state.set_state(FSMAddCourse.select_action)


# Хендлер для обработки выбора добавления курса
@router.callback_query(StateFilter(FSMAddCourse.select_action), F.from_user.id.in_(bot_db.get_admins_id()),
                F.data.in_(['add_course']))
async def get_course_name(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(text=LEXICON['input_course_name'], reply_markup=kb.kb_cancel())
    await state.set_state(FSMAddCourse.add_name)


# Хэндлер для обработки введенного названия курса
@router.message(StateFilter(FSMAddCourse.add_name), F.from_user.id.in_(bot_db.get_admins_id()))
async def add_course(message: Message, state: FSMContext):
    # Cохраняем введенное название курса
    name_course = message.text
    # Сохраняем курс в базе данных
    if bot_db.check_course(name_course):
        new_text = LEXICON['course_exists']
    else:
        new_text = LEXICON['add_course_message'] + f'*{escape_markdown(name_course)}*'
        bot_db.add_course(name=name_course)
    # Отправляем сообщение подтверждающее добавление админа
    await message.answer(text=new_text, parse_mode='MarkdownV2')
    # Очищаем данные и выходим из состояния
    await state.clear()


# Хендлер для обработки нажатия кнопки отмены при названия курса
@router.callback_query(StateFilter(FSMAddCourse.add_name),
                       F.from_user.id.in_(bot_db.get_admins_id()), F.data.in_(['cancel']))
async def cancel_other(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text=callback.message.text + " ")
    await callback.message.answer(text=LEXICON['cancel_other'])
    await state.clear()


# Хендлер для обработки удаления курса
@router.callback_query(StateFilter(FSMAddCourse.select_action), F.from_user.id.in_(bot_db.get_admins_id()),
                F.data.in_(['del_course']))
async def select_del_course(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    markup = kb.kb_delete_course(bot_db.courses)
    await callback.message.answer(text=LEXICON['select_del_course'], reply_markup=markup)
    # Устанавливаем состояние ожидания удаления курса
    await state.set_state(FSMAddCourse.del_course)


# Хендлер для удаления администратора
@router.callback_query(StateFilter(FSMAddCourse.del_course), F.from_user.id.in_(bot_db.get_admins_id()),
                       F.data.startswith("course"))
async def del_course(callback: CallbackQuery, state: FSMContext):
    course_name: str = callback.data
    await callback.message.delete()
    if course_name != "cancel":
        # Обработка удаления курса
        del_name: str = bot_db.del_course(course_name)
        new_text = LEXICON['del_course_message'] + f'*{escape_markdown(del_name)}*'
        await callback.message.answer(text=new_text, parse_mode='MarkdownV2')
    # Выходим из состояния
    await state.clear()
