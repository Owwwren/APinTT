import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys

# Очистка консоли
import os
os.system('cls||clear')


# Путь к папке с видео
svideo_folder = os.path.abspath("downloads/1853593910/1853593910_Ls_630")
sdescription = 'Так чисто для тестов!'
# Путь к ChromeDriver

# Настройки TikTok
tiktok_login_url = "https://www.tiktok.com/login"
tiktok_upload_url = "https://www.tiktok.com/tiktokstudio/upload"
cookies_file = "tik-tok/com_cookies.json" #tiktok_cookies.json

# Настройки прокси
proxy_username = "proxy_username"  # Замените на ваш логин прокси
proxy_password = "proxy_password"  # Замените на ваш пароль прокси
proxy_host = "proxy_host"  # Замените на хост прокси
proxy_port = "proxy_port"  # Замените на порт прокси


# Функция для загрузки cookies
def load_cookies(driver):
    if os.path.exists(cookies_file):
        with open(cookies_file, "r") as file:
            cookies = json.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)
        print("Cookies загружены.")
    else:
        print("Файл cookies не найден.")

# Функция для загрузки видео
def upload_video(driver, video_path, description):
    driver.get(tiktok_upload_url)
    time.sleep(5)  # Ждем загрузки страницы

    # Загружаем видео
    file_input = driver.find_element(By.XPATH, "//input[@type='file']")
    file_input.send_keys(video_path)

    # Вводим описание
    time.sleep(5)  # Ждем загрузки видео
    try:
        description_input = driver.find_element(By.XPATH, "//br[@data-text='true']")
    except:
        description_input = driver.find_element(By.XPATH, "//span[@data-text='true']")
    time.sleep(5)
    description_input.clear()
    description_input.send_keys(description)
    time.sleep(5)  # Ждем загрузки страницы

    # Публикуем видео
    # publish_button = driver.find_element(By.XPATH, "//button[div/div[text()='Опубликовать']]")
    # publish_button.click()

    # Ждем завершения загрузки
    time.sleep(10)

def sand_video(description, video_folder):
    
    
    chrome_driver_path = "tik-tok/chromedriver/chromedriver.exe"
    
    
    # Инициализация браузера
    service = Service(chrome_driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")  # Отключаем уведомления
    options.add_argument(f'--disable-blink-features=AutomationControlled')
    # options.add_argument(f'--proxy-server=http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}')
    options.add_argument(f'--proxy-server={proxy_host}:{proxy_port}')
    driver = webdriver.Chrome(service=service, options=options)

    
    # Загружаем cookies, если они есть
    driver.get("https://www.tiktok.com")  # Открываем TikTok для установки cookies
    load_cookies(driver)

    # Проверяем, авторизованы ли мы
    driver.get(tiktok_upload_url)
    time.sleep(5)

    if "login" in driver.current_url:
        print("Не удалось авторезироваться через cookies.")
        return
    else:
        print("Авторизация выполнена с использованием cookies.")

    # Получаем список видео в папке
    video_files = [f for f in os.listdir(video_folder) if f.endswith('.mp4')]

    # Постим каждое видео
    for video_file in video_files:
        video_path = os.path.join(video_folder, video_file)
        try:
            upload_video(driver, video_path, description=description)
            print(f"Видео {video_file} успешно загружено!")
        except Exception as e:
            print(f"Ошибка при загрузке видео {video_file}: {e}")

    # Закрываем браузер
    time.sleep(5000)
    driver.quit()
    print("Все видео загружены!")
    
# sand_video(description, video_folder)
