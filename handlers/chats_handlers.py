from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import CallbackQuery, Message
from database.database import bot_db, escape_markdown
from lexicon.lexicon import LEXICON
import keyboards.keyboards as kb


router = Router()


# Класс состояний для добавления чатов
class FSMAddChats(StatesGroup):
    select_action = State()         # Состояние ожидания выбора действия
    add_id = State()                # Состояние ожидания ввода идентификатора чата
    add_name = State()              # Состояние ожидания ввода названия чата
    select_workspace = State()      # Состояние ожидания выбора воркспейса
    select_course = State()         # Состояние ожидания выбора учебного курса
    del_chat = State()              # Состояние ожидания выбора чата для удаления


# ================================================
# ======== Хендлеры для работы с чатами ==========
# ================================================


# Хэндлер для обработки входа в меню чатов
@router.message(Command(commands='chats'), F.from_user.id.in_(bot_db.get_admins_id()), StateFilter(default_state))
async def menu_chats(message: Message, state: FSMContext):
    await message.answer(text=LEXICON['select_action'], reply_markup=kb.kb_menu_chat())
    # Переходим в состояние меню чата
    await state.set_state(FSMAddChats.select_action)


# Хендлер для обработки нажатия кнопки отмены в меню чатов
@router.callback_query(StateFilter(FSMAddChats.select_action),
                       F.from_user.id.in_(bot_db.get_admins_id()), F.data.in_(['cancel']))
async def cancel_chats_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()


# Хэндлер для обработки ввода текста при активном меню чата
@router.message(StateFilter(FSMAddChats.select_action), F.from_user.id.in_(bot_db.get_admins_id()))
async def cancel_menu_chats(message: Message, state: FSMContext):
    await message.answer(text=LEXICON['wrong_message_menu'])
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

# Хэндлер для обработки введенного текста при открытом меню
@router.message(StateFilter(FSMAddChats.select_action), F.from_user.id.in_(bot_db.get_admins_id()))
async def message_with_menu(message: Message, state: FSMContext):
    await message.answer(text=LEXICON['message_in_menu'])
    # Переходим в состояние ввода названия чата
    await state.set_state(FSMAddChats.select_action)

# Хэндлер для обработки введенного идентификатора чата
@router.message(StateFilter(FSMAddChats.add_id), F.from_user.id.in_(bot_db.get_admins_id()), F.text.isdigit())
async def chat_add_id(message: Message, state: FSMContext):
    # Cохраняем введенный идентификатор по ключу "id"
    await state.update_data(id=int(message.text))
    await message.answer(text=LEXICON['input_name'], reply_markup=kb.kb_cancel())
    # Переходим в состояние ввода названия чата
    await state.set_state(FSMAddChats.add_name)


# Хэндлер для обработки неверного идентификатора чата
@router.message(StateFilter(FSMAddChats.add_id), F.from_user.id.in_(bot_db.get_admins_id()))
async def chat_add_id(message: Message, state: FSMContext):
    await message.answer(text=LEXICON['wrong_id'])
    await state.clear()


# Хэндлер для обработки введенного названия чата
@router.message(StateFilter(FSMAddChats.add_name), F.from_user.id.in_(bot_db.get_admins_id()))
async def chat_add_name(message: Message, state: FSMContext):
    # Cохраняем введенный названия по ключу "name"
    await state.update_data(name=message.text)
    markup = kb.kb_select_workspace(bot_db.get_workspaces())
    await message.answer(text=LEXICON['select_workspace'], reply_markup=markup)
    # Переходим в состояние выбора воркспейса
    await state.set_state(FSMAddChats.select_workspace)


# Хэндлер для обработки выбранного воркспейса и перехода к выбору курса
@router.callback_query(StateFilter(FSMAddChats.select_workspace))
async def chat_add_course(callback: CallbackQuery, state: FSMContext):
    workspace_name = callback.data
    # Cохраняем выбранный воркспейс
    await state.update_data(workspace=workspace_name)
    await callback.message.delete()
    if workspace_name != "cancel":
        new_text = LEXICON['selected_workspace']
        if workspace_name == "any":
            new_text += f'*Любой*'
        else:
            new_text += f'*{workspace_name}*'
        await callback.message.answer(text=new_text, parse_mode='MarkdownV2')
        await callback.message.answer(text=LEXICON['select_course'], reply_markup=kb.kb_select_course(bot_db.courses))
        # Переходим в состояние выбора курса
        await state.set_state(FSMAddChats.select_course)
    else:
        # Выходим из состояния
        await callback.message.answer(text=LEXICON['cancel_other'])
        await state.clear()


# Хэндлер для обработки ввода сообщения при выборе воркспейса
@router.message(StateFilter(FSMAddChats.select_workspace), F.from_user.id.in_(bot_db.get_admins_id()))
async def message_in_select_workspace(message: Message, state: FSMContext):
    await message.answer(text=LEXICON['message_in_workspace'])
    await state.set_state(FSMAddChats.select_workspace)


# Хэндлер для сохранения данных чата
@router.callback_query(StateFilter(FSMAddChats.select_course))
async def chat_save_in_db(callback: CallbackQuery, state: FSMContext):
    callback_answer = callback.data
    course_name: str = ""
    if callback_answer.startswith("course"):
        course_name = bot_db.get_course_name(callback_answer)
    else:
        course_name = callback_answer
    # Сохраняем чат в базе данных
    data = await state.get_data()
    id_chat: int = int(data.get("id"))
    name_chat: str = data.get("name")
    workspace_name: str = data.get("workspace")
    bot_db.add_chats(id=id_chat, name=name_chat, workspace=workspace_name, course=course_name)
    await callback.message.delete()
    if course_name != "cancel":
        new_text = LEXICON['selected_course']
        if course_name == "any":
            new_text += "*Любой*"
        else:
            new_text += f'*{escape_markdown(course_name)}*'
        await callback.message.answer(text=new_text, parse_mode='MarkdownV2')
        new_text = LEXICON['add_chat_message']
        new_text += f'Название  *{escape_markdown(name_chat)}*\n'
        new_text += f'ID  *{id_chat}*\n'
        new_text += f'Воркспейс  '
        if workspace_name == "any":
            new_text += f'*Любой*\n'
        else:
            new_text += f'*{escape_markdown(workspace_name)}*\n'
        new_text += f'Курс  '
        if course_name == "any":
            new_text += f'*Любой*\n'
        else:
            new_text += f'*{escape_markdown(course_name)}*\n'
        await callback.message.answer(text=new_text, parse_mode='MarkdownV2')
    else:
        await callback.message.answer(text=LEXICON['action_canceled'])
    # Выходим из состояния
    await state.clear()


# Хэндлер для обработки ввода сообщения при выборе воркспейса
@router.message(StateFilter(FSMAddChats.select_course), F.from_user.id.in_(bot_db.get_admins_id()))
async def message_in_select_course(message: Message, state: FSMContext):
    await message.answer(text=LEXICON['message_in_course'])
    await state.set_state(FSMAddChats.select_course)


# Хендлер для обработки нажатия кнопки отмены при вводе данных чата
@router.callback_query(StateFilter(FSMAddChats.add_id, FSMAddChats.add_name),
                       F.from_user.id.in_(bot_db.get_admins_id()), F.data.in_(['cancel']))
async def cancel_other(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text=callback.message.text + " ")
    await callback.message.answer(text=LEXICON['cancel_other'])
    await state.clear()


# Хендлер для обработки выбора удаления чата
@router.callback_query(StateFilter(FSMAddChats.select_action), F.from_user.id.in_(bot_db.get_admins_id()),
                F.data.in_(['delete_chat']))
async def menu_del_chat(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    await callback.message.answer(text=LEXICON['del_chat_menu'], reply_markup=kb.kb_delete_one_chat(bot_db.chats))
    await state.set_state(FSMAddChats.del_chat)


# Хендлер для удаления чата
@router.callback_query(StateFilter(FSMAddChats.del_chat), F.from_user.id.in_(bot_db.get_admins_id()))
async def del_chat(callback: CallbackQuery, state: FSMContext):
    chat_id = int(callback.data)
    await callback.message.delete()
    if chat_id != "cancel":
        # Обработка удаления чата
        chat_name = escape_markdown(bot_db.get_chat_name(chat_id))
        bot_db.del_chat(chat_id)
        new_text = LEXICON['del_chat'] + f'*{chat_name}*'
        await callback.message.answer(text=new_text, parse_mode='MarkdownV2')
    # Выходим из состояния
    await state.clear()


# Хэндлер для обработки ввода сообщения при выборе чата на удалении
@router.message(StateFilter(FSMAddChats.del_chat), F.from_user.id.in_(bot_db.get_admins_id()))
async def message_in_select_course_del(message: Message, state: FSMContext):
    await message.answer(text=LEXICON['message_in_del_course'])
    await state.set_state(FSMAddChats.del_chat)