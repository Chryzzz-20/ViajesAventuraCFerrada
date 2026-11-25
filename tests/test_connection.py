from src.persistence.database import get_connection, get_db_engine


def main() -> None:
    engine = get_db_engine()
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            if engine == "sqlite":
                cursor.execute("SELECT sqlite_version();")
                version = cursor.fetchone()[0]
                cursor.execute("PRAGMA foreign_keys;")
                fk_status = cursor.fetchone()[0]
                print(
                    f"Conexión exitosa a SQLite (versión {version}, foreign_keys={fk_status})."
                )
            else:
                cursor.execute("SELECT VERSION();")
                version = cursor.fetchone()[0]
                print(f"Conexión exitosa a MySQL (versión {version}).")
    except Exception as exc:
        print(f"Error al conectar con {engine}: {exc}")
        raise


if __name__ == "__main__":
    main()

    