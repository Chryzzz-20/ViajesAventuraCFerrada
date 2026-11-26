from src.domain.destination import Destination
from src.persistence.destination_repository import DestinationRepository


class DestinationService:
    def __init__(self, repository: DestinationRepository | None = None) -> None:
        self.repository = repository or DestinationRepository()
        self.repository.init_table()

    @staticmethod
    def _validate_id(destination_id: int) -> int:
        if isinstance(destination_id, bool) or not isinstance(destination_id, int) or destination_id <= 0:
            raise ValueError("El ID del destino debe ser un número entero positivo.")
        return destination_id

    @staticmethod
    def _normalize_text(value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("El texto ingresado debe ser una cadena válida.")
        return value.strip()

    def create_destination(self, name: str, country: str) -> Destination:
        clean_name = self._normalize_text(name)
        clean_country = self._normalize_text(country)

        destination = Destination(
            id=None,
            name=clean_name,
            country=clean_country,
            active=True,
        )
        destination.validate()
        return self.repository.create(destination)

    def get_destination_by_id(self, destination_id: int) -> Destination:
        valid_id = self._validate_id(destination_id)
        existing = self.repository.get_by_id(valid_id)
        if not existing:
            raise LookupError("No se encontró un destino con ese ID.")
        return existing

    def list_destinations(self, only_active: bool = False) -> list[Destination]:
        return self.repository.get_all(only_active=only_active)

    def update_destination(
        self, destination_id: int, name: str, country: str
    ) -> Destination:
        existing = self.get_destination_by_id(destination_id)
        existing.name = self._normalize_text(name)
        existing.country = self._normalize_text(country)
        existing.validate()
        self.repository.update(existing)
        return existing

    def retire_or_delete_destination(
        self, destination_id: int, has_associated_trips: bool = False
    ) -> str:
        existing = self.get_destination_by_id(destination_id)

        if has_associated_trips:
            existing.retire()
            self.repository.update(existing)
            return "Destino retirado para nuevos viajes; se conserva su historial."

        self.repository.delete_hard(existing.id if existing.id is not None else destination_id)
        return "Destino eliminado correctamente." 
    