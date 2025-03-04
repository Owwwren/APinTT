from telethon.tl.types import PeerChannel, PeerChat, PeerUser, User, Channel, Chat
from telethon import TelegramClient, events, errors

from aiogram import Bot
from aiogram.types.input_file import FSInputFile
from aiogram.types import InputMediaDocument

import os
import shutil
import threading
import random
import asyncio

from config import API_ID, API_HASH, VIDEO_FOLDER, POST_FOLDER, DOWNLOAD_FOLDER, BOT_TOKEN
from ai import AI_GenerateText, link_rename
from utils import UserDataManager

# from tiktok.tiktok_video import sand_video

client_loader = TelegramClient('session_loader', API_ID, API_HASH)
client_unloader = TelegramClient('session_unloader', API_ID, API_HASH)

# Список для хранения информации о загружаемых файлах
downloads_list_new = {}
# Блокировка для синхронизации доступа к списку
downloads_lock = threading.Lock()


async def download_video(event, download_folder, post_folder):
    """Скачивает видео из поста."""
    if event.message.video:
        print("Новое видео найдено!")
        
        if not os.path.exists(f'{download_folder}/{post_folder}'):
            os.makedirs(f'{download_folder}/{post_folder}')
        post_path = f'{download_folder}/{post_folder}'
        
        # Создать файл stop.txt
        with open(os.path.join(post_path, 'stop.txt'), 'w') as file:
            file.write("Я запрещаю скачивать из меня файлы!")
        
        video_path = await event.message.download_media(file=f'{download_folder}/{post_folder}/{post_folder}')
        print(f"Видео сохранено в {video_path}")
        
        # Удалить файл stop.txt
        if os.path.exists(f'{post_path}/stop.txt'):
            os.remove(f'{post_path}/stop.txt')
                
        return video_path
    return None

async def download_post(event, source_folder, post_folder):
    """Скачивает весь пост (текст, фото, видео) в одну папку."""
    
    if post_folder == None or post_folder == 'None':
        post_folder = str(event.message.id)
    if not os.path.exists(f'{source_folder}/{post_folder}'):
        os.makedirs(f'{source_folder}/{post_folder}')
    post_path = f'{source_folder}/{post_folder}'

                 
    # Создать файл stop.txt
    with open(os.path.join(post_path, 'stop.txt'), 'w') as file:
        file.write("Я запрещаю скачивать из меня файлы!")    
    
    # добвление файла ожидание загрузки
    group_id = post_folder.split('_')[2]     
    while True:
        task_number = str(random.randint(1, 100))   
        # Проверяем, существует ли ключ в словаре
        if downloads_list_new.get(group_id, {}).get(str(task_number)) is None:
            break            
    # Инициализация словаря, если он еще не существует
    if group_id not in downloads_list_new:
        downloads_list_new[group_id] = {}
    # Присваиваем значение 'start' для task_number
    downloads_list_new[group_id][str(task_number)] = 'start'
    
    

    # Сохраняем текст
    if event.message.text:
        with open(os.path.join(post_path, 'text.txt'), 'w', encoding='utf-8') as f:
            f.write(event.message.text)
    
    # Сохраняем медиа (фото, видео, документы)
    if event.message.media:
        media_path = await event.message.download_media(file=post_path)
        print(f"Медиа сохранены в {media_path}")
        
    # Удаление загрузки из словаря
    if group_id in downloads_list_new:  # Проверяем, существует ли group_id        
        if (task_number) in downloads_list_new[group_id]:  # Проверяем, существует ли task_number
            # Проверяем, станет ли вложенный словарь пустым после удаления task_number
            if len(downloads_list_new[group_id]) == 1:
                del downloads_list_new[group_id]  # Удаляем group_id, если вложенный словарь станет пустым
                
                # Удалить файл stop.txt
                if os.path.exists(f'{post_path}/stop.txt'):
                    os.remove(f'{post_path}/stop.txt')
            else:
                del downloads_list_new[group_id][task_number]  # Удаляем task_number

    
    print(downloads_list_new)

async def send_post(target_unloading, folder, content):
    """Отправляет пост с текстом и медиафайлами."""
    while 100:           
        try:
            if content == "video":
                video = f'{VIDEO_FOLDER}/{folder}.mp4'
                print(f'\n\n{video}\n\n')
                await client_loader.send_file(target_unloading, video)
            if content == "post":
                folder_path = f'{POST_FOLDER}/{folder}'
                
                with open(f'{folder_path}/text.txt', 'r', encoding='utf-8') as file:
                    text = file.read()

                media_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
                
                await client_loader.send_message(target_unloading, text)

                for media_file in media_files:
                    await client_loader.send_file(target_unloading, media_file)
            break
        except errors.FloodWaitError as e:
            print(f"Необходимо подождать {e.seconds} секунд")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"Ошибка: {e}")
            await asyncio.sleep(1)
        
async def check_chat_entity(chat_link):
    try:
        chat_entity = await client_loader.get_entity(chat_link)
        if isinstance(chat_entity, PeerChannel):
            chat_id = chat_entity.channel_id
        elif isinstance(chat_entity, PeerChat):
            chat_id = chat_entity.chat_id
        elif isinstance(chat_entity, PeerUser):
            chat_id = chat_entity.user_id
        else:
            chat_id = chat_entity.id
        return chat_id
    except errors.FloodWaitError as e:
        print(f"Необходимо подождать {e.seconds} секунд")
        await asyncio.sleep(e.seconds)
        return await check_chat_entity(chat_link)
    except Exception as e:
        print(f"Ошибка при получении сущности чата: {e}")
        return None
        
async def strat_unload():
    # await client_unloader.start()
    # print("(Telethon)Бот выгрузки запущен. Ожидание новых сообщений...")
    while not client_loader.is_connected():
        print('Нет подключения к аккаунту!')
        await asyncio.sleep(5)
        if client_loader.is_connected():
            print('Подключени к аккаунту востановлено!')
        
    while True:
        try:
            text = None
            user_json = UserDataManager('users.json', False)
            downloads_folder = os.listdir(VIDEO_FOLDER)
            posts_folder = os.listdir(POST_FOLDER)
            

            if bool(downloads_folder):
                for folder in downloads_folder:
                    files = os.listdir(f'{VIDEO_FOLDER}/{folder}')
                    if 'stop.txt' not in files: 
                        user_id = folder.split('_')[0]
                        soft_name = folder.split('_')[1]
                        soft = user_json.get_user_data(user_id, 'soft')[f'{soft_name}']   
                        folder_path = f'{VIDEO_FOLDER}/{folder}'
                        unloading_mode = str(soft['unloading_mode'])
                        
                        
                        
                        if unloading_mode == 'tg_chenal':
                            await client_loader.send_file(str(soft['target_unloading']), f'{folder_path}/{files[0]}')
                        
                        if unloading_mode == 'ls':
                            bot = Bot(token=BOT_TOKEN)
                            await bot.send_video(chat_id=user_id, video=FSInputFile(os.path.join(folder_path, files[0])), caption=f'Видео от программы {soft_name}')

                            print(unloading_mode)
                        if unloading_mode == 'server':
                            bot = Bot(token=BOT_TOKEN)
                                   
                            shutil.copytree(folder_path, f'{DOWNLOAD_FOLDER}/{user_id}/{folder}') 
                            
                            await bot.send_message(chat_id=user_id, text=f"📂 __Файл от программы {soft_name}:__\n"
                                                                         f"- __Путь к файлу:__ `{DOWNLOAD_FOLDER}/{user_id}/{folder}`\n\n"
                                                                          "🔗 __Сохранен на сервере.__", parse_mode='Markdown')
                            
                            

                        if unloading_mode == 'vk':
                            print(unloading_mode)
                        if unloading_mode == 'instagram':
                            print(unloading_mode)
                        if unloading_mode == 'youtube':
                            print(unloading_mode)
                        if unloading_mode == 'tiktok':
                            # sand_video(f'{folder_path}')
                            print(unloading_mode)
                        
                        
                        print(f'Файл: {files[0]} отправлен')
                        
                        # Удалить файл
                        
                        if os.path.exists(f'{folder_path}'):
                            shutil.rmtree(folder_path)  
                            
            if bool(posts_folder):
                for folder in posts_folder:
                    files = os.listdir(f'{POST_FOLDER}/{folder}')
                    if 'stop.txt' not in files: 
                        user_id = folder.split('_')[0]
                        soft_name = folder.split('_')[1]
                        soft = user_json.get_user_data(user_id, 'soft')[f'{soft_name}']       
                        folder_path = f'{POST_FOLDER}/{folder}'
                        unloading_mode = str(soft['unloading_mode'])
                        
                        # работа с .txt
                        if os.path.exists(f'{folder_path}/text.txt'):
                            with open(f'{folder_path}/text.txt', 'r', encoding='utf-8') as file:
                                text = file.read()
                            text = await link_rename(text)
                            ai = str(soft['ai'])
                            if ai == 'true':
                                text = await AI_GenerateText(text, True) 

                        media_files = []
                        for file in os.listdir(folder_path):
                            if os.path.isfile(os.path.join(folder_path, file)) and not file.endswith('.txt'):
                                media_files.append(f'{folder_path}/{file}')


                        if unloading_mode == 'tg_chenal':
                            if bool(media_files):
                                if text != None:    
                                    await client_loader.send_file(str(soft['target_unloading']), media_files, caption=text)
                                else:
                                    await client_loader.send_file(str(soft['target_unloading']), media_files)
                            if not bool(media_files) and text != None:  
                                await client_loader.send_message(str(soft['target_unloading']), text)  
                         
                                                
                        if unloading_mode == 'ls':
                            bot = Bot(token=BOT_TOKEN)
                            if bool(media_files):
                                media = []
                                for file_path in media_files:
                                    if file_path == media_files[0]:  # Добавляем подпись только к первому файлу
                                        media.append(InputMediaDocument(media=FSInputFile(file_path), caption=text))
                                    else:
                                        media.append(InputMediaDocument(media=FSInputFile(file_path)))
                                if text != None:    
                                    await bot.send_media_group(chat_id=user_id, media=media)
                                else:
                                    await bot.send_media_group(chat_id=user_id, media=media)
                            if not bool(media_files) and text != None: 
                                await bot.send_message(chat_id=user_id, text=text) 
                                
                        if unloading_mode == 'server':
                            bot = Bot(token=BOT_TOKEN)
                                   
                            shutil.copytree(folder_path, f'{DOWNLOAD_FOLDER}/{user_id}/{folder}') 
                            
                            await bot.send_message(chat_id=user_id, text=f"📂 __Файл от программы {soft_name}:__\n"
                                                                         f"- __Путь к файлу:__ `{DOWNLOAD_FOLDER}/{user_id}/{folder}`\n\n"
                                                                          "🔗 __Сохранен на сервере.__", parse_mode='Markdown')
                            
                            
                        if unloading_mode == 'vk':
                            print(unloading_mode)
                        if unloading_mode == 'instagram':
                            print(unloading_mode)
                        if unloading_mode == 'youtube':
                            print(unloading_mode)
                        if unloading_mode == 'tiktok':
                            print(unloading_mode)    
                            
                            
                        print(f'Пост отправлен')
                        
                        # Удалить файл
                        if os.path.exists(f'{folder_path}'):
                             shutil.rmtree(folder_path)

                    
        except errors.FloodWaitError as e:
            print(f"Необходимо подождать {e.seconds} секунд")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"Ошибка: {e}")
            await asyncio.sleep(1)
        
        await asyncio.sleep(5)
    
    # await client_unloader.run_until_disconnected()
    
def get_chat_id():
    # Загрузка данных пользователей
    user_json = UserDataManager('users.json', False)
    chat_id_link = []
    all_user = user_json.get_user_data()
    # Итерация по данным пользователей
    for user_id, user_data in all_user.items():
        # Проверяем наличие ключа 'soft'
        if 'soft' in user_data:
            soft_data = user_data['soft']
            # Итерация по ключам и значениям внутри 'soft'
            for soft_key, soft_value in soft_data.items():
                # Проверяем наличие ключа 'state'
                if 'state' in soft_value:
                    # Формируем результат
                    # result = {soft_key: soft_value['state']}
                    # pprint.pprint(result)
                    if soft_value['state'] == 'start':    
                         chat_id_link.append(soft_value['target_loading'])
    print(chat_id_link)                  
    return chat_id_link

async def start_loader(): 
    
    # Загрузка данных пользователей
    user_json = UserDataManager('users.json', False)
    
    """Запускает прослушивание канала."""
    @client_loader.on(events.NewMessage())
    async def handler(event):   
        print('Найдено новое сообщение/элемент сообщения')
        await asyncio.sleep(3)
        if not event.message.out:
            all_user = user_json.get_user_data()
            # Итерация по данным пользователей
            for user_id, user_data in all_user.items():
                # Проверяем наличие ключа 'soft'
                if 'soft' in user_data:
                    soft_data = user_data['soft']
                    # Итерация по ключам и значениям внутри 'soft'
                    for soft_key, soft_value in soft_data.items():
                        # Проверяем наличие ключа 'state'
                        if 'state' in soft_value:
                            # Формируем результат
                            # result = {soft_key: soft_value['state']}
                            # pprint.pprint(result)
                            if soft_value['state'] == 'start':    
                                chat_link = soft_value['target_loading']
                                # Получаем числовой ID чата по ссылке
                                target_loading = await check_chat_entity(chat_link)
                                if not target_loading:
                                    continue
                                    
                                # Получаем ID чата/канала из события
                                if isinstance(event.peer_id, PeerChannel):
                                    event_chat_id = event.peer_id.channel_id
                                elif isinstance(event.peer_id, PeerChat):
                                    event_chat_id = event.peer_id.chat_id
                                elif isinstance(event.peer_id, PeerUser):
                                    event_chat_id = event.peer_id.user_id
                                else:
                                    event_chat_id = event.peer_id.id  # Для других сущностей
                                # Сравниваем ID
                                if target_loading == event_chat_id:
                                    # print(f"Сообщение пришло из нужного чата/канала/группы/пользователя: {target_loading}")

                                    loading_mode = soft_value['loading_mode']
                                    content = soft_value['content']
                                    report = soft_value['report']
                                    
                                    media_name = [user_id, soft_key]
                                    if event.message.grouped_id == None or event.message.grouped_id == 'None':
                                        group_id = event.message.id
                                    else:
                                        group_id = event.message.grouped_id
                                            # цикл  
                                    if loading_mode == 'continuous':
                                        if content == 'video':
                                            post_folder = f'{media_name[0]}_{media_name[1]}_{group_id}'
                                            await download_video(event, VIDEO_FOLDER, post_folder)
                                        elif content == 'post':
                                            post_folder = f'{media_name[0]}_{media_name[1]}_{group_id}'
                                            await download_post(event, POST_FOLDER, post_folder)
                                        # await send_post(target_unloading, post_folder, content)
                                        
                                        
                                    # # 1 
                                    # if loading_mode == 'once':
                                    #     if content == 'video':
                                    #         post_folder = str(event.message.id)
                                    #         await download_video(event, DOWNLOAD_FOLDER, post_folder)
                                    #         # await stop_soft(soft_json, soft, run_task, callback, user_manager)
                                    #     elif content == 'post':
                                    #         post_folder = str(event.message.grouped_id)
                                    #         await download_post(event, POST_FOLDER, post_folder)

    await client_loader.start()
    print("(Telethon)Бот загрузки запущен. Ожидание новых сообщений...")
    await client_loader.run_until_disconnected()


