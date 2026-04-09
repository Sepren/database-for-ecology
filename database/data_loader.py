import pandas as pd
import psycopg2
import os
from config import DB_CONFIG, LOCAL_DATA_PATH
import warnings

# Игнорируем предупреждение Pandas о SQL (чтобы не засоряло консоль)
warnings.filterwarnings('ignore', category=UserWarning)


class DataLoader:
    def __init__(self):
        self.connection = None

    def connect_db(self):
        try:
            self.connection = psycopg2.connect(**DB_CONFIG)
            return True
        except Exception as e:
            # print(f"Ошибка БД: {e}")
            return False

    def normalize_columns(self, df):
        """
        Приводит заголовки к единому виду и ГАРАНТИРОВАННО удаляет дубликаты.
        """
        # 1. Нижний регистр и очистка пробелов
        df.columns = [str(c).lower().strip() for c in df.columns]

        # 2. Словарь перевода (Добавил вариации из вашего лога)
        rename_map = {
            'метод': 'method',
            'метод_ml': 'method',  # Важно!
            'метод (ml)': 'method',
            'methods': 'method',
            'technology': 'method',
            'технология': 'method',

            'продукт': 'product',
            'продукты': 'product',
            'продукты_ml': 'product',  # Важно!
            'продукты (ml)': 'product',
            'products': 'product',

            'trl': 'trl',
            'уровень готовности': 'trl',

            'год': 'year',
            'year': 'year',

            'аннотация': 'abstract',
            'abstract': 'abstract'
        }

        # 3. Переименовываем
        df.rename(columns=rename_map, inplace=True)

        # 4. УБИВАЕМ ДУБЛИКАТЫ (Самое важное место)
        # Если есть два столбца 'method', оставляем первый, остальные удаляем
        df = df.loc[:, ~df.columns.duplicated()]

        # Лог для проверки
        print(f"[DataLoader] Финальные колонки (без дублей): {list(df.columns)}")

        return df

    def load_data(self):
        df = pd.DataFrame()

        # Попытка 1: БД
        if self.connect_db():
            print("[DataLoader] Загрузка из PostgreSQL...")
            try:
                # ВНИМАНИЕ: Если используете pandas старой версии, engine='postgresql' не нужен,
                # но для new pandas лучше использовать SQLAlchemy.
                # Пока оставляем старый метод, он работает, просто ругается.
                query = "SELECT * FROM biorefinery_data LIMIT 500"
                df = pd.read_sql(query, self.connection)
                self.connection.close()
            except Exception as e:
                print(f"[DataLoader] Ошибка SQL: {e}")

        # Попытка 2: Локальный файл
        if df.empty:
            print(f"[DataLoader] Загрузка локального файла: {LOCAL_DATA_PATH}...")
            try:
                if os.path.exists(LOCAL_DATA_PATH):
                    if LOCAL_DATA_PATH.endswith('.csv'):
                        df = pd.read_csv(LOCAL_DATA_PATH)
                    else:
                        df = pd.read_excel(LOCAL_DATA_PATH)
                else:
                    print("[DataLoader] Файл не найден, создаю демо-данные.")
                    df = pd.DataFrame({
                        'method': ['гидролиз', 'пиролиз'],
                        'product': ['этанол', 'уголь'],
                        'trl': [5, 6]
                    })
            except Exception as e:
                print(f"[DataLoader] Ошибка чтения файла: {e}")
                return pd.DataFrame()

        # Нормализация (если данные есть)
        if not df.empty:
            df = self.normalize_columns(df)

        return df