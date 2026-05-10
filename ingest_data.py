import pandas as pd
import psycopg2
import sys
from psycopg2.extras import execute_values
from core.config import psycopg2_connect_kwargs
from agents.analyst_agent import AnalystAgent
import os
import re


# --- ФУНКЦИИ ОЧИСТКИ ---
def force_to_year(val):
    if pd.isna(val): return None
    match = re.search(r'\b(18|19|20)\d{2}\b', str(val))
    if match:
        y = int(match.group())
        if 1800 <= y <= 2030: return y
    return None


def force_to_trl(val):
    if pd.isna(val): return 0
    text = str(val)
    match = re.search(r'\b([1-9])\b', text)
    if match: return int(match.group(1))
    return 0


def run():
    print("--- 🚀 Ingestor: Full Column Mode ---")
    file_path = "data/merged_documents.xlsx"

    if not os.path.exists(file_path):
        print("Файл не найден")
        return

    try:
        print("⏳ Чтение Excel...")
        df = pd.read_excel(file_path, engine='openpyxl')

        # --- ПОЛНЫЙ МАППИНГ (Все твои столбцы) ---
        rename_map = {
            'Заголовок': 'title',
            'Аннотация': 'abstract',
            'Авторы': 'authors',
            'Год': 'publication_year',
            'Ссылка': 'url',

            'Метод': 'method_raw',
            'Продукты (ml)': 'product_raw',
            'TRL': 'trl_level',

            # Новые поля
            'Выводы': 'findings',
            'Заключение': 'conclusion',
            'Концепция': 'concept',
            'Результаты': 'results',
            'Содержание': 'content',
            'Сокращения': 'abbreviations',
            'Термины': 'terms',
            'Технология': 'technology_raw',
            'Тип публикации': 'publication_type'
        }

        # Переименовываем
        df = df.rename(columns=rename_map)
        df['source_file'] = 'merged_documents.xlsx'

        # Агент (Нормализация)
        print("🤖 Агент работает...")
        agent = AnalystAgent()
        df_clean, _ = agent.execute(df)

        # Очистка типов
        if 'publication_year' in df_clean.columns:
            df_clean['publication_year'] = df_clean['publication_year'].apply(force_to_year)
        if 'trl_level' in df_clean.columns:
            df_clean['trl_level'] = df_clean['trl_level'].apply(force_to_trl)

        # Подготовка к БД
        conn = psycopg2.connect(**psycopg2_connect_kwargs())
        cur = conn.cursor()

        # Список ВСЕХ колонок, которые мы создали в Шаге 1
        db_cols = [
            'title', 'abstract', 'authors', 'publication_year', 'url',
            'method_raw', 'method_normalized',
            'product_raw', 'product_normalized',
            'trl_level',
            'findings', 'conclusion', 'concept', 'results',
            'content', 'abbreviations', 'terms', 'technology_raw', 'publication_type',
            'source_file'
        ]

        # Создаем пустые, если нет в Excel
        for col in db_cols:
            if col not in df_clean.columns: df_clean[col] = None

        # NaN -> None
        df_final = df_clean[db_cols].astype(object).where(pd.notnull(df_clean[db_cols]), None)
        data_values = [tuple(x) for x in df_final.to_numpy()]

        print(f"🚀 Вставка {len(data_values)} строк со всеми столбцами...")
        query = f"INSERT INTO biorefinery_data_clean ({', '.join(db_cols)}) VALUES %s"
        batch = 2000
        for i in range(0, len(data_values), batch):
            chunk = data_values[i : i + batch]
            execute_values(cur, query, chunk)
        conn.commit()
        print("✅ УСПЕХ!")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals(): conn.close()


if __name__ == '__main__':
    run()