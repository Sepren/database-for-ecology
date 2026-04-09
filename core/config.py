import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# PostgreSQL: приоритет переменных окружения (Docker, .env), без хранения паролей в репозитории.


def _env_str(name: str, default: str) -> str:
    return os.environ.get(name, default)


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    return int(raw)


DB_CONFIG = {
    "host": _env_str("POSTGRES_HOST", _env_str("DB_HOST", "127.0.0.1")),
    "database": _env_str("POSTGRES_DB", _env_str("DB_NAME", "diploma")),
    "user": _env_str("POSTGRES_USER", _env_str("DB_USER", "postgres")),
    "password": _env_str("POSTGRES_PASSWORD", _env_str("DB_PASSWORD", "postgres")),
    "port": _env_int("POSTGRES_PORT", _env_int("DB_PORT", 5432)),
}

# Путь к локальному файлу (для режима без БД)
LOCAL_DATA_PATH = os.path.join("data", "merged_documents.xlsx")

# Настройки LLM (если будем использовать локальную)
MODEL_NAME = "google/flan-t5-large"