import asyncio
import logging
import sys
from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN
import asyncio
from telegram_client import start_loader, strat_unload
dp = Dispatcher()

# Очистка консоли
import os
os.system('cls||clear')

async def on_startup(_):
    print('(Aiogram)БОТ запущен!')
    
# Регистрация хэндлеров
from handlers import register_handler_message
register_handler_message(dp)


async def main() -> None:
    # Создаем экземпляр бота
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Запускаем задач
    try:
        asyncio.gather(
        start_loader(),
        strat_unload()
        )
        
        print('(Aiogram)БОТ запущен!')
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())