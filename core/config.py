import os
from typing import Optional
from urllib.parse import parse_qs, quote, quote_plus, unquote, urlparse

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
    cfg = {
        "host": parsed.hostname,
        "database": dbname or "postgres",
        "user": unquote(parsed.username or ""),
        "password": unquote(parsed.password or ""),
        "port": parsed.port or 5432,
    }
    qs = parse_qs(parsed.query)
    if qs.get("sslmode"):
        cfg["sslmode"] = qs["sslmode"][0]
    return cfg


def _default_sslmode_for_host(host: str) -> Optional[str]:
    """Render Postgres requires TLS for external connections from your PC."""
    explicit = os.environ.get("POSTGRES_SSLMODE", "").strip()
    if explicit:
        return explicit if explicit.lower() != "disable" else None
    if host in ("127.0.0.1", "localhost", "::1"):
        return None
    if "render.com" in host:
        return "require"
    return None


def _apply_ssl_to_config(cfg: dict) -> dict:
    if "sslmode" in cfg:
        return cfg
    mode = _default_sslmode_for_host(cfg.get("host", ""))
    if mode:
        cfg = dict(cfg)
        cfg["sslmode"] = mode
    return cfg


def _build_db_config() -> dict:
    url = os.environ.get("DATABASE_URL") or os.environ.get("RENDER_DATABASE_URL")
    if url:
        cfg = _db_config_from_url(url)
    else:
        cfg = {
            "host": _env_str("POSTGRES_HOST", _env_str("DB_HOST", "127.0.0.1")),
            "database": _env_str("POSTGRES_DB", _env_str("DB_NAME", "diploma")),
            "user": _env_str("POSTGRES_USER", _env_str("DB_USER", "postgres")),
            "password": _env_str("POSTGRES_PASSWORD", _env_str("DB_PASSWORD", "postgres")),
            "port": _env_int("POSTGRES_PORT", _env_int("DB_PORT", 5432)),
        }
    return _apply_ssl_to_config(cfg)


DB_CONFIG = _build_db_config()


def psycopg2_connect_kwargs() -> dict:
    """Arguments for psycopg2.connect(**kwargs) including optional sslmode."""
    keys = ("host", "database", "user", "password", "port", "sslmode")
    return {k: DB_CONFIG[k] for k in keys if k in DB_CONFIG and DB_CONFIG[k] is not None}


def sqlalchemy_database_url() -> str:
    """SQLAlchemy connection URL with optional sslmode for managed Postgres (Render)."""
    user = quote_plus(str(DB_CONFIG.get("user", "")))
    pwd = quote_plus(str(DB_CONFIG.get("password", "")))
    host = DB_CONFIG["host"]
    port = DB_CONFIG["port"]
    db = quote(str(DB_CONFIG["database"]), safe="")
    base = f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"
    if DB_CONFIG.get("sslmode"):
        base += f"?sslmode={quote_plus(str(DB_CONFIG['sslmode']))}"
    return base


# Путь к локальному файлу (для режима без БД)
LOCAL_DATA_PATH = os.path.join("data", "merged_documents.xlsx")

# Настройки LLM (если будем использовать локальную)
MODEL_NAME = "google/flan-t5-large"