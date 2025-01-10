from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
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


# Класс состояний для добавления чатов
class FSMAddChats(StatesGroup):
    select_action = State()         # Состояние ожидания выбора действия
    add_id = State()                # Состояние ожидания ввода идентификатора чата
    add_name = State()              # Состояние ожидания ввода названия чата
    select_workspace = State()      # Состояние ожидания выбора воркспейса
    select_course = State()         # Состояние ожидания выбора учебного курса
    del_chat = State()              # Состояние ожидания выбора чата для удаления


# Класс состояний для добавления воркспейсов
class FSMAddWorkspace(StatesGroup):
    select_action = State()         # Состояние ожидания выбора действия
    add_name = State()              # Состояние ожидания ввода названия воркспейса
    del_workspace = State()         # Состояние ожидания выбора воркспейса для удаления


# Класс состояний для добавления учебного курса
class FSMAddCourse(StatesGroup):
    select_action = State()         # Состояние ожидания выбора действия
    add_name = State()              # Состояние ожидания ввода названия курса
    del_course = State()         # Состояние ожидания выбора курса для удаления


# Класс состояний для настройки администраторов
class FSMAddAdmin(StatesGroup):
    select_action = State()         # Состояние ожидания выбора действия
    add_id = State()                # Состояние ожидания ввода идентификатора администратора
    add_name = State()              # Состояние ожидания ввода названия администратора
    del_admin = State()             # Состояние ожидания выбора администратора для удаления


# Хэндлер обрабатывает использование меню пользователями, не являющимися админами
@router.message(Command(commands=['send', 'chats', 'workspaces', 'courses', 'admins']),
                ~F.from_user.id.in_(bot_db.get_admins_id()))
async def use_user_command(message: Message):
    await message.answer(text=LEXICON['no_access'])


# ================================================
# ======== Хендлеры для работы с чатами ==========
# ================================================


# Хэндлер для обработки входа в меню чатов
@router.message(Command(commands='chats'), F.from_user.id.in_(bot_db.get_admins_id()), StateFilter(default_state))
async def menu_chats(message: Message, state: FSMContext):
    await message.answer(text=LEXICON['select_action'], reply_markup=kb.kb_menu_chat())
    # Переходим в состояние меню чата
    await state.set_state(FSMAddChats.select_action)


# Хендлер для обработки выбора добавления чата
@router.callback_query(StateFilter(FSMAddChats.select_action), F.from_user.id.in_(bot_db.get_admins_id()),
                F.data.in_(['add_chat']))
async def chat_message_id(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(text=LEXICON['input_id'], reply_markup=kb.kb_cancel())
    # Устанавливаем состояние ожидания ввода идентификатора чата
    await state.set_state(FSMAddChats.add_id)


# Хэндлер для обработки введенного идентификатора чата
@router.message(StateFilter(FSMAddChats.add_id), F.from_user.id.in_(bot_db.get_admins_id()), F.text.isdigit())
async def menu_chats(message: Message, state: FSMContext):
    # Cохраняем введенный идентификатор по ключу "id"
    await state.update_data(id=int(message.text))
    await message.answer(text=LEXICON['input_name'], reply_markup=kb.kb_cancel())
    # Переходим в состояние ввода названия чата
    await state.set_state(FSMAddChats.add_name)


# Хэндлер для обработки введенного названия чата
@router.message(StateFilter(FSMAddChats.add_name), F.from_user.id.in_(bot_db.get_admins_id()))
async def menu_chats(message: Message, state: FSMContext):
    # Cохраняем введенный названия по ключу "name"
    await state.update_data(name=message.text)
    markup = kb.kb_select_workspace(bot_db.get_workspaces())
    await message.answer(text=LEXICON['select_workspace'], reply_markup=markup)
    # Переходим в состояние выбора воркспейса
    await state.set_state(FSMAddChats.select_workspace)



# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text=LEXICON['action_canceled']
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


# =================================================
# ======== Хендлеры для работы с курсами ==========
# =================================================

# Хэндлер для обработки входа в меню управления курсами
@router.message(Command(commands='courses'), F.from_user.id.in_(bot_db.get_admins_id()), StateFilter(default_state))
async def menu_course(message: Message, state: FSMContext):
    await message.answer(text=LEXICON['select_action_course'], reply_markup=kb.kb_menu_course())
    # Переходим в состояние меню чата
    await state.set_state(FSMAddCourse.select_action)


# Хендлер для обработки выбора добавления курса
@router.callback_query(StateFilter(FSMAddCourse.select_action), F.from_user.id.in_(bot_db.get_admins_id()),
                F.data.in_(['add_course']))
async def get_course_name(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(text=LEXICON['input_course_name'], reply_markup=kb.kb_cancel())
    # Устанавливаем состояние ожидания ввода названия курса
    await state.set_state(FSMAddCourse.add_name)


# Хэндлер для обработки введенного названия админа
@router.message(StateFilter(FSMAddCourse.add_name), F.from_user.id.in_(bot_db.get_admins_id()))
async def add_course(message: Message, state: FSMContext):
    # Cохраняем введенное название курса
    name_course = message.text
    # Сохраняем курс в базе данных
    if bot_db.check_course(name_course):
        new_text = LEXICON['course_exists']
    else:
        new_text = LEXICON['add_course_message'] + f'*{name_course}*'
        bot_db.add_course(name=name_course)
    # Отправляем сообщение подтверждающее добавление админа
    await message.answer(text=new_text, parse_mode='MarkdownV2')
    # Очищаем данные и выходим из состояния
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
@router.callback_query(StateFilter(FSMAddCourse.del_course), F.from_user.id.in_(bot_db.get_admins_id()))
async def del_course(callback: CallbackQuery, state: FSMContext):
    course_name = callback.data
    await callback.message.delete()
    if course_name != "cancel":
        # Обработка удаления курса
        bot_db.del_course(course_name)
        new_text = LEXICON['del_course_message'] + f'*{course_name}*'
        await callback.message.answer(text=new_text, parse_mode='MarkdownV2')
    # Выходим из состояния
    await state.clear()

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
    markup = kb.kb_delete_admin(bot_db.get_admins_name())
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
        bot_db.del_admin(admin_name)
        new_text = LEXICON['del_admin_message'] + f'*{admin_name}*'
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
async def cancel_admin_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=callback.message.text + " ")

    #await callback.message.delete()
    await callback.message.answer(text='Добавление администратора отменено.')
    await state.clear()