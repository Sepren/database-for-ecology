import pandas as pd
from sqlalchemy import create_engine
from core.config import DB_CONFIG


class DBConnector:
    def get_engine(self):
        # Создаем строку подключения для SQLAlchemy
        # Формат: postgresql+psycopg2://user:password@host:port/dbname
        url = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        return create_engine(url)

    def fetch_all(self, table_name):
        engine = self.get_engine()
        query = f"SELECT * FROM {table_name}"
        try:
            # Используем engine вместо сырого conn
            with engine.connect() as conn:
                df = pd.read_sql(query, conn)
            return df
        except Exception as e:
            print(f"Ошибка чтения БД: {e}")
            return pd.DataFrame()
