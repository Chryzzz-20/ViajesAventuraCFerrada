from src.domain.destination import Destination
from src.persistence.database import get_connection, get_db_engine


class DestinationRepository:
    def _placeholder(self) -> str:
        return "?" if get_db_engine() == "sqlite" else "%s"

    def init_table(self) -> None:
        engine = get_db_engine()
        with get_connection() as conn:
            cursor = conn.cursor()
            if engine == "sqlite":
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS destinations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        country TEXT NOT NULL,
                        active INTEGER NOT NULL DEFAULT 1
                    );
                    """
                )
            else:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS destinations (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(120) NOT NULL,
                        country VARCHAR(120) NOT NULL,
                        active BOOLEAN NOT NULL DEFAULT TRUE
                    );
                    """
                )
            conn.commit()

    def create(self, destination: Destination) -> Destination:
        ph = self._placeholder()
        active_val = 1 if destination.active else 0
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"INSERT INTO destinations (name, country, active) VALUES ({ph}, {ph}, {ph})",
                (destination.name.strip(), destination.country.strip(), active_val),
            )
            conn.commit()
            destination.id = cursor.lastrowid
        return destination

    def get_all(self, only_active: bool = False) -> list[Destination]:
        ph = self._placeholder()
        query = "SELECT id, name, country, active FROM destinations"
        params: tuple = ()
        if only_active:
            query += f" WHERE active = {ph}"
            params = (1,)
        query += " ORDER BY id ASC"

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

        result: list[Destination] = []
        for row in rows:
            if isinstance(row, dict):
                result.append(
                    Destination(
                        id=row["id"],
                        name=row["name"],
                        country=row["country"],
                        active=bool(row["active"]),
                    )
                )
            else:
                result.append(
                    Destination(
                        id=row[0],
                        name=row[1],
                        country=row[2],
                        active=bool(row[3]),
                    )
                )
        return result

    def get_by_id(self, destination_id: int) -> Destination | None:
        ph = self._placeholder()
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT id, name, country, active FROM destinations WHERE id = {ph}",
                (destination_id,),
            )
            row = cursor.fetchone()

        if not row:
            return None
        if isinstance(row, dict):
            return Destination(
                id=row["id"],
                name=row["name"],
                country=row["country"],
                active=bool(row["active"]),
            )
        return Destination(
            id=row[0],
            name=row[1],
            country=row[2],
            active=bool(row[3]),
        )

    def update(self, destination: Destination) -> None:
        if destination.id is None:
            raise ValueError("El destino necesita un ID para actualizarse.")
        ph = self._placeholder()
        active_val = 1 if destination.active else 0
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE destinations SET name = {ph}, country = {ph}, active = {ph} WHERE id = {ph}",
                (
                    destination.name.strip(),
                    destination.country.strip(),
                    active_val,
                    destination.id,
                ),
            )
            conn.commit()

    def delete_hard(self, destination_id: int) -> None:
        ph = self._placeholder()
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"DELETE FROM destinations WHERE id = {ph}",
                (destination_id,),
            )
            conn.commit()

            