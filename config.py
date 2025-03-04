import os

# Ваши учетные данные
API_ID = 'API_ID'
API_HASH = 'API_HASH'
API_VK = 'API_VK'
BOT_TOKEN = 'BOT_TOKEN'
BOT_TOKEN2 = 'BOT_TOKEN2'

# Папки для сохранения
VIDEO_FOLDER = 'video'
POST_FOLDER = 'posts'
DOWNLOAD_FOLDER = 'downloads'

# Создаем папки, если они не существуют
if not os.path.exists(VIDEO_FOLDER):
    os.makedirs(VIDEO_FOLDER)
if not os.path.exists(POST_FOLDER):
    os.makedirs(POST_FOLDER)
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)