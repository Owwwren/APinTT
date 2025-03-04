from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import UserDataManager


user_manager = UserDataManager('users.json', False)

def get_main_keyboard():
    """Клавиатура для выбора режима (видео или пост)."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📹 Загрузить видео", callback_data="regime_video")],
        [InlineKeyboardButton(text="📄 Загрузить пост", callback_data="regime_post")]
    ])
    return keyboard

def back_inlinekb(soft=False):
    """Клавиатура для ввода username канала."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"back.{soft}")]
    ])
    return keyboard

def get_stop_keyboard():
    """Клавиатура для остановки прослушивания."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⛔ Остановить", callback_data="stop_listening")]
    ])
    return keyboard

def delete_soft_inlinekb(user_id, soft):
    """Клавиатура для удаления программы."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data=f"delete_soft.{soft}"),
        InlineKeyboardButton(text="Нет", callback_data=f"back.{soft}")]
    ])
    return keyboard




def start_inlinekb(user_id):   
    """Клавиатура для выбора программы"""
    # Получаем список программ пользователя
    user_softs = user_manager.get_user_data(user_id, 'soft')

    if user_softs:
        
        keyboard_buttons = []
        
        # Добавляем кнопку "Создать программу" отдельно
        keyboard_buttons.append([InlineKeyboardButton(text="Создать программу", callback_data="create_soft")])

        # Итерация по программам пользователя, создание кнопок и группировка их по 2 в ряд
        row = []
        for i, soft in enumerate(user_softs):
            row.append(InlineKeyboardButton(text=soft, callback_data=f"soft.{soft}"))
            # Если ряд заполнен двумя кнопками, добавляем его в клавиатуру и начинаем новый ряд
            if len(row) == 2:
                keyboard_buttons.append(row)
                row = []

        # Если есть оставшиеся кнопки после цикла, добавляем их в последний ряд
        if row:
            keyboard_buttons.append(row)

        # Создаем клавиатуру
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Создать программу", callback_data="create_soft")]
        ])
    return keyboard


def soft_inlinekb(user_id, soft):
    """Клавиатура софта"""
    button = [
        [InlineKeyboardButton(text="📥Загрузка", callback_data=f"settings_soft.{soft}.loading_mode"),
        InlineKeyboardButton(text="Что загружать🔍", callback_data=f"settings_soft.{soft}.content"),
        InlineKeyboardButton(text="Выгрузка📤", callback_data=f"settings_soft.{soft}.unloading_mode")],
        [InlineKeyboardButton(text="🔗Источники", callback_data=f"settings_soft.{soft}.targets"),
        InlineKeyboardButton(text="⚙️Доп. функции", callback_data=f"settings_soft.{soft}.additional_functions")],
        [InlineKeyboardButton(text="🗑Удалить", callback_data=f"settings_soft.{soft}.delete"),
        InlineKeyboardButton(text="🔄Сменить", callback_data=f"back.{soft}")]  
    ]
    
    if user_manager.get_user_data(user_id, 'soft')[f"{soft}"]["state"] == 'start':
        button.append([InlineKeyboardButton(text="Стоп", callback_data=f"settings_soft.{soft}.stop")])
    if user_manager.get_user_data(user_id, 'soft')[f"{soft}"]["state"] == 'stop':
        button.append([InlineKeyboardButton(text="Старт", callback_data=f"settings_soft.{soft}.start")])
        
    keyboard = InlineKeyboardMarkup(inline_keyboard=button)
    return keyboard


def loading_mode_inlinekb(user_id, soft):
    """Клавиатура для выбора режима загрузки (1 раз или постоянно)."""
    button = []
    loading_mode = user_manager.get_user_data(user_id, 'soft')[f"{soft}"]["loading_mode"]
    if loading_mode == "None":
        button.append([InlineKeyboardButton(text="1 раз", callback_data=f"loading_mode.{soft}.once"),
                       InlineKeyboardButton(text="Постоянно", callback_data=f"loading_mode.{soft}.continuous")])
    if loading_mode == "once":
        button.append([InlineKeyboardButton(text="1 раз ✅", callback_data=f"loading_mode.{soft}.once"),
                       InlineKeyboardButton(text="Постоянно", callback_data=f"loading_mode.{soft}.continuous")])
    if loading_mode == "continuous":
        button.append([InlineKeyboardButton(text="1 раз", callback_data=f"loading_mode.{soft}.once"),
                       InlineKeyboardButton(text="Постоянно ✅", callback_data=f"loading_mode.{soft}.continuous")])
        
    button.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"back.{soft}")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=button)
    return keyboard

def unloading_mode_inlinekb(user_id, soft):
    """Клавиатура для выбора режима выгрузки (лс бота, сервер, Tik-Tok, YouTube, instagram, vk)."""
    unloading_mode = user_manager.get_user_data(user_id, 'soft')[f"{soft}"]["unloading_mode"]
    if unloading_mode == "tiktok":
        tiktok = "Tik-Tok ✅"
    if unloading_mode != "tiktok":
        tiktok = "Tik-Tok"
    if unloading_mode == "youtube":
        youtube = "YouTube ✅"
    if unloading_mode != "youtube":
        youtube = "YouTube"
    if unloading_mode == "instagram":
        instagram = "Instagram ✅"
    if unloading_mode != "instagram":
        instagram = "Instagram"
    if unloading_mode == "vk":
        vk = "Vk ✅"
    if unloading_mode != "vk":
        vk = "Vk"
    if unloading_mode == "ls":
        ls = "Лс ✅"
    if unloading_mode != "ls":
        ls = "Лс"
    if unloading_mode == "server":
        server = "Сервер ✅"
    if unloading_mode != "server":
        server = "Сервер"
    if unloading_mode == "tg_chenal":
        group = "Группа ✅"
    if unloading_mode != "tg_chenal":
        group = "Группа"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{tiktok}", callback_data=f"unloading_mode.{soft}.tiktok"),
        InlineKeyboardButton(text=f"{youtube}", callback_data=f"unloading_mode.{soft}.youtube")],
        [InlineKeyboardButton(text=f"{instagram}", callback_data=f"unloading_mode.{soft}.instagram"),
        InlineKeyboardButton(text=f"{vk}", callback_data=f"unloading_mode.{soft}.vk")],
        [InlineKeyboardButton(text=f"{ls}", callback_data=f"unloading_mode.{soft}.ls"),
        InlineKeyboardButton(text=f"{server}", callback_data=f"unloading_mode.{soft}.server")],
        [InlineKeyboardButton(text=f"{group}", callback_data=f"unloading_mode.{soft}.tg_chenal")],
        [InlineKeyboardButton(text=f"🔙 Назад", callback_data=f"back.{soft}")]
    ])
    return keyboard

def targets_mode_inlinekb(user_id, soft):
    """Клавиатура для выбора источника."""
    row = []
    target_unloading = user_manager.get_user_data(user_id, 'soft')[f"{soft}"]["target_unloading"]
    target_loading = user_manager.get_user_data(user_id, 'soft')[f"{soft}"]["target_loading"]
    unloading_mode = user_manager.get_user_data(user_id, 'soft')[f"{soft}"]["unloading_mode"]
    if target_loading != "None":
        row.append(InlineKeyboardButton(text="Загрузка ✅", callback_data=f"targets_mode.{soft}.target_loading"))
    if target_loading == "None":
        row.append(InlineKeyboardButton(text="Загрузка", callback_data=f"targets_mode.{soft}.target_loading"))
    if target_unloading != "None" and unloading_mode != "ls" and unloading_mode != "server":
        row.append(InlineKeyboardButton(text="Выгрузка ✅", callback_data=f"targets_mode.{soft}.target_unloading"))
    if target_unloading == "None" and unloading_mode != "ls" and unloading_mode != "server":
        row.append(InlineKeyboardButton(text="Выгрузка", callback_data=f"targets_mode.{soft}.target_unloading"))

    button = [row]
    button.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"back.{soft}")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=button)
    return keyboard


def content_mode_inlinekb(user_id, soft):
    """Клавиатура контента загрузки"""
    button = []
    content = user_manager.get_user_data(user_id, 'soft')[f"{soft}"]["content"]
    if content == "None":
        button.append([InlineKeyboardButton(text="Видео", callback_data=f"content_mode.{soft}.video"),
                       InlineKeyboardButton(text="Пост", callback_data=f"content_mode.{soft}.post")])
    if content == "video":
        button.append([InlineKeyboardButton(text="Видео ✅", callback_data=f"content_mode.{soft}.video"),
                       InlineKeyboardButton(text="Пост", callback_data=f"content_mode.{soft}.post")])
    if content == "post":
        button.append([InlineKeyboardButton(text="Видео", callback_data=f"content_mode.{soft}.video"),
                       InlineKeyboardButton(text="Пост ✅", callback_data=f"content_mode.{soft}.post")])
        
    button.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"back.{soft}")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=button)
    return keyboard


def additional_functions_inlinekb(user_id, soft):
    """Клавиатура контента загрузки"""
    button = []
    report = user_manager.get_user_data(user_id, 'soft')[f"{soft}"]["report"]
    ai = user_manager.get_user_data(user_id, 'soft')[f"{soft}"]["ai"]
    if report == "false" and ai == "false":
        button.append([InlineKeyboardButton(text="AI", callback_data=f"additional_functions.{soft}.ai"),
                       InlineKeyboardButton(text="Отчет", callback_data=f"additional_functions.{soft}.report")])
    if ai == "true" and report == "false":
        button.append([InlineKeyboardButton(text="AI ✅", callback_data=f"additional_functions.{soft}.ai"),
                       InlineKeyboardButton(text="Отчет", callback_data=f"additional_functions.{soft}.report")])
    if report == "true" and ai == "false":
        button.append([InlineKeyboardButton(text="AI", callback_data=f"additional_functions.{soft}.ai"),
                       InlineKeyboardButton(text="Отчет ✅", callback_data=f"additional_functions.{soft}.report")])
    if report == "true" and ai == "true":
        button.append([InlineKeyboardButton(text="AI ✅", callback_data=f"additional_functions.{soft}.ai"),
                       InlineKeyboardButton(text="Отчет ✅", callback_data=f"additional_functions.{soft}.report")])
        
    button.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"back.{soft}")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=button)
    return keyboard
