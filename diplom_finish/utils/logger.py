from db.db import get_connection
from datetime import datetime


def log_action(user_id, action, description, timestamp):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO logs (user_id, action, description, created_at)
                VALUES (%s, %s, %s, %s)
            """, (user_id, action, description, timestamp))
            connection.commit()
    except Exception as e:
        print(f"[LOGGING ERROR]: {e}")
    finally:
        connection.close()