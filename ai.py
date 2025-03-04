import os
import aiohttp
import asyncio
from pprint import pprint

# Очистка консоли
os.system('cls||clear')


async def AI_GenerateText(text, debug):
    print('(AI)Генерация текста')
    model_ai = 'gpt-4o-mini' #deepseek-chat
    API_KAY = 'API_KAY'
    url = "https://bothub.chat/api/v2/openai/v1/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KAY}',
    }
    payload = {
        "messages": [
            {
                "role": "user",
                "content": f"Сделай пост что бы он был продающим, красивым и не большой, основывайся только на факты и увиличь цену на 30%\n\n{text}",
            }
        ],
        "model": model_ai,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                result = str(data['choices'][0]['message']['content'])
                if debug == True:
                    print(data)
            else:
                result = False
    return result

async def link_rename(text):
    # Словарь с заменами
    links_dict = {
        "https://t.me/AlesyaMex": "https://t.me/sergeimagicmeha",
        "https://t.me/men_furs": "https://t.me/magicmehamen",
        "@AlexeyFurs (Алексей)": "@SergeyPromtorg (Сергей)",
    
        "Повседневная одежда здесь 👇": "Женская одежда здесь 👇",
        "https://t.me/sportimperial": "https://t.me/Magicmeha",
        
        
        "❤️Отзывы довольных покупателей 😍": "",
        "https://t.me/imperialotziv": "",     
        "👠обувь https://t.me/shoesimperial1": "",
        "https://t.me/imperialotziv": "",           
        "@AlexProStore (Александр)": ""
    }
    for old_link, new_link in links_dict.items():
        text = text.replace(old_link, new_link)
    return text
    