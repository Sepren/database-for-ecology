import psycopg2
from core.config import DB_CONFIG

def create_table():
    print("--- 🛠 Создание ПОЛНОЙ схемы БД (Все столбцы Excel) ---")

    commands = (
        """DROP TABLE IF EXISTS biorefinery_data_clean;""",

        """
        CREATE TABLE biorefinery_data_clean (
            id SERIAL PRIMARY KEY,

            -- 1. Основные (Core)
            title TEXT,                  -- Заголовок
            abstract TEXT,               -- Аннотация
            authors TEXT,                -- Авторы
            publication_year INTEGER,    -- Год
            url TEXT,                    -- Ссылка

            -- 2. WoodMind Аналитика (AI)
            method_raw TEXT,             -- Метод (исходный)
            method_normalized TEXT,      -- Метод (чистый)
            product_raw TEXT,            -- Продукты (исходный)
            product_normalized TEXT,     -- Продукты (чистый)
            trl_level INTEGER DEFAULT 0, -- TRL

            -- 3. Все остальные столбцы из Excel
            findings TEXT,               -- Выводы
            conclusion TEXT,             -- Заключение
            concept TEXT,                -- Концепция
            results TEXT,                -- Результаты
            content TEXT,                -- Содержание
            abbreviations TEXT,          -- Сокращения
            terms TEXT,                  -- Термины
            technology_raw TEXT,         -- Технология (как в excel)
            publication_type TEXT,       -- Тип публикации

            -- Служебные
            source_file TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        # Индексы для скорости
        """CREATE INDEX IF NOT EXISTS idx_method ON biorefinery_data_clean(method_normalized);""",
        """CREATE INDEX IF NOT EXISTS idx_product ON biorefinery_data_clean(product_normalized);"""
    )

    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        conn.commit()
        cur.close()
        print("✅ Таблица успешно расширена под все столбцы!")
    except Exception as error:
        print(f"❌ Ошибка БД: {error}")
    finally:
        if conn is not None: conn.close()


if __name__ == '__main__':
    create_table()