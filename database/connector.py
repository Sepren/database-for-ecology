import pandas as pd
from sqlalchemy import create_engine
from core.config import DB_CONFIG
import json
import time

DEBUG_LOG_PATH = "debug-8495ce.log"


def _agent_log(run_id, hypothesis_id, message, data):
    # #region agent log
    try:
        payload = {
            "sessionId": "8495ce",
            "runId": run_id,
            "hypothesisId": hypothesis_id,
            "location": "database/connector.py",
            "message": message,
            "data": data,
            "timestamp": int(time.time() * 1000),
        }
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as lf:
            lf.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass
    # #endregion

class DBConnector:
    def get_engine(self):
        # Создаем строку подключения для SQLAlchemy
        # Формат: postgresql+psycopg2://user:password@host:port/dbname
        _agent_log(
            "pre-fix",
            "H1",
            "building engine with DB config",
            {
                "host": DB_CONFIG.get("host"),
                "port": DB_CONFIG.get("port"),
                "database": DB_CONFIG.get("database"),
                "user": DB_CONFIG.get("user"),
                "password_set": bool(DB_CONFIG.get("password")),
            },
        )
        url = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        return create_engine(url)

    def fetch_all(self, table_name):
        engine = self.get_engine()
        query = f"SELECT * FROM {table_name}"
        try:
            _agent_log("pre-fix", "H2", "starting fetch_all", {"table_name": table_name})
            # Используем engine вместо сырого conn
            with engine.connect() as conn:
                df = pd.read_sql(query, conn)
            _agent_log("pre-fix", "H3", "fetch_all succeeded", {"rows": int(len(df))})
            return df
        except Exception as e:
            _agent_log(
                "pre-fix",
                "H4",
                "fetch_all failed",
                {"error_type": type(e).__name__, "error_text": str(e)[:500]},
            )
            print(f"Ошибка чтения БД: {e}")
            return pd.DataFrame()