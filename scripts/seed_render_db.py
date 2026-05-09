import os
import subprocess
import sys
from urllib.parse import urlparse


def _apply_database_url(env_var_name: str) -> bool:
    raw = os.environ.get(env_var_name)
    if not raw:
        return False

    parsed = urlparse(raw)
    if parsed.scheme not in ("postgres", "postgresql"):
        raise ValueError(f"{env_var_name} must start with postgres:// or postgresql://")

    if not parsed.hostname or not parsed.path:
        raise ValueError(f"{env_var_name} is missing host/database")

    os.environ["POSTGRES_HOST"] = parsed.hostname
    os.environ["POSTGRES_PORT"] = str(parsed.port or 5432)
    os.environ["POSTGRES_DB"] = parsed.path.lstrip("/")
    os.environ["POSTGRES_USER"] = parsed.username or ""
    os.environ["POSTGRES_PASSWORD"] = parsed.password or ""
    return True


def _ensure_postgres_env() -> None:
    if _apply_database_url("RENDER_DATABASE_URL"):
        return
    if _apply_database_url("DATABASE_URL"):
        return

    required = ["POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD"]
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise ValueError(
            "Missing DB settings. Set RENDER_DATABASE_URL (or DATABASE_URL), "
            "or explicitly set POSTGRES_HOST/PORT/DB/USER/PASSWORD."
        )


def _run_step(cmd: list[str]) -> None:
    print(f"-> {' '.join(cmd)}")
    subprocess.run(cmd, check=True, env=os.environ.copy())


def main() -> int:
    try:
        _ensure_postgres_env()
        print("Target DB:")
        print(f"  host={os.environ.get('POSTGRES_HOST')} port={os.environ.get('POSTGRES_PORT')}")
        print(f"  db={os.environ.get('POSTGRES_DB')} user={os.environ.get('POSTGRES_USER')}")

        _run_step([sys.executable, "database/db_init.py"])
        _run_step([sys.executable, "ingest_data.py"])
        print("Done: schema recreated and data ingested.")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
