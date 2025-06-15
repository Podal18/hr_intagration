from db.db import get_connection
from utils.logger import log_action
from datetime import datetime


def reset_password(login, new_password_hash):  # Принимаем уже хэшированный пароль
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE login = %s", (login,))
            user = cursor.fetchone()
            if not user:
                return False, "Пользователь не найден"

            user_id = user['id']
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            log_action(
                user_id=user_id,
                action="Сброс пароля",
                description=f"Пользователь {login} сбросил пароль",
                timestamp=timestamp
            )

            cursor.execute("""
                UPDATE users 
                SET password_hash = %s 
                WHERE login = %s
            """, (new_password_hash, login))  # Сохраняем хэш
            connection.commit()
            return True, "Пароль успешно изменён"
    except Exception as e:
        connection.rollback()
        return False, f"Ошибка: {str(e)}"
    finally:
        connection.close()

def register_user(login, password_hash, role_id, full_name):  # Принимаем хэш пароля
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE login = %s", (login,))
            if cursor.fetchone():
                return False, "Логин уже занят"

            # Сохраняем хэш пароля
            cursor.execute("""
                INSERT INTO users (login, password_hash, role)
                VALUES (%s, %s, %s)
            """, (login, password_hash, role_id))
            user_id = cursor.lastrowid

            if role_id in (2, 3):
                if not full_name:
                    full_name = "Не указано"

                cursor.execute("""
                    INSERT INTO employees (user_id, full_name)
                    VALUES (%s, %s)
                """, (user_id, full_name))

            connection.commit()
            return True, "Регистрация успешна"
    except Exception as e:
        connection.rollback()
        return False, f"Ошибка базы данных: {str(e)}"
    finally:
        connection.close()


def register_user(login, password, role_id, full_name):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Проверка логина
            cursor.execute("SELECT id FROM users WHERE login = %s", (login,))
            if cursor.fetchone():
                print(f"[DEBUG] Логин {login} уже занят")
                return False, "Логин уже занят"

            # Вставка пользователя
            cursor.execute("""
                INSERT INTO users (login, password_hash, role)
                VALUES (%s, %s, %s)
            """, (login, password, role_id))
            user_id = cursor.lastrowid

            # Для сотрудников создаём запись в employees
            if role_id in (2, 3):  # Employee или HR
                if not full_name:
                    full_name = "Не указано"

                cursor.execute("""
                    INSERT INTO employees (user_id, full_name)
                    VALUES (%s, %s)
                """, (user_id, full_name))

            connection.commit()  # Критически важно!
            print(f"[DEBUG] Пользователь {login} успешно создан, ID: {user_id}")
            return True, "Регистрация успешна"

    except Exception as e:
        connection.rollback()
        print(f"[ERROR] Ошибка регистрации: {str(e)}")
        return False, f"Ошибка базы данных: {str(e)}"
    finally:
        connection.close()
