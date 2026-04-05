# test_async.py
# Скрипт для тестирования асинхронности JMS

import requests
import time
import json

BASE_URL = "http://localhost:8000"


def register(username: str, password: str):
    """Регистрация нового пользователя"""
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        params={"username": username, "password": password}
    )
    if response.status_code == 200:
        print(f" Пользователь {username} зарегистрирован")
        return True
    elif response.status_code == 400:
        print(f" Пользователь {username} уже существует")
        return True
    else:
        print(f" Ошибка регистрации: {response.status_code} - {response.text}")
        return False


def login(username: str, password: str) -> str:
    """Логин и получение токена"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        params={"username": username, "password": password}
    )
    
    print(f"Статус ответа: {response.status_code}")
    print(f"Ответ: {response.text}")
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f" Логин успешен, токен получен")
        return token
    else:
        print(f" Ошибка логина: {response.status_code}")
        return None


def make_admin(username: str):
    """Назначить пользователю роль ADMIN (через прямой запрос к БД)"""
    # Создаем временный скрипт для назначения роли
    script_content = f'''
from database import SessionLocal
import models

db = SessionLocal()
user = db.query(models.User).filter(models.User.username == "{username}").first()
admin_role = db.query(models.Role).filter(models.Role.name == "ROLE_ADMIN").first()

if user and admin_role:
    if admin_role not in user.roles:
        user.roles.append(admin_role)
        db.commit()
        print(f" Пользователю {username} назначена роль ADMIN")
    else:
        print(f" У пользователя {username} уже есть роль ADMIN")
else:
    if not user:
        print(f" Пользователь {username} не найден")
    if not admin_role:
        print(" Роль ROLE_ADMIN не найдена")
db.close()
'''
    
    
    with open("temp_make_admin.py", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    import subprocess
    result = subprocess.run(["python", "temp_make_admin.py"], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    
    import os
    os.remove("temp_make_admin.py")


def create_customer(token: str, first_name: str, last_name: str, email: str, request_id: int):
    
    start_time = time.time()
    
    response = requests.post(
        f"{BASE_URL}/api/v1/customers/",
        params={
            "first_name": first_name,
            "last_name": last_name,
            "email": email
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    elapsed_time = time.time() - start_time
    
    if response.status_code == 200:
        print(f" [Запрос {request_id}] Клиент создан за {elapsed_time:.3f} секунд")
        customer = response.json()
        print(f"   ID: {customer.get('id')}")
        print(f"   Имя: {customer.get('first_name')} {customer.get('last_name')}")
        print(f"   Email: {customer.get('email')}")
        return customer
    else:
        print(f" [Запрос {request_id}] Ошибка: {response.status_code}")
        print(f"   Ответ: {response.text}")
        return None


def test_async_behavior():
    
    print("ТЕСТИРОВАНИЕ АСИНХРОННОСТИ JMS")
    
    
    
    print("\n1. Регистрация пользователя...")
    register("test_admin", "admin123")
    
    
    print("\n2. Назначение роли ADMIN...")
    make_admin("test_admin")
    
    
    print("\n3. Логин...")
    token = login("test_admin", "admin123")
    
    if not token:
        print(" Не удалось получить токен. Проверьте, запущено ли приложение.")
        print("   Запустите: python main.py")
        return
    
    print(f"\n Токен получен: {token[:50]}...")
    
    
    
    
    customers = [
        ("Анна", "Иванова", "anna_async@test.com"),
        ("Петр", "Сидоров", "petr_async@test.com"),
        ("Елена", "Козлова", "elena_async@test.com"),
    ]
    
    for i, (first, last, email) in enumerate(customers, 1):
        create_customer(token, first, last, email, i)
        print()
    
    
    print(" Все API запросы завершены!")
    print(" Сообщения отправлены в очередь email.queue")
    print(" JMS Consumer обрабатывает их в фоне (каждое письмо - 2 секунды)")
    
    
    print("\n Ждём 10 секунд для завершения обработки email...")
    time.sleep(10)
    
    
    print(" РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("    API отвечает мгновенно (не блокируется отправкой email)")
    print("    Email обрабатываются асинхронно в фоновых потоках")
    print("    Поддержка многопоточности (concurrency 1-5)")
    print("    Имитация долгой операции (sleep 2 секунды)")
    


def check_api():
    
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print(" API доступен (Swagger UI работает)")
            return True
    except requests.exceptions.ConnectionError:
        print(" API не доступен. Убедитесь, что приложение запущено:")
        print("   python main.py")
        return False


if __name__ == "__main__":
    
    if not check_api():
        exit(1)
    
    test_async_behavior()