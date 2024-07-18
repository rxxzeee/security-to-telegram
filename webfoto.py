import cv2
import requests
import os
import threading
from pathlib import Path
from pynput import keyboard, mouse
import time

# Вставьте сюда токен вашего бота и ваш chat_id
TOKEN = 'Your_token_here'
CHAT_ID = 'Your_id_here'

# Глобальная переменная для отслеживания активности
last_activity_time = time.time()
waiting_for_key = False
# Установка клавиши для предотвращения отправки фото
expected_key = keyboard.Key.esc

def send_photo_to_telegram(photo_path):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    with open(photo_path, 'rb') as photo:
        files = {'photo': photo}
        data = {'chat_id': CHAT_ID}
        response = requests.post(url, files=files, data=data)
    if response.status_code == 200:
        print("Фото успешно отправлено в Telegram.")
    else:
        print(f"Не удалось отправить фото. Ошибка: {response.status_code}")

def take_photo():
    try:
        # Используем встроенную веб-камеру
        cap = cv2.VideoCapture(0)

        # Проверяем успешность открытия камеры
        if not cap.isOpened():
            raise Exception("Не удалось открыть камеру.")

        # Чтение изображения с камеры
        ret, frame = cap.read()

        # Проверяем успешность чтения кадра
        if not ret:
            raise Exception("Не удалось получить кадр с камеры.")

        # Путь к временному файлу
        temp_photo_path = Path('photo.jpg')

        # Сохраняем изображение
        cv2.imwrite(str(temp_photo_path), frame)

        # Отправляем фото в Telegram
        send_photo_to_telegram(temp_photo_path)

        # Удаляем временный файл
        temp_photo_path.unlink()

    except Exception as e:
        print(f"Ошибка: {e}")

    finally:
        # Освобождаем ресурсы
        cap.release()

def on_press(key):
    global last_activity_time, waiting_for_key
    last_activity_time = time.time()
    if waiting_for_key:
        if key == expected_key:
            print("Ожидаемая клавиша нажата, фото не будет сделано.")
        else:
            print("Фото будет отправлено в Telegram.")
            take_photo()
        waiting_for_key = False

def on_move(x, y):
    global last_activity_time
    last_activity_time = time.time()

def check_inactivity():
    global waiting_for_key
    while True:
        if time.time() - last_activity_time > 60 and not waiting_for_key:
            print("Компьютер был неактивен в течение 1 минуты. Ожидание нажатия клавиши.")
            waiting_for_key = True
        time.sleep(1)

if __name__ == "__main__":
    # Слушатели для отслеживания активности
    keyboard_listener = keyboard.Listener(on_press=on_press)
    mouse_listener = mouse.Listener(on_move=on_move)

    # Запускаем слушатели
    keyboard_listener.start()
    mouse_listener.start()

    # Запуск проверки на неактивность в отдельном потоке
    inactivity_thread = threading.Thread(target=check_inactivity)
    inactivity_thread.start()

    # Запускаем основной поток, чтобы предотвратить завершение программы
    keyboard_listener.join()
    mouse_listener.join()
    inactivity_thread.join()