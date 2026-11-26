from datetime import date

from src.domain.travel_package import TravelPackage
from src.persistence.destination_repository import DestinationRepository
from src.persistence.travel_package_repository import TravelPackageRepository


class TravelPackageService:
    def __init__(
        self,
        package_repo: TravelPackageRepository | None = None,
        destination_repo: DestinationRepository | None = None,
    ) -> None:
        self.package_repo = package_repo or TravelPackageRepository()
        self.destination_repo = destination_repo or DestinationRepository()
        self.package_repo.init_tables()

    @staticmethod
    def _parse_iso_date(raw_date: str, field_label: str) -> date:
        try:
            return date.fromisoformat(raw_date.strip())
        except ValueError as exc:
            raise ValueError(
                f"La fecha de {field_label} debe tener formato AAAA-MM-DD."
            ) from exc

    def create_package(
        self,
        name: str,
        start_date_str: str,
        end_date_str: str,
        destination_ids: list[int],
        destination_costs: list[float] | None = None,
    ) -> TravelPackage:
        start_dt = self._parse_iso_date(start_date_str, "inicio")
        end_dt = self._parse_iso_date(end_date_str, "término")

        if not destination_ids:
            raise ValueError("Debes seleccionar al menos un destino.")

        unique_ids: list[int] = []
        for dest_id in destination_ids:
            if (
                isinstance(dest_id, bool)
                or not isinstance(dest_id, int)
                or dest_id <= 0
            ):
                raise ValueError("Cada ID de destino debe ser un entero positivo.")
            dest = self.destination_repo.get_by_id(dest_id)
            if not dest:
                raise LookupError(f"No existe un destino con ID {dest_id}.")
            if not dest.active:
                raise ValueError(
                    f"El destino '{dest.name}' está retirado y no puede agregarse a nuevos paquetes."
                )
            if dest_id not in unique_ids:
                unique_ids.append(dest_id)

        if destination_costs is not None:
            if len(destination_costs) != len(unique_ids):
                raise ValueError(
                    "La cantidad de costos debe coincidir con los destinos seleccionados."
                )
            total_cost = TravelPackage.calculate_cost_from_prices(destination_costs)
        else:
            total_cost = TravelPackage.calculate_cost_from_prices(
                [100.0 for _ in unique_ids]
            )

        package = TravelPackage(
            id=None,
            name=name,
            start_date=start_dt,
            end_date=end_dt,
            total_cost=total_cost,
            destination_ids=unique_ids,
            active=True,
        )
        package.validate()
        return self.package_repo.create(package)

    def list_packages(self, only_available: bool = False) -> list[TravelPackage]:
        return self.package_repo.get_all(only_available=only_available)

    def get_package_by_id(self, package_id: int) -> TravelPackage:
        if (
            isinstance(package_id, bool)
            or not isinstance(package_id, int)
            or package_id <= 0
        ):
            raise ValueError("El ID del paquete debe ser un entero positivo.")
        pkg = self.package_repo.get_by_id(package_id)
        if not pkg:
            raise LookupError("No se encontró un paquete turístico con ese ID.")
        return pkg

    def deactivate_package(self, package_id: int) -> TravelPackage:
        pkg = self.get_package_by_id(package_id)
        pkg.deactivate()
        self.package_repo.set_active_status(package_id, active=False)
        return pkg
    
