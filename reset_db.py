import psycopg2
from core.config import psycopg2_connect_kwargs


def reset_database():
    print("🧨 Начинаю очистку базы данных...")
    conn = None
    try:
        # Подключаемся
        conn = psycopg2.connect(**psycopg2_connect_kwargs())
        cur = conn.cursor()

        # Выполняем очистку
        cur.execute("TRUNCATE TABLE biorefinery_data_clean RESTART IDENTITY;")
        conn.commit()

        print("✅ УСПЕХ: База данных полностью очищена!")

    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()


if __name__ == "__main__":
    reset_database()