import os
import sqlite3
from pathlib import Path
from typing import Any


def _load_env_file(env_path: Path = Path(".env")) -> None:
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_env_file()


def get_db_engine() -> str:
    return os.getenv("DB_ENGINE", "sqlite").strip().lower()


def get_sqlite_connection() -> sqlite3.Connection:
    db_path = Path(os.getenv("DB_PATH", "data/viajes_aventura.sqlite3"))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def get_mysql_connection() -> Any:
    try:
        import mysql.connector
    except ImportError as exc:
        raise RuntimeError(
            "Falta instalar 'mysql-connector-python' para usar MySQL."
        ) from exc

    raw_port = os.getenv("MYSQL_PORT", "3306").strip()
    try:
        port = int(raw_port)
    except ValueError as exc:
        raise ValueError(
            f"Puerto de MySQL inválido en MYSQL_PORT: '{raw_port}'."
        ) from exc

    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=port,
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "viajes_aventura"),
    )


def get_connection() -> Any:
    engine = get_db_engine()
    if engine == "sqlite":
        return get_sqlite_connection()
    if engine == "mysql":
        return get_mysql_connection()
    raise ValueError(f"Motor de base de datos no soportado: {engine}")

