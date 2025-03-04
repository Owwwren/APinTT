import os
import re
import json
import asyncio
from aiogram import Bot
from config import BOT_TOKEN
bot = Bot(token=BOT_TOKEN)

def name_correct(text):
    if text == 'once':
        text = '1 раз'
    if text == 'continuous':
        text = 'Постоянно'
        
    if text == 'tiktok':
        text = 'Tik-Tok'
    if text == 'youtube':
        text = 'YouTube'
    if text == 'instagram':
        text = 'Instagram'
    if text == 'vk':
        text = 'Vk'
    if text == 'ls':
        text = 'Лич. сообщ.'
    if text == 'tg_chenal':
        text = 'ТГ Канал'
    if text == 'server':
        text = 'Сервер'
    if text == 'video':
        
        text = 'Видео'
    if text == 'post':
        text = 'Пост'
        
    if text == 'None':
        text = 'Не задано'
    return text




def is_valid_cookie(cookie):
    # Обязательные поля в объекте куки
    required_fields = {"name", "value", "domain", "path", "expires", "httpOnly", "secure", "sameSite"}
    
    # Проверяем, есть ли все обязательные поля в объекте
    return required_fields.issubset(cookie.keys())

def validate_cookies(cookies_json):
    try:
        # Пытаемся загрузить JSON
        cookies = json.loads(cookies_json)
        
        # Проверяем, что это список
        if not isinstance(cookies, list):
            return False
        
        # Проверяем каждый объект в списке
        for cookie in cookies:
            if not is_valid_cookie(cookie):
                return False
        
        return True
    except json.JSONDecodeError:
        return False

def is_link(text):
    if validate_cookies(text):
        return True
    else:
        # Регулярное выражение для проверки ссылки
        link_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        return bool(link_pattern.search(text))


async def time_delet_message(chat_id, message_id, time):
    await asyncio.sleep(time)
    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    
    
def ensure_folder_exists(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    


class UserDataManager:
    def __init__(self, filename, debug=False):
        self.filename = filename
        self.debug = debug
        self.ensure_file_exists()

    def ensure_file_exists(self):
        """Создает файл, если его нет."""
        if not os.path.exists(self.filename):
            if self.debug:
                print(self.filename)
            with open(self.filename, 'w') as file:
                json.dump({}, file)

    def load_data(self):
        """Загружает данные из файла."""
        with open(self.filename, 'r') as file:
            if self.debug:
                print(f"Загрузка данных из файла {self.filename}")
            return json.load(file)

    def save_data(self, data):
        """Сохраняет данные в файл."""
        with open(self.filename, 'w') as file:
            if self.debug:
                print(f"Сохранение данных в файл {self.filename}\n")
            json.dump(data, file, indent=4)

    def add_or_update_user_data(self, user_id, key, value):
        """Добавляет или обновляет данные для пользователя."""
        data = self.load_data()

        # Если пользователь не существует, создаем запись для него
        if user_id not in data:
            if self.debug:
                print(f"Пользователь {user_id} добавлен")
            data[user_id] = {}

        # Обновляем или добавляем данные пользователя
        data[user_id][key] = value

        # Сохраняем обновленные данные
        if self.debug:
            print(f"Данные {data} для пользователя {user_id} добавлены.")
        self.save_data(data)

    def get_user_data(self, user_id=None, key=None):
        """Возвращает данные пользователя по ключу."""
        data = self.load_data()
        if self.debug:
            print(f"Данные {data} у пользователя {user_id} взяты.")
        if user_id == None:
            return data
        if key == None:
            return data.get(user_id, None)
        else:
            return data.get(user_id, {}).get(key, None)

    def remove_duplicates(self):
        """Удаляет дубликаты из данных."""
        data = self.load_data()

        return data


async def stop_soft(soft_json, soft, run_task, callback, user_manager):
    soft_json[f"{soft}"]["state"] = "stop"
    
    # Получаем все текущие задачи
    current_tasks = asyncio.all_tasks()
    task = run_task.get_user_data(str(callback.from_user.id), soft)
    
    # Ищем задачу по имени
    for task_name in current_tasks:
        print(f'{task_name.get_name()} | {task}')
        if task_name.get_name() == task:
            task_name.cancel()
            try:
                await task_name
            except asyncio.CancelledError: 
                
                run_task.add_or_update_user_data(str(callback.from_user.id), str(soft), 'None')
               
                user_manager.add_or_update_user_data(str(callback.from_user.id), 'soft', soft_json)
                await callback.answer(f'😔 Программа {soft} остановлена!')
                print("Прослушивание остановлено.")
                return callback