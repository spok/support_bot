from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import (CallbackQuery, Message, ContentType)
from copy import deepcopy
from database.database import bot_db, escape_markdown
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


# Хэндлер для обработки входа в меню чатов
@router.message(Command(commands='send'), F.from_user.id.in_(bot_db.get_admins_id()), StateFilter(default_state))
async def message_for_add_text(message: Message, state: FSMContext):
    await message.answer(text=LEXICON['add_message_text'], reply_markup=kb.kb_cancel())
    # Переходим в состояние меню чата
    await state.set_state(FSMAddMessage.add_text)


# Хэндлер для обработки введенного сообщения с фотографией
@router.message(StateFilter(FSMAddMessage.add_text), F.from_user.id.in_(bot_db.get_admins_id()), F.photo)
async def get_message_photo(message: Message, state: FSMContext):
    # Cохраняем данные сообщения с фотографией
    await state.update_data(file=message.photo[0].file_id)
    await state.update_data(text=message.caption)
    await state.update_data(type="photo")
    await message.answer(text=LEXICON['select_workspace_for_send'],
                         reply_markup=kb.kb_select_workspace(bot_db.get_workspaces()))
    # Переходим в состояние выбора воркспейса
    await state.set_state(FSMAddMessage.add_workspace)


# Хэндлер для обработки введенного сообщения с анимацией
@router.message(StateFilter(FSMAddMessage.add_text), F.from_user.id.in_(bot_db.get_admins_id()),
                F.content_type == ContentType.ANIMATION)
async def get_message_animation(message: Message, state: FSMContext):
    # Cохраняем данные сообщения с фотографией
    await state.update_data(file=message.animation.file_id)
    await state.update_data(text=message.caption)
    await state.update_data(type="animation")
    await message.answer(text=LEXICON['select_workspace_for_send'],
                         reply_markup=kb.kb_select_workspace(bot_db.get_workspaces()))
    # Переходим в состояние выбора воркспейса
    await state.set_state(FSMAddMessage.add_workspace)


# Хэндлер для обработки введенного сообщения с текстом
@router.message(StateFilter(FSMAddMessage.add_text), F.from_user.id.in_(bot_db.get_admins_id()))
async def get_message_text(message: Message, state: FSMContext):
    # Cохраняем данные сообщения
    await state.update_data(text=message.text)
    await state.update_data(file="")
    await state.update_data(type="text")
    await message.answer(text=LEXICON['select_workspace_for_send'],
                         reply_markup=kb.kb_select_workspace(bot_db.get_workspaces()))
    # Переходим в состояние выбора воркспейса
    await state.set_state(FSMAddMessage.add_workspace)


# Хендлер для обработки нажатия кнопки отмены при запросе текста сообщения
@router.callback_query(StateFilter(FSMAddMessage.add_text),
                       F.from_user.id.in_(bot_db.get_admins_id()), F.data.in_(['cancel']))
async def cancel_message(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text=callback.message.text + " ")
    await callback.message.answer(text=LEXICON['action_canceled'])
    await state.clear()


# Хендлер для обработки нажатия на кнопку выбора воркспейса
@router.callback_query(StateFilter(FSMAddMessage.add_workspace))
async def get_message_workspace(callback: CallbackQuery, state: FSMContext):
    workspace_name = callback.data
    # Cохраняем выбранный воркспейс
    await state.update_data(workspace=workspace_name)
    await callback.message.delete()
    if workspace_name != "cancel":
        new_text = LEXICON['selected_workspace']
        if workspace_name == "any":
            new_text += f'*Любой*'
        else:
            new_text += f'*{escape_markdown(workspace_name)}*'
        await callback.message.answer(text=new_text, parse_mode='MarkdownV2')
        await callback.message.answer(text=LEXICON['select_course_for_send'], reply_markup=kb.kb_select_course(bot_db.courses))
        # Переходим в состояние выбора курса
        await state.set_state(FSMAddMessage.add_course)
    else:
        # Выходим из состояния
        await callback.message.answer(text=LEXICON['cancel_other'])
        await state.clear()


# Хэндлер для обработки ввода сообщения при выборе воркспейса
@router.message(StateFilter(FSMAddMessage.add_workspace), F.from_user.id.in_(bot_db.get_admins_id()))
async def get_text_in_select_workspace(message: Message, state: FSMContext):
    await message.answer(text=LEXICON['message_in_workspace'])
    await state.set_state(FSMAddMessage.add_workspace)


# Хендлер для обработки нажатия на кнопку выбора учебного курса
@router.callback_query(StateFilter(FSMAddMessage.add_course))
async def get_message_course(callback: CallbackQuery, state: FSMContext):
    course_index: str = callback.data
    # Cохраняем выбранный воркспейс
    course_name: str = ""
    if course_index.startswith("course"):
        course_name = bot_db.get_course_name(course_index)
    else:
        course_name = course_index
    await state.update_data(course=course_name)
    await callback.message.delete()
    if course_name != "cancel":
        new_text = LEXICON['selected_course']
        if course_name == "any":
            new_text += f'*Любой*'
        else:
            new_text += f'*{escape_markdown(course_name)}*'
        await callback.message.answer(text=new_text, parse_mode='MarkdownV2')
        # Выводим сообщение с кнопками отфильтрованных чатов
        data = await state.get_data()
        workspace: str = data.get("workspace")
        group: str = data.get("group")
        markup = kb.kb_select_chat(bot_db.get_filter_chats(workspace=workspace, group=group, course=course_name))
        await callback.message.answer(text=LEXICON['select_chats_for_send'], reply_markup=markup)
        # Переходим в состояние выбора курса
        await state.set_state(FSMAddMessage.add_chats)
    else:
        # Выходим из состояния
        await callback.message.answer(text=LEXICON['cancel_other'])
        await state.clear()


# Хендлер для обработки нажатий кнопок с выбором чата
@router.callback_query(StateFilter(FSMAddMessage.add_chats),
                       ~F.data.in_(['any', 'cancel', 'confirm_select', 'reset_select']))
async def select_one_course(callback: CallbackQuery, state: FSMContext):
    chat_id: int = int(callback.data)
    # Сохраняем идентификатор чата в состоянии
    data = await state.get_data()
    workspace: str = data.get("workspace")
    group: str = data.get("group")
    course: str = data.get("course")
    chats_id: list[int] = []
    if data.get("chats_id") is None:
        chats_id: list[int] = []
    else:
        chats_id.extend(data.get("chats_id"))
    chats_id.append(chat_id)
    # Cохраняем измененный кортеж с идентификаторами
    await state.update_data(chats_id=chats_id)
    # Добавляем в сообщение названия выбранных чатов
    new_text = escape_markdown(LEXICON['select_chats_for_send']) + "\n"
    new_text += escape_markdown(LEXICON['selected_chats_for_send'])
    non_select_chats = bot_db.get_filter_chats(workspace=workspace, group=group, course=course)
    index_chat = 1
    for id in chats_id:
        new_text += escape_markdown(f'{index_chat}. ') + f'*{escape_markdown(bot_db.get_chat_name(id))}*\n'
        del non_select_chats[id]
        index_chat += 1
    markup = kb.kb_select_chat(non_select_chats)
    await callback.message.edit_text(text=escape_markdown(new_text), reply_markup=markup, parse_mode='MarkdownV2')
    # Переходим в состояние выбора курса
    await state.set_state(FSMAddMessage.add_chats)


# Хендлер для обработки нажатий кнопки для выбора всех чатов


# Хендлер для обработки нажатия кнопки подтверждения выбора


# Хендлер для обработки нажатия кнопки сброса выбора


# Хендлер для обработки нажатия кнопки отмены
