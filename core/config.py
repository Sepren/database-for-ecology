import os
from urllib.parse import unquote, urlparse

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# PostgreSQL: приоритет переменных окружения (Docker, .env), без хранения паролей в репозитории.
# Render / Railway часто задают DATABASE_URL при привязке Postgres к Web Service.


def _env_str(name: str, default: str) -> str:
    return os.environ.get(name, default)


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    return int(raw)


def _db_config_from_url(url: str) -> dict:
    raw = url.strip()
    if raw.startswith("postgres://"):
        raw = "postgresql://" + raw[len("postgres://") :]
    parsed = urlparse(raw)
    if not parsed.hostname:
        raise ValueError("DATABASE_URL is missing hostname")
    dbname = (parsed.path or "/").lstrip("/").split("?")[0]
    return {
        "host": parsed.hostname,
        "database": dbname or "postgres",
        "user": unquote(parsed.username or ""),
        "password": unquote(parsed.password or ""),
        "port": parsed.port or 5432,
    }


def _build_db_config() -> dict:
    url = os.environ.get("DATABASE_URL") or os.environ.get("RENDER_DATABASE_URL")
    if url:
        return _db_config_from_url(url)
    return {
        "host": _env_str("POSTGRES_HOST", _env_str("DB_HOST", "127.0.0.1")),
        "database": _env_str("POSTGRES_DB", _env_str("DB_NAME", "diploma")),
        "user": _env_str("POSTGRES_USER", _env_str("DB_USER", "postgres")),
        "password": _env_str("POSTGRES_PASSWORD", _env_str("DB_PASSWORD", "postgres")),
        "port": _env_int("POSTGRES_PORT", _env_int("DB_PORT", 5432)),
    }


DB_CONFIG = _build_db_config()

# Путь к локальному файлу (для режима без БД)
LOCAL_DATA_PATH = os.path.join("data", "merged_documents.xlsx")

# Настройки LLM (если будем использовать локальную)
MODEL_NAME = "google/flan-t5-large"