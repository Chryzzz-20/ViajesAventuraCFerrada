from typing import Any

from src.domain.user import User
from src.persistence.database import get_connection, get_db_engine


class UserRepository:
    def _placeholder(self) -> str:
        return "?" if get_db_engine() == "sqlite" else "%s"

    @staticmethod
    def _row_to_user(row: Any) -> User:
        if isinstance(row, dict):
            return User(
                id=int(row["id"]),
                full_name=row["full_name"],
                email=row["email"],
                password_hash=row["password_hash"],
                active=bool(row["active"]),
            )
        return User(
            id=int(row[0]),
            full_name=row[1],
            email=row[2],
            password_hash=row[3],
            active=bool(row[4]),
        )

    def init_table(self) -> None:
        engine = get_db_engine()
        conn = get_connection()
        try:
            cursor = conn.cursor()
            if engine == "sqlite":
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        full_name TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        password_hash TEXT NOT NULL,
                        active INTEGER NOT NULL DEFAULT 1
                    );
                    """
                )
            else:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        full_name VARCHAR(120) NOT NULL,
                        email VARCHAR(160) NOT NULL UNIQUE,
                        password_hash VARCHAR(255) NOT NULL,
                        active BOOLEAN NOT NULL DEFAULT TRUE
                    );
                    """
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def create(self, user: User) -> User:
        ph = self._placeholder()
        active_val = 1 if user.active else 0
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                INSERT INTO users (full_name, email, password_hash, active)
                VALUES ({ph}, {ph}, {ph}, {ph})
                """,
                (
                    user.full_name.strip(),
                    user.email.strip().lower(),
                    user.password_hash,
                    active_val,
                ),
            )
            conn.commit()
            user.id = (
                int(cursor.lastrowid) if cursor.lastrowid is not None else None
            )
        except Exception as exc:
            conn.rollback()
            if "unique" in str(exc).lower() or "duplicate" in str(exc).lower():
                raise ValueError(
                    "Ya existe una cuenta registrada con ese correo."
                ) from exc
            raise
        finally:
            conn.close()
        return user

    def get_by_email(self, email: str) -> User | None:
        ph = self._placeholder()
        clean_email = email.strip().lower()
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT id, full_name, email, password_hash, active
                FROM users
                WHERE email = {ph}
                """,
                (clean_email,),
            )
            row = cursor.fetchone()
        finally:
            conn.close()

        if not row:
            return None
        return self._row_to_user(row)

    def get_by_id(self, user_id: int) -> User | None:
        ph = self._placeholder()
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT id, full_name, email, password_hash, active
                FROM users
                WHERE id = {ph}
                """,
                (user_id,),
            )
            row = cursor.fetchone()
        finally:
            conn.close()

        if not row:
            return None
        return self._row_to_user(row)
    
