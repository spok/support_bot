from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from lexicon.lexicon import LEXICON


# Создание кнопки отмены действия
def kb_cancel_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text= LEXICON['cancel'],
        callback_data='cancel'
    )


# Создание клавиатуры для отмены действия
def kb_cancel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[kb_cancel_button()]])


#  ========= Клавиатуры для отправки рассылки =========
#  ====================================================

# Клавиатура для выбора воркспейса
def kb_select_workspace(work: set[str]) -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = []
    # Создаем объекты инлайн-кнопок
    any_workspace = InlineKeyboardButton(
        text= LEXICON['any'],
        callback_data='any'
    )
    keyboard.append([any_workspace])
    if type(work) == set and len(work) > 0:
        for w in work:
            keyboard.append([InlineKeyboardButton(
                text= w,
                callback_data= w
            )])
    keyboard.append([kb_cancel_button()])
    # Создаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Клавиатура для выбора учебного курса
def kb_select_course(courses: set[str]) -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = []
    any_courses = InlineKeyboardButton(
        text= LEXICON['any'],
        callback_data='any'
    )
    keyboard.append([any_courses])
    if len(courses) > 0:
        for course in courses:
            keyboard.append([InlineKeyboardButton(
                text= course,
                callback_data= course
            )])
    keyboard.append([kb_cancel_button()])
    # Создаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Клавиатура для выбора чатов
def kb_select_chat(chats: set[str]) -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = []
    all_select = InlineKeyboardButton(
        text= LEXICON['all_select'],
        callback_data='all_select'
    )
    keyboard.append([all_select])
    for chat in chats:
        keyboard.append([InlineKeyboardButton(
            text= '➕' + chat,
            callback_data= chat
        )])
    confirm_select = InlineKeyboardButton(
        text= LEXICON['confirm_select'],
        callback_data='confirm_select'
    )
    keyboard.append([confirm_select])
    reset_select = InlineKeyboardButton(
        text= LEXICON['reset_select'],
        callback_data='reset_select'
    )
    keyboard.append([reset_select])
    keyboard.append([kb_cancel_button()])
    # Создаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Клавиатура подтверждения отправки сообщения
def kb_confirm_send() -> InlineKeyboardMarkup:
    # Создаем объекты инлайн-кнопок
    confirm_send = InlineKeyboardButton(
        text=LEXICON['confirm_send'],
        callback_data='confirm_send'
    )
    add_chat = InlineKeyboardButton(
        text= LEXICON['add_chat'],
        callback_data='add_chat'
    )
    delete_chat = InlineKeyboardButton(
        text= LEXICON['delete_chat'],
        callback_data='delete_chat'
    )
    keyboard: list[list[InlineKeyboardButton]] = [
        [confirm_send],
        [add_chat], [delete_chat],
        [kb_cancel_button()]
    ]
    # Создаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Клавиатура для удаления выбранных чатов
def kb_delete_chat(chats: set[str]) -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = []
    for chat in chats:
        keyboard.append([InlineKeyboardButton(
            text= '➖' + chat,
            callback_data= chat
        )])
    confirm_select = InlineKeyboardButton(
        text= LEXICON['confirm_select'],
        callback_data='confirm_select'
    )
    keyboard.append([confirm_select])
    keyboard.append([kb_cancel_button()])
    # Создаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


#  ========= Клавиатуры для работы с чатами =========
#  ==================================================

# Создание клавиатуры с меню управления чатами
def kb_menu_chat() -> InlineKeyboardMarkup:
    # Создаем объекты инлайн-кнопок
    add_chat = InlineKeyboardButton(
        text= LEXICON['add_chat'],
        callback_data='add_chat'
    )
    delete_chat = InlineKeyboardButton(
        text= LEXICON['delete_chat'],
        callback_data='delete_chat'
    )
    keyboard: list[list[InlineKeyboardButton]] = [
        [add_chat], [delete_chat],
        [kb_cancel_button()]
    ]
    # Создаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Клавиатура для удаления выбранных чатов
def kb_delete_one_chat(chats: set[str]) -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = []
    for chat in chats:
        keyboard.append([InlineKeyboardButton(
            text= '➖' + chat,
            callback_data= chat
        )])
    keyboard.append([kb_cancel_button()])
    # Создаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

#  ========= Клавиатуры для работы с воркспейсам =========
#  =======================================================

# Создание клавиатуры с меню управления воркспейсами
def kb_menu_workspace() -> InlineKeyboardMarkup:
    # Создаем объекты инлайн-кнопок
    add_workspace = InlineKeyboardButton(
        text= LEXICON['add_workspace'],
        callback_data='add_workspace'
    )
    delete_workspace = InlineKeyboardButton(
        text= LEXICON['del_workspace'],
        callback_data='del_workspace'
    )
    keyboard: list[list[InlineKeyboardButton]] = [
        [add_workspace], [delete_workspace],
        [kb_cancel_button()]
    ]
    # Создаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Клавиатура для удаления выбранных воркспейсов
def kb_delete_workspace(workspaces: set[str]) -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = []
    for work in workspaces:
        keyboard.append([InlineKeyboardButton(
            text= '➖' + work,
            callback_data= work
        )])
    keyboard.append([kb_cancel_button()])
    # Создаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


#  ========= Клавиатуры для работы с курсами =========
#  =======================================================

# Создание клавиатуры с меню управления воркспейсами
def kb_menu_course() -> InlineKeyboardMarkup:
    # Создаем объекты инлайн-кнопок
    add_course = InlineKeyboardButton(
        text= LEXICON['add_course'],
        callback_data='add_course'
    )
    delete_course = InlineKeyboardButton(
        text= LEXICON['del_course'],
        callback_data='del_course'
    )
    keyboard: list[list[InlineKeyboardButton]] = [
        [add_course], [delete_course],
        [kb_cancel_button()]
    ]
    # Создаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Клавиатура для удаления выбранных воркспейсов
def kb_delete_course(courses: set[str]) -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = []
    for course in courses:
        keyboard.append([InlineKeyboardButton(
            text= '➖' + course,
            callback_data= course
        )])
    keyboard.append([kb_cancel_button()])
    # Создаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


#  ========= Клавиатуры для работы с администраторами =========
#  ============================================================

# Создание клавиатуры с меню управления администраторами
def kb_menu_admin() -> InlineKeyboardMarkup:
    # Создаем объекты инлайн-кнопок
    add_admin = InlineKeyboardButton(
        text= LEXICON['add_admin'],
        callback_data='add_admin'
    )
    del_admin = InlineKeyboardButton(
        text= LEXICON['del_admin'],
        callback_data='del_admin'
    )
    keyboard: list[list[InlineKeyboardButton]] = [
        [add_admin], [del_admin],
        [kb_cancel_button()]
    ]
    # Создаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Клавиатура для удаления выбранных воркспейсов
def kb_delete_admin(admins: set[str]) -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = []
    for admin in admins:
        keyboard.append([InlineKeyboardButton(
            text= '➖' + admin,
            callback_data= admin
        )])
    keyboard.append([kb_cancel_button()])
    # Создаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=keyboard)