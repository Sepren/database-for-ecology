import psycopg2
import pandas as pd
from psycopg2 import sql


def load_clean_data_from_db(table_name="biorefinery_data_clean"):
    """Устанавливает соединение с БД и загружает очищенные данные в DataFrame."""

    # --- !!! ЗАМЕНИТЕ ЭТИ ПАРАМЕТРЫ СВОИМИ ДАННЫМИ !!! ---
    DB_HOST = "127.0.0.1"
    DB_NAME = "diploma"
    DB_USER = "postgres"
    DB_PASSWORD = "RfVtlB-DevtY"
    DB_PORT = 5433
    # --------------x`--------------------------------------

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
    except psycopg2.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        # В случае ошибки возвращаем пустой DataFrame
        return pd.DataFrame()

    # 1. Создаем объект SQL для запроса
    query_object = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))

    # 2. !!! КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ !!!
    # Преобразуем объект запроса в простую строку, которую ожидает Pandas
    query_string = query_object.as_string(conn)

    # 3. Используем строку в read_sql
    df = pd.read_sql(query_string, conn)  # Используем query_string
    conn.close()
    return df


if __name__ == '__main__':
    # Тест подключения
    df_test = load_clean_data_from_db()
    if not df_test.empty:
        print(f"Успешно загружено строк: {len(df_test)}")
        print(df_test.head())