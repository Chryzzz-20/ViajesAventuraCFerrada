import os
import sqlite3
from pathlib import Path


def get_db_engine() -> str:
    return os.getenv("DB_ENGINE", "sqlite").strip().lower()


def get_sqlite_connection() -> sqlite3.Connection:
    db_path = Path(os.getenv("DB_PATH", "data/viajes_aventura.sqlite3"))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def get_mysql_connection():
    try:
        import mysql.connector
    except ImportError as exc:
        raise RuntimeError(
            "Falta instalar 'mysql-connector-python' para usar MySQL."
        ) from exc

    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "viajes_aventura"),
    )


def get_connection():
    engine = get_db_engine()
    if engine == "sqlite":
        return get_sqlite_connection()
    if engine == "mysql":
        return get_mysql_connection()
    raise ValueError(f"Motor de base de datos no soportado: {engine}")

