
#https://oauth.vk.com/authorize?client_id=TOKEN&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=offline,wall,messages,groups,photos&response_type=token&v=5.131
API_VK = 'API_VK'
import vk_api
from vk_api.upload import VkUpload
# from config import API_VK
from vk_api.utils import get_random_id
import re
import os

# Настройки
USER_ACCESS_TOKEN = API_VK
GROUP_URL = "GROUP_URL"  # Ссылка на группу
POST_TEXT = "Привет, это тестовый пост от имени группы!"
IMAGE_PATH = "vk/image.png"  # Путь к изображению (если нужно)

# Функция для извлечения GROUP_ID из ссылки
def get_group_id_from_url(url):
    """Извлекает GROUP_ID из ссылки на группу."""
    match = re.search(r'(public|club)(\d+)', url)
    if match:
        return -int(match.group(2))  # Возвращаем ID со знаком минус
    else:
        raise ValueError("Неверная ссылка на группу. Ожидается формат: https://vk.com/public123456789 или https://vk.com/club123456789")

# Инициализация VK API
vk_session = vk_api.VkApi(token=USER_ACCESS_TOKEN)
vk = vk_session.get_api()
upload = VkUpload(vk_session)
permissions = vk.account.getAppPermissions()
print("Права токена:", permissions)

def check_token_permissions():
    """Проверяет права токена."""
    try:
        permissions = vk.account.getAppPermissions()
        print("Права токена:", permissions)
        required_scopes = {'wall', 'groups', 'photos'}
        if not required_scopes.issubset(set(permissions)):
            raise ValueError("Токен не имеет необходимых прав: wall, groups, photos")
    except vk_api.exceptions.ApiError as e:
        print(f"Ошибка при проверке прав токена: {e}")

def upload_photo(image_path):
    """Загружает фото на сервер VK и возвращает attachment."""
    try:
        # Передаем image_path как список
        photo = upload.photo_wall(photos=[image_path], group_id=abs(GROUP_ID))[0]
        return f"photo{photo['owner_id']}_{photo['id']}"
    except Exception as e:
        print(f"Ошибка при загрузке фото: {e}")
        return None


def create_post(text, attachments=None):
    """Создает пост на стене группы."""
    try:
        post = vk.wall.post(
            owner_id=GROUP_ID,  # ID группы (со знаком минус)
            from_group=1,  # Пост от имени группы
            message=text,
            attachments=attachments,
            random_id=get_random_id()
        )
        print(f"Пост успешно опубликован! ID поста: {post['post_id']}")
    except vk_api.exceptions.ApiError as e:
        print(f"Ошибка при публикации поста: {e}")

if __name__ == "__main__":
    try:
        # Извлекаем GROUP_ID из ссылки
        GROUP_ID = get_group_id_from_url(GROUP_URL)
        print(f"GROUP_ID: {GROUP_ID}")

        # Проверяем права токена
        # check_token_permissions()

        # Загружаем фото (если нужно)
        if IMAGE_PATH and os.path.exists(IMAGE_PATH):
            attachment = upload_photo(IMAGE_PATH)
        else:
            attachment = None
            print("Изображение не найдено или не указано.")

        # Публикуем пост
        create_post(POST_TEXT, attachment)
    except Exception as e:
        print(f"Произошла ошибка: {e}")