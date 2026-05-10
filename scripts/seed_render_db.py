import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


def _normalize_database_url(raw: str) -> str:
    raw = (raw or "").strip().strip('"').strip("'")
    # PowerShellsometimes leaves odd whitespace or BOM.
    raw = raw.lstrip("\ufeff")
    low = raw.lower()
    if low.startswith("postgres://") or low.startswith("postgresql://"):
        return raw
    # user:pass@host:port/db形式 (без схемы)
    if "@" in raw and "/" in raw.split("@", maxsplit=1)[-1] and "://" not in raw.split("@", maxsplit=1)[0]:
        return "postgresql://" + raw
    return raw


def _apply_database_url(env_var_name: str) -> bool:
    raw = os.environ.get(env_var_name)
    if not raw:
        return False

    raw = _normalize_database_url(raw)
    os.environ[env_var_name] = raw

    parsed = urlparse(raw)
    if parsed.scheme not in ("postgres", "postgresql"):
        snippet = raw[:48] + ("…" if len(raw) > 48 else "")
        raise ValueError(
            f"{env_var_name} must use scheme postgres:// or postgresql:// "
            f"(got scheme={parsed.scheme!r}, start={snippet!r}). "
            'PowerShell: $env:RENDER_DATABASE_URL="postgresql://USER:PASS@HOST:5432/DB"'
        )

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
    env = os.environ.copy()
    project_root = str(Path(__file__).resolve().parent.parent)
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = project_root if not existing else f"{project_root}{os.pathsep}{existing}"
    subprocess.run(cmd, check=True, env=env)


def main() -> int:
    try:
        local_xlsx = Path("data/merged_documents.xlsx")
        if not local_xlsx.exists():
            raise FileNotFoundError(
                "Local dataset not found: data/merged_documents.xlsx. "
                "Run this script from repository root where the file exists."
            )

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
