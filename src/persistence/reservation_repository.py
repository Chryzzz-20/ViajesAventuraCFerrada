from typing import Any

from src.domain.reservation import Reservation
from src.persistence.database import get_connection, get_db_engine


class ReservationRepository:
    def _placeholder(self) -> str:
        return "?" if get_db_engine() == "sqlite" else "%s"

    @staticmethod
    def _row_to_reservation(row: Any) -> Reservation:
        if isinstance(row, dict):
            return Reservation(
                id=int(row["id"]),
                user_id=int(row["user_id"]),
                package_id=int(row["package_id"]),
                travelers_count=int(row["travelers_count"]),
                total_amount=float(row["total_amount"]),
                status=str(row["status"]),
                created_at=str(row["created_at"]) if row.get("created_at") is not None else None,
            )
        return Reservation(
            id=int(row[0]),
            user_id=int(row[1]),
            package_id=int(row[2]),
            travelers_count=int(row[3]),
            total_amount=float(row[4]),
            status=str(row[5]),
            created_at=str(row[6]) if row[6] is not None else None,
        )

    def init_table(self) -> None:
        engine = get_db_engine()
        conn = get_connection()
        try:
            cursor = conn.cursor()
            if engine == "sqlite":
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS reservations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        package_id INTEGER NOT NULL,
                        travelers_count INTEGER NOT NULL,
                        total_amount REAL NOT NULL,
                        status TEXT NOT NULL DEFAULT 'CONFIRMED',
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (package_id) REFERENCES travel_packages(id)
                    );
                    """
                )
            else:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS reservations (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        package_id INT NOT NULL,
                        travelers_count INT NOT NULL,
                        total_amount DECIMAL(10, 2) NOT NULL,
                        status VARCHAR(20) NOT NULL DEFAULT 'CONFIRMED',
                        created_at VARCHAR(40) NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (package_id) REFERENCES travel_packages(id)
                    );
                    """
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def create(self, reservation: Reservation) -> Reservation:
        ph = self._placeholder()
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                INSERT INTO reservations
                    (user_id, package_id, travelers_count, total_amount, status, created_at)
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})
                """,
                (
                    reservation.user_id,
                    reservation.package_id,
                    reservation.travelers_count,
                    reservation.total_amount,
                    reservation.status,
                    reservation.created_at,
                ),
            )
            conn.commit()
            reservation.id = (
                int(cursor.lastrowid) if cursor.lastrowid is not None else None
            )
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return reservation

    def get_by_id(self, reservation_id: int) -> Reservation | None:
        ph = self._placeholder()
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT id, user_id, package_id, travelers_count, total_amount, status, created_at
                FROM reservations
                WHERE id = {ph}
                """,
                (reservation_id,),
            )
            row = cursor.fetchone()
        finally:
            conn.close()

        if not row:
            return None
        return self._row_to_reservation(row)

    def get_by_user(self, user_id: int) -> list[Reservation]:
        ph = self._placeholder()
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT id, user_id, package_id, travelers_count, total_amount, status, created_at
                FROM reservations
                WHERE user_id = {ph}
                ORDER BY id DESC
                """,
                (user_id,),
            )
            rows = cursor.fetchall()
        finally:
            conn.close()

        return [self._row_to_reservation(row) for row in rows]

    def get_all(self) -> list[Reservation]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, user_id, package_id, travelers_count, total_amount, status, created_at
                FROM reservations
                ORDER BY id DESC
                """
            )
            rows = cursor.fetchall()
        finally:
            conn.close()

        return [self._row_to_reservation(row) for row in rows]

    def update_status(self, reservation_id: int, status: str) -> None:
        ph = self._placeholder()
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE reservations SET status = {ph} WHERE id = {ph}",
                (status, reservation_id),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

