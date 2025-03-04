from aiogram import Dispatcher, Bot, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext


from keyboards import get_main_keyboard, back_inlinekb, get_stop_keyboard, start_inlinekb, soft_inlinekb, loading_mode_inlinekb, unloading_mode_inlinekb, targets_mode_inlinekb, content_mode_inlinekb, delete_soft_inlinekb, additional_functions_inlinekb

from config import BOT_TOKEN
from utils import UserDataManager, time_delet_message, is_link, name_correct, stop_soft
from state_machine import Status
import asyncio
import json

bot = Bot(token=BOT_TOKEN)
user_manager = UserDataManager('users.json', False)

# Хранение состояния пользователя
user_data = {}




# Обработчик кнопки "Назад"
async def back_handler(callback: CallbackQuery, state: FSMContext):
    if await state.get_state() == 'Status:CreateSoft_name' or await state.get_state() == 'Status:OpenSoft':
        await start(callback, state)
    if await state.get_state() == 'Status:OpenSoftSettings':
        await state.set_state(Status.OpenSoft)
        await opensoft(callback, state)
    if await state.get_state() == 'Status:OpenSoftSettingsTargetMod':
        soft = callback.data.split(".")[1]  # soft
        await state.set_state(Status.OpenSoftSettings)
        await callback.message.edit_text('🎯 <b>Выбери источник:</b>  \n'
                                         '\n'
                                         '1. 📥 <b>Загрузка</b> — загрука данный из указанного пути.  \n'
                                         '2. 📤 <b>Выгрузка</b> — выгрузка данный в указанный путь.  \n'
                                         '\n'
                                         '👇 <i>Выбери режим и нажми нанего!</i>\n', reply_markup=targets_mode_inlinekb(str(callback.from_user.id), soft))
    await callback.answer()



# Обработчик команды /start
async def start_command(message: Message, state: FSMContext):
    await start(message, state)
async def start(message, state):
    if isinstance(message, Message):
        if not user_manager.get_user_data(str(message.from_user.id), 'soft'):
            user_manager.add_or_update_user_data(str(message.from_user.id), 'user_name', message.from_user.username)
            user_manager.add_or_update_user_data(str(message.from_user.id), 'first_name', message.from_user.first_name)
            user_manager.add_or_update_user_data(str(message.from_user.id), 'last_name', message.from_user.last_name)
        await message.answer(f"👋 <b>Привет, {message.from_user.first_name}!</b>\n\n"
                             "Пожалуйста, выбери программу из списка ниже: \n"
                             "👇👇👇", reply_markup=start_inlinekb(str(message.from_user.id)))
    if isinstance(message, CallbackQuery):
        if not user_manager.get_user_data(str(message.from_user.id), 'soft'):
            user_manager.add_or_update_user_data(str(message.from_user.id), 'user_name', message.from_user.username)
            user_manager.add_or_update_user_data(str(message.from_user.id), 'first_name', message.from_user.first_name)
            user_manager.add_or_update_user_data(str(message.from_user.id), 'last_name', message.from_user.last_name)
        await message.message.edit_text(f"👋 <b>{message.from_user.first_name}!</b>\n\n"
                             "Пожалуйста, выбери программу из списка ниже: \n"
                             "👇👇👇", reply_markup=start_inlinekb(str(message.from_user.id)))
        await message.answer()
    
# Обработчик создания софта
async def create_soft(callback: CallbackQuery, state: FSMContext):
    try:
        len_soft = len(user_manager.get_user_data(str(callback.from_user.id), 'soft'))
    except:
        len_soft = 0
    finally:
        if len_soft <= 5:
            await state.set_state(Status.CreateSoft_name)
            sent_message = await callback.message.edit_text(f"👋 <b>{callback.from_user.first_name}!</b>\n\n"
                                                            "Пожалуйста, укажи название для программы:\n"
                                                            "👇👇👇\n"
                                                            "\n"
                                                            "📝 <b>Примеры названий:</b>  \n"
                                                            "- soft\n"
                                                            "- софт\n"
                                                            "- Автопостер\n"
                                                            "- AutoPost\n\n"
                                                            "Напиши своё название, и я помогу тебе с настройкой! 😊\n", reply_markup=back_inlinekb())
            await state.update_data(bot_message_id=sent_message.message_id)  
        else:
            sent_message = await callback.message.answer(f"⚠️ <b>Внимание, {callback.from_user.first_name}!</b> ⚠️\n"
                                                         "\n"
                                                         "🚫 <b>Превышен лимит!</b>  \n"
                                                         "Максимальное число приложений: <b>6</b>.  \n"
                                                         "\n"
                                                         "📌 Пожалуйста, удали одно из приложений, чтобы добавить новое.  \n"
                                                         "Или измени старое приложение:  \n"
                                                         "\n"
                                                         "1. 📋 <b>Нажми на приложение</b>  \n"
                                                         "2. 🔄 <b>Отредактируй функции</b>  \n"
                                                         "3. 🗑️ <b>или нажми 🗑️Удалить</b> \n"
                                                         "\n")
            asyncio.create_task(time_delet_message(chat_id=callback.message.chat.id, message_id=sent_message.message_id, time=5))
        await callback.answer()
         
# Обработчик настроеk софта
async def settings_soft(callback: CallbackQuery, state: FSMContext):
    soft = callback.data.split(".")[1]  # soft
    settings = callback.data.split(".")[2]  # settings
    if settings == "loading_mode":
        await state.set_state(Status.OpenSoftSettings)
        await callback.message.edit_text('🎯 <b>Выбери режим загрузки:</b> \n'
                                     '\n'
                                     '1. ⤵️ <b>1 раз</b> — загрузка последнего поста. \n'
                                     '2. 🔄 <b>Постоянно</b> — загрузка новых сообщений без остановки. \n'
                                     '\n'
                                     '👇 <i>Выбери режим и нажми нанего!</i>', reply_markup=loading_mode_inlinekb(str(callback.from_user.id), soft))
    if settings == "unloading_mode":
        await state.set_state(Status.OpenSoftSettings)
        await callback.message.edit_text('🎯 <b>Выбери режим выгрузки:</b>  \n'
                                     '\n'
                                     '1. 📱 <b>Tik-Tok</b> — загрузка видео на Tik-Tok.  \n'
                                     '2. 📹 <b>YouTube</b> — загрузка видео на YouTube.\n'
                                     '3. 📷 <b>Instagram</b> — загрузка видео на Instagram.\n'
                                     '4. 📞 <b>Vk</b> — загрузка видео/пост в группу Telegram.\n'
                                     '5. 👯‍♀️ <b>Группа</b> — загрузка видео на Vk.\n'
                                     '6. 📩 <b>Лс</b> — отправка видео/поста в личное сообщение.\n'
                                     '7. 🖥️ <b>Сервер</b> — выгрузка видео/пост на удалённый сервер. \n'
                                     '\n'
                                     '👇 <i>Выбери режим и нажми нанего!</i>', reply_markup=unloading_mode_inlinekb(str(callback.from_user.id), soft))
    if settings == "targets":
        await state.set_state(Status.OpenSoftSettings)
        await callback.message.edit_text('🎯 <b>Выбери источник:</b>  \n'
                                         '\n'
                                         '1. 📥 <b>Загрузка</b> — загрука данный из указанного пути.  \n'
                                         '2. 📤 <b>Выгрузка</b> — выгрузка данный в указанный путь.  \n'
                                         '\n'
                                         '👇 <i>Выбери режим и нажми на него!</i>\n', reply_markup=targets_mode_inlinekb(str(callback.from_user.id), soft))
    if settings == "content":
        await state.set_state(Status.OpenSoftSettings)
        await callback.message.edit_text('🎯 <b>Выбери что загружать:</b>\n'
                                     '\n'
                                     '1. 🎥 Видео — загрузка видеофайлов. \n'
                                     '2. 🧾 Пост — загрузка текст, фото и видео. \n'
                                     '\n'
                                     '👇 <i>Выбери вариант и нажми на него!!</i>', reply_markup=content_mode_inlinekb(str(callback.from_user.id), soft))
    if settings == "delete":
        await state.set_state(Status.OpenSoftSettings)
        await callback.message.edit_text('Удалить программу?', reply_markup=delete_soft_inlinekb(str(callback.from_user.id), soft))
    if settings == "additional_functions":
        await state.set_state(Status.OpenSoftSettings)
        await callback.message.edit_text('🎯 <b>Выбери что включить:</b>\n'
                                     '\n'
                                     '1. 🧾 Отчет — получать отчет задач бота. \n'
                                     '2.  🤖 AI — ИИ редактирование текста. \n'
                                     '\n'
                                     '👇 <i>Выбери вариант и нажми на него!!</i>', reply_markup=additional_functions_inlinekb(str(callback.from_user.id), soft))
    if settings == "start":
        await starter_soft(callback, state)
    if settings == "stop":
        await starter_soft(callback, state)
    await callback.answer()
         
# Обработчик открытия панели софта
async def open_soft(callback: CallbackQuery, state: FSMContext):
    await opensoft(callback, state)
async def opensoft(callback, state, soft=None):
    await state.set_state(Status.OpenSoft)
    soft_date = user_manager.get_user_data(str(callback.from_user.id), 'soft')
    if isinstance(callback, CallbackQuery):
        if soft == None:
            soft = callback.data.split(".")[1]  # soft
        if soft_date[f"{soft}"]["state"] == "start":
            soft_state = "ВКЛ ✅"
        else:
            soft_state = "ВЫКЛ ❌"
        await callback.message.edit_text(f'📛 <b>{soft}</b> | {soft_state}\n'
                        f'\n'
                        f'⚙️ <b>Режим загрузки:</b> {name_correct(soft_date[f"{soft}"]["loading_mode"])} | {name_correct(soft_date[f"{soft}"]["content"])}\n'
                        f'⚙️ <b>Режим выгрузки:</b> {name_correct(soft_date[f"{soft}"]["unloading_mode"])}\n'
                        f'✨ <b>Доп. функции</b> {name_correct(soft_date[f"{soft}"]["report"])}\n'
                        f'\n'
                        '🌐 <b>Источники:</b>\n'
                        f'⬇️ {name_correct(soft_date[f"{soft}"]["target_loading"])}\n'
                        f'⬆️ {name_correct(soft_date[f"{soft}"]["target_unloading"])}\n'
                        '\n'
                        f'📝 Настройте параметры, чтобы начать работу! \n', reply_markup=soft_inlinekb(str(callback.from_user.id), soft), parse_mode="HTML")
        await callback.answer()
    if isinstance(callback, Message):
        soft = callback.text  # soft
        if soft_date[f"{soft}"]["state"] == "start":
            soft_state = "ВКЛ ✅"
        else:
            soft_state = "ВЫКЛ ❌"
        await callback.answer(f'📛 <b>{soft}</b> | {soft_state}\n'
                    f'\n'
                    f'⚙️ <b>Режим загрузки:</b> {name_correct(soft_date[f"{soft}"]["loading_mode"])} | {name_correct(soft_date[f"{soft}"]["content"])}\n'
                    f'⚙️ <b>Режим выгрузки:</b> {name_correct(soft_date[f"{soft}"]["unloading_mode"])}\n'
                    f'✨ <b>Доп. функции</b> {name_correct(soft_date[f"{soft}"]["report"])}\n'
                    f'\n'
                    '🌐 <b>Источники:</b>\n'
                    f'⬇️ {name_correct(soft_date[f"{soft}"]["target_loading"])}\n'
                    f'⬆️ {name_correct(soft_date[f"{soft}"]["target_unloading"])}\n'
                    '\n'
                    f'📝 Настройте параметры, чтобы начать работу!', reply_markup=soft_inlinekb(str(callback.from_user.id), soft), parse_mode="HTML")

# Обработчик ввода пользователя
async def user_input(message: Message, state: FSMContext):
    if await state.get_state() == 'Status:CreateSoft_name':
        if user_manager.get_user_data(str(message.from_user.id), 'soft'):
            soft_date = user_manager.get_user_data(str(message.from_user.id), 'soft')
            try:
                soft_date[f"{message.text}"]
                soft_copy = True
            except:
                soft_copy = False
            finally:
                if soft_copy:
                    sent_message = await message.answer(f'Программа с названием {message.text} уже существует!')
                    asyncio.create_task(time_delet_message(chat_id=message.chat.id, message_id=sent_message.message_id, time=5))
                    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                else:
                    soft_date[f"{message.text}"] = {
                                                    "loading_mode": "None",
                                                    "unloading_mode": "None",
                                                    "target_unloading": "None",
                                                    "target_loading": "None",
                                                    "content": "None",
                                                    "state": "stop",
                                                    "ai": "false",
                                                    "report": "false"
                                                    }
                    user_manager.add_or_update_user_data(str(message.from_user.id), 'soft', soft_date)
        else:
            soft_copy = False
            user_manager.add_or_update_user_data(str(message.from_user.id), 'soft', {f"{message.text}": {
                                                                                                        "loading_mode": "None",
                                                                                                        "unloading_mode": "None",
                                                                                                        "target_unloading": "None",
                                                                                                        "target_loading": "None",
                                                                                                        "content": "None",
                                                                                                        "state": "stop",
                                                                                                        "ai": "false",
                                                                                                        "report": "false"
                                                                                                        }
                                                                                     })
        if not soft_copy:
            state_data = await state.get_data()
            bot_message_id = state_data.get('bot_message_id')
            if bot_message_id:
                await bot.edit_message_text(chat_id=message.chat.id, message_id=bot_message_id, text=f'Программа {message.text} создана!')    
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            asyncio.create_task(time_delet_message(chat_id=message.chat.id, message_id=bot_message_id, time=5))
            await opensoft(message, state)
    if await state.get_state() == 'Status:OpenSoftSettingsTargetMod':
        if not is_link(message.text):
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot_message = await message.answer(f'{message.text} это не ссылка!')
            asyncio.create_task(time_delet_message(chat_id=message.chat.id, message_id=bot_message.message_id, time=5))
        else:
            state_data = await state.get_data()
            soft = state_data.get('soft')  # mode
            mode = state_data.get('mode')  # soft
            soft_json = user_manager.get_user_data(str(message.from_user.id), 'soft')
            
            if mode == "target_loading":
                soft_json[f"{soft}"]["target_loading"] = f"{message.text}"
            if mode == "target_unloading":
                soft_json[f"{soft}"]["target_unloading"] = f"{message.text}"
            
            user_manager.add_or_update_user_data(str(message.from_user.id), 'soft', soft_json)
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            
            bot_message = await message.answer(f'Ссылка {message.text} успешно добавлена!')
            asyncio.create_task(time_delet_message(chat_id=message.chat.id, message_id=bot_message.message_id, time=5))
            
            bot_message_id = state_data.get('bot_message_id')
            if bot_message_id:
                await state.set_state(Status.OpenSoftSettings)
                await bot.edit_message_text(chat_id=message.chat.id, message_id=bot_message_id, text='🎯 <b>Выбери источник:</b>  \n'
                                                                                                        '\n'
                                                                                                        '1. 📥 <b>Загрузка</b> — загрука данный из указанного пути.  \n'
                                                                                                        '2. 📤 <b>Выгрузка</b> — выгрузка данный в указанный путь.  \n'
                                                                                                        '\n'
                                                                                                        '👇 <i>Выбери режим и нажми нанего!</i>\n', reply_markup=targets_mode_inlinekb(str(message.from_user.id), soft))  

async def loading_mode(callback: CallbackQuery, state: FSMContext):
    soft = callback.data.split(".")[1]  # soft
    mode = callback.data.split(".")[2]  # mode
    soft_json = user_manager.get_user_data(str(callback.from_user.id), 'soft')
    soft_json[f"{soft}"]["loading_mode"] = f"{mode}"
    
    user_manager.add_or_update_user_data(str(callback.from_user.id), 'soft', soft_json)
    
    await callback.message.edit_text('🎯 <b>Выбери режим загрузки:</b> \n'
                                     '\n'
                                     '1. ⤵️ <b>1 раз</b> — загрузка последнего поста. \n'
                                     '2. 🔄 <b>Постоянно</b> — загрузка новых сообщений без остановки. \n'
                                     '\n'
                                     '👇 <i>Выбери режим и нажми нанего!</i>', reply_markup=loading_mode_inlinekb(str(callback.from_user.id), soft))
    await callback.answer()
    
async def unloading_mode(callback: CallbackQuery, state: FSMContext):
    soft = callback.data.split(".")[1]  # soft
    mode = callback.data.split(".")[2]  # mode
    soft_json = user_manager.get_user_data(str(callback.from_user.id), 'soft')
    soft_json[f"{soft}"]["unloading_mode"] = f"{mode}"
    
    if mode == "ls":
        soft_json[f"{soft}"]["target_unloading"] = "Личное сообщение в бота"
    if mode == "server":
        soft_json[f"{soft}"]["target_unloading"] = "Сервер"
    if mode != "ls" and  mode != "server":
        soft_json[f"{soft}"]["target_unloading"] = "None"
        
    
    user_manager.add_or_update_user_data(str(callback.from_user.id), 'soft', soft_json)
    
    await callback.message.edit_text('🎯 <b>Выбери режим выгрузки:</b>  \n'
                                     '\n'
                                     '1. 📱 <b>Tik-Tok</b> — загрузка видео на Tik-Tok.  \n'
                                     '2. 📹 <b>YouTube</b> — загрузка видео на YouTube.\n'
                                     '3. 📷 <b>Instagram</b> — загрузка видео на Instagram.\n'
                                     '4. 📞 <b>Vk</b> — загрузка видео/пост в группу Telegram.\n'
                                     '5. 👯‍♀️ <b>Группа</b> — загрузка видео на Vk.\n'
                                     '6. 📩 <b>Лс</b> — отправка видео/поста в личное сообщение.\n'
                                     '7. 🖥️ <b>Сервер</b> — выгрузка видео/пост на удалённый сервер. \n'
                                     '\n'
                                     '👇 <i>Выбери режим и нажми нанего!</i>', reply_markup=unloading_mode_inlinekb(str(callback.from_user.id), soft))
    await callback.answer()
    
async def targets_mode(callback: CallbackQuery, state: FSMContext):
    soft = callback.data.split(".")[1]  # soft
    mode = callback.data.split(".")[2]  # mode
    soft_json = user_manager.get_user_data(str(callback.from_user.id), 'soft')
    
    if soft_json[f"{soft}"]["loading_mode"] != "None" and soft_json[f"{soft}"]["unloading_mode"] != "None":
        await state.set_state(Status.OpenSoftSettingsTargetMod)
        await state.update_data(mode=mode)
        await state.update_data(soft=soft)
        content = soft_json[f"{soft}"]["content"]
        if content == 'video':
            content = 'видео'
            smile = "🎥"
        if content == 'post':
            content = 'пост'
            smile = "🧾"
        if content == 'None':
            content = 'контент'
            smile = "📊"
                
                
        if mode == "target_loading":
            text = f'канала, откуда загружать {content}'
            url = "https://t.me/ChannelName"
            
        if mode == "target_unloading":
            unloading_mode = soft_json[f"{soft}"]["unloading_mode"]
            if unloading_mode == "tiktok":
                text = f'Tik-Tok, куда загружать {content}'
                link_content = 'cookies'
                url = '\n[{\n"name": "name",\n"value": "value",\n"domain": "domain",\n"path": "path",\n"expires": expires,\n"httpOnly": httpOnly,\n"secure": secure,\n"sameSite": "sameSite"\n}]'
            if unloading_mode == "youtube":
                text = f'YouTube, куда загружать {content}'
                link_content = 'cookies'
                url = '\n[{\n"name": "name",\n"value": "value",\n"domain": "domain",\n"path": "path",\n"expires": expires,\n"httpOnly": httpOnly,\n"secure": secure,\n"sameSite": "sameSite"\n}]'
            if unloading_mode == "instagram":
                text = f'Instagram куда загружать {content}'
                link_content = 'cookies'
                url = '\n[{\n"name": "name",\n"value": "value",\n"domain": "domain",\n"path": "path",\n"expires": expires,\n"httpOnly": httpOnly,\n"secure": secure,\n"sameSite": "sameSite"\n}]'
            if unloading_mode == "vk":
                text = f'Vk, куда загружать {content}'
                link_content = 'api kay'
                url = "vk1.a.ehgcnruwegrt7ywi3grci34g87r4cc_4398vw348o7nvyw87389_v8ny487wi45455"
            if unloading_mode == "tg_chenal":
                link_content = 'ссылку'
                text = f'канал, куда загружать {content}'
                url = "https://t.me/ChannelName"
        
        
        sent_message = await callback.message.edit_text(f'{smile} <b>Отправь {link_content} на {text}:</b>\n'
                                                        '\n'
                                                        '👇 <i>Пример:</i>  \n'
                                                        f'🔗 <code>{url}</code>  \n'
                                                        '\n'
                                                        '📌 <i>Убедись, что ссылка корректна и доступна!</i> \n', parse_mode="HTML", reply_markup=back_inlinekb(soft))
        await state.update_data(bot_message_id=sent_message.message_id)  
        await callback.answer()
    else:
        await callback.answer('Режимы загрузки и выгрузки не заданы!')

async def content_mode(callback: CallbackQuery, state: FSMContext):
    soft = callback.data.split(".")[1]  # soft
    mode = callback.data.split(".")[2]  # mode
    soft_json = user_manager.get_user_data(str(callback.from_user.id), 'soft')
    soft_json[f"{soft}"]["content"] = f"{mode}"
    
    user_manager.add_or_update_user_data(str(callback.from_user.id), 'soft', soft_json)
    
    await callback.message.edit_text('🎯 <b>Выбери что загружать:</b>\n'
                                     '\n'
                                     '1. 🎥 Видео — загрузка видеофайлов. \n'
                                     '2. 🧾 Пост — загрузка текст, фото и видео. \n'
                                     '\n'
                                     '👇 <i>Выбери вариант и нажми нанего!!</i>', reply_markup=content_mode_inlinekb(str(callback.from_user.id), soft))
    await callback.answer()
    
async def delete_soft(callback: CallbackQuery, state: FSMContext):
    soft = callback.data.split(".")[1]  # soft
    soft_json = user_manager.get_user_data(str(callback.from_user.id), 'soft')
    soft_json.pop(f"{soft}", None)
    user_manager.add_or_update_user_data(str(callback.from_user.id), 'soft', soft_json)  
    await state.set_state(None)
    await start(callback, state)         
    
    await callback.answer(f'Программа {soft} удалена!')
    
async def starter_soft(callback, state):
    soft = callback.data.split(".")[1]  # soft
    mode = callback.data.split(".")[2]  # mode
    
    get_soft_date = user_manager.get_user_data(str(callback.from_user.id), 'soft')[f'{soft}']
    soft_json = user_manager.get_user_data(str(callback.from_user.id), 'soft')
    

    if mode == 'start':
        if get_soft_date['target_unloading'] == 'None' and get_soft_date['target_loading'] == 'None':
            await callback.answer(f'🚫 Ошибка, не заданы ссылки!')
        elif get_soft_date['content'] == 'None':
            await callback.answer(f'🚫 Ошибка, не задано что загружать!')
        else:
            if get_soft_date['state'] == 'start':
                await callback.answer(f'Программа {soft} уже работает!')
            else:
                soft_json[f"{soft}"]["state"] = "start"   
                user_manager.add_or_update_user_data(str(callback.from_user.id), 'soft', soft_json)
                
                await callback.answer(f'🎉 Программа {soft} запущена!')
                await opensoft(callback, state, soft)
        
    if mode == 'stop':
        if get_soft_date['state'] == 'stop':
            await callback.answer(f'Программа {soft} уже отключена!')
        else:
            soft_json[f"{soft}"]["state"] = "stop"
            user_manager.add_or_update_user_data(str(callback.from_user.id), 'soft', soft_json)
            
            await callback.answer(f'😔 Программа {soft} остановлена!')
            print("Прослушивание остановлено.")
            
            await opensoft(callback, state, soft)
            
            
async def additional_functions(callback: CallbackQuery, state: FSMContext):
    soft = callback.data.split(".")[1]  # soft
    mode = callback.data.split(".")[2]  # mode
    soft_json = user_manager.get_user_data(str(callback.from_user.id), 'soft')
    
    if mode == "ai":
        if soft_json[f"{soft}"]["ai"] == "false":
            soft_json[f"{soft}"]["ai"] = "true"
        else:
            soft_json[f"{soft}"]["ai"] = "false"
    if mode == "report":
        if soft_json[f"{soft}"]["report"] == "false":
            soft_json[f"{soft}"]["report"] = "true"
        else:
            soft_json[f"{soft}"]["report"] = "false"
        
    
    user_manager.add_or_update_user_data(str(callback.from_user.id), 'soft', soft_json)
    
    await callback.message.edit_text('🎯 <b>Выбери что включить:</b>\n'
                                     '\n'
                                     '1. 🧾 Отчет — получать отчет задач бота. \n'
                                     '2.  🤖 AI — ИИ редактирование текста. \n'
                                     '\n'
                                     '👇 <i>Выбери вариант и нажми на него!!</i>', reply_markup=additional_functions_inlinekb(str(callback.from_user.id), soft))
    await callback.answer()
    
async def loop_task(message: Message, state: FSMContext):
    print('\n')
    current_tasks = asyncio.all_tasks()
    for task_name in current_tasks:
        print(f'{task_name.get_name()}')
def register_handler_message(dp: Dispatcher):
    dp.message.register(start_command, Command(commands= ['start']))
    dp.message.register(loop_task, Command(commands= ['task']))
    dp.message.register(user_input, F.text)
    dp.callback_query.register(back_handler, F.data.startswith("back."))
    
    dp.callback_query.register(open_soft, F.data.startswith("soft."))
    dp.callback_query.register(settings_soft, F.data.startswith("settings_soft."))
    dp.callback_query.register(create_soft, F.data.startswith("create_soft"))
    
    dp.callback_query.register(loading_mode, F.data.startswith("loading_mode."))
    dp.callback_query.register(unloading_mode, F.data.startswith("unloading_mode."))
    dp.callback_query.register(targets_mode, F.data.startswith("targets_mode."))
    dp.callback_query.register(content_mode, F.data.startswith("content_mode."))
    dp.callback_query.register(delete_soft, F.data.startswith("delete_soft."))
    dp.callback_query.register(additional_functions, F.data.startswith("additional_functions."))