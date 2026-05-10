import pandas as pd
from sqlalchemy import create_engine
from core.config import sqlalchemy_database_url


class DBConnector:
    def get_engine(self):
        # Создаем строку подключения для SQLAlchemy
        # Формат: postgresql+psycopg2://user:password@host:port/dbname
        return create_engine(sqlalchemy_database_url())

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
