from datetime import date, datetime
from typing import Any

from src.domain.travel_package import TravelPackage
from src.persistence.database import get_connection, get_db_engine


class TravelPackageRepository:
    def _placeholder(self) -> str:
        return "?" if get_db_engine() == "sqlite" else "%s"

    def init_tables(self) -> None:
        engine = get_db_engine()
        conn = get_connection()
        try:
            cursor = conn.cursor()
            if engine == "sqlite":
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS travel_packages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        start_date TEXT NOT NULL,
                        end_date TEXT NOT NULL,
                        total_cost REAL NOT NULL,
                        active INTEGER NOT NULL DEFAULT 1
                    );
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS package_destinations (
                        package_id INTEGER NOT NULL,
                        destination_id INTEGER NOT NULL,
                        PRIMARY KEY (package_id, destination_id),
                        FOREIGN KEY (package_id) REFERENCES travel_packages(id) ON DELETE CASCADE,
                        FOREIGN KEY (destination_id) REFERENCES destinations(id)
                    );
                    """
                )
            else:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS travel_packages (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(120) NOT NULL,
                        start_date DATE NOT NULL,
                        end_date DATE NOT NULL,
                        total_cost DECIMAL(10, 2) NOT NULL,
                        active BOOLEAN NOT NULL DEFAULT TRUE
                    );
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS package_destinations (
                        package_id INT NOT NULL,
                        destination_id INT NOT NULL,
                        PRIMARY KEY (package_id, destination_id),
                        FOREIGN KEY (package_id) REFERENCES travel_packages(id) ON DELETE CASCADE,
                        FOREIGN KEY (destination_id) REFERENCES destinations(id)
                    );
                    """
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def _parse_date(value: Any) -> date:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        return date.fromisoformat(str(value))

    def _get_destination_ids(self, cursor: Any, package_id: int) -> list[int]:
        ph = self._placeholder()
        cursor.execute(
            f"""
            SELECT destination_id
            FROM package_destinations
            WHERE package_id = {ph}
            ORDER BY destination_id ASC
            """,
            (package_id,),
        )
        rows = cursor.fetchall()
        return [
            int(r["destination_id"] if isinstance(r, dict) else r[0]) for r in rows
        ]

    def create(self, package: TravelPackage) -> TravelPackage:
        ph = self._placeholder()
        active_val = 1 if package.active else 0
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                INSERT INTO travel_packages (name, start_date, end_date, total_cost, active)
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph})
                """,
                (
                    package.name.strip(),
                    package.start_date.isoformat(),
                    package.end_date.isoformat(),
                    package.total_cost,
                    active_val,
                ),
            )
            package.id = (
                int(cursor.lastrowid) if cursor.lastrowid is not None else None
            )
            if package.id is not None:
                for dest_id in package.destination_ids:
                    cursor.execute(
                        f"""
                        INSERT INTO package_destinations (package_id, destination_id)
                        VALUES ({ph}, {ph})
                        """,
                        (package.id, dest_id),
                    )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return package

    def get_all(self, only_available: bool = False) -> list[TravelPackage]:
        ph = self._placeholder()
        query = """
            SELECT id, name, start_date, end_date, total_cost, active
            FROM travel_packages
        """
        params: list[Any] = []
        if only_available:
            query += f" WHERE active = {ph} AND end_date >= {ph}"
            params.extend([1, date.today().isoformat()])
        query += " ORDER BY id ASC"

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()

            packages: list[TravelPackage] = []
            for row in rows:
                if isinstance(row, dict):
                    pkg_id = int(row["id"])
                    name = row["name"]
                    start_dt = self._parse_date(row["start_date"])
                    end_dt = self._parse_date(row["end_date"])
                    total = float(row["total_cost"])
                    is_active = bool(row["active"])
                else:
                    pkg_id = int(row[0])
                    name = row[1]
                    start_dt = self._parse_date(row[2])
                    end_dt = self._parse_date(row[3])
                    total = float(row[4])
                    is_active = bool(row[5])

                dest_ids = self._get_destination_ids(cursor, pkg_id)
                packages.append(
                    TravelPackage(
                        id=pkg_id,
                        name=name,
                        start_date=start_dt,
                        end_date=end_dt,
                        total_cost=total,
                        destination_ids=dest_ids,
                        active=is_active,
                    )
                )
        finally:
            conn.close()
        return packages

    def get_by_id(self, package_id: int) -> TravelPackage | None:
        ph = self._placeholder()
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT id, name, start_date, end_date, total_cost, active
                FROM travel_packages
                WHERE id = {ph}
                """,
                (package_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None

            if isinstance(row, dict):
                pkg_id = int(row["id"])
                name = row["name"]
                start_dt = self._parse_date(row["start_date"])
                end_dt = self._parse_date(row["end_date"])
                total = float(row["total_cost"])
                is_active = bool(row["active"])
            else:
                pkg_id = int(row[0])
                name = row[1]
                start_dt = self._parse_date(row[2])
                end_dt = self._parse_date(row[3])
                total = float(row[4])
                is_active = bool(row[5])

            dest_ids = self._get_destination_ids(cursor, pkg_id)
        finally:
            conn.close()

        return TravelPackage(
            id=pkg_id,
            name=name,
            start_date=start_dt,
            end_date=end_dt,
            total_cost=total,
            destination_ids=dest_ids,
            active=is_active,
        )

    def set_active_status(self, package_id: int, active: bool) -> None:
        ph = self._placeholder()
        active_val = 1 if active else 0
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE travel_packages SET active = {ph} WHERE id = {ph}",
                (active_val, package_id),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

