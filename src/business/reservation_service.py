from datetime import date

from src.domain.reservation import Reservation
from src.persistence.reservation_repository import ReservationRepository
from src.persistence.travel_package_repository import TravelPackageRepository
from src.persistence.user_repository import UserRepository


class ReservationService:
    def __init__(
        self,
        reservation_repo: ReservationRepository | None = None,
        user_repo: UserRepository | None = None,
        package_repo: TravelPackageRepository | None = None,
    ) -> None:
        self.reservation_repo = reservation_repo or ReservationRepository()
        self.user_repo = user_repo or UserRepository()
        self.package_repo = package_repo or TravelPackageRepository()
        self.reservation_repo.init_table()

    @staticmethod
    def _validate_positive_int(value: int, label: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{label} debe ser un número entero positivo.")
        return value

    def create_reservation(
        self, user_id: int, package_id: int, travelers_count: int
    ) -> Reservation:
        valid_user_id = self._validate_positive_int(user_id, "El ID de usuario")
        valid_package_id = self._validate_positive_int(package_id, "El ID del paquete")
        valid_travelers = self._validate_positive_int(
            travelers_count, "La cantidad de viajeros"
        )

        user = self.user_repo.get_by_id(valid_user_id)
        if not user or not user.active:
            raise LookupError("El usuario no existe o está inactivo.")

        package = self.package_repo.get_by_id(valid_package_id)
        if not package:
            raise LookupError("No se encontró el paquete turístico seleccionado.")
        if not package.active:
            raise ValueError("El paquete turístico seleccionado no está activo.")
        if package.end_date < date.today():
            raise ValueError(
                "El paquete turístico ya finalizó y no está disponible para reservar."
            )

        total_amount = Reservation.calculate_amount(
            package.total_cost, valid_travelers
        )
        reservation = Reservation(
            id=None,
            user_id=valid_user_id,
            package_id=valid_package_id,
            travelers_count=valid_travelers,
            total_amount=total_amount,
            status="CONFIRMED",
        )
        reservation.validate()
        return self.reservation_repo.create(reservation)

    def list_user_reservations(self, user_id: int) -> list[Reservation]:
        valid_user_id = self._validate_positive_int(user_id, "El ID de usuario")
        return self.reservation_repo.get_by_user(valid_user_id)

    def list_all_reservations(self) -> list[Reservation]:
        return self.reservation_repo.get_all()

    def cancel_reservation(
        self, reservation_id: int, requester_user_id: int | None = None
    ) -> Reservation:
        valid_id = self._validate_positive_int(reservation_id, "El ID de reserva")
        reservation = self.reservation_repo.get_by_id(valid_id)
        if not reservation:
            raise LookupError("No se encontró la reserva indicada.")

        if requester_user_id is not None:
            valid_requester = self._validate_positive_int(
                requester_user_id, "El ID de usuario"
            )
            if reservation.user_id != valid_requester:
                raise PermissionError(
                    "Solo el propietario de la reserva puede cancelarla."
                )

        reservation.cancel()
        self.reservation_repo.update_status(valid_id, reservation.status)
        return reservation
    
