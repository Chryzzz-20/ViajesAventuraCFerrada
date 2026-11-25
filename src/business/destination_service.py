from src.domain.destination import Destination
from src.persistence.destination_repository import DestinationRepository


class DestinationService:
    def __init__(self, repository: DestinationRepository | None = None) -> None:
        self.repository = repository or DestinationRepository()
        self.repository.init_table()

    def create_destination(self, name: str, country: str) -> Destination:
        destination = Destination(id=None, name=name, country=country, active=True)
        destination.validate()
        return self.repository.create(destination)

    def list_destinations(self, only_active: bool = False) -> list[Destination]:
        return self.repository.get_all(only_active=only_active)

    def update_destination(
        self, destination_id: int, name: str, country: str
    ) -> Destination:
        existing = self.repository.get_by_id(destination_id)
        if not existing:
            raise LookupError("No se encontró un destino con ese ID.")
        existing.name = name
        existing.country = country
        existing.validate()
        self.repository.update(existing)
        return existing

    def retire_or_delete_destination(
        self, destination_id: int, has_associated_trips: bool = False
    ) -> str:
        existing = self.repository.get_by_id(destination_id)
        if not existing:
            raise LookupError("No se encontró un destino con ese ID.")

        if has_associated_trips:
            existing.retire()
            self.repository.update(existing)
            return "Destino retirado para nuevos viajes; se conserva su historial."

        self.repository.delete_hard(destination_id)
        return "Destino eliminado correctamente."
    
    