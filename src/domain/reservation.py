from dataclasses import dataclass
from datetime import datetime


@dataclass
class Reservation:
    id: int | None
    user_id: int
    package_id: int
    travelers_count: int
    total_amount: float
    status: str = "CONFIRMED"
    created_at: str | None = None

    def validate(self) -> None:
        if isinstance(self.user_id, bool) or not isinstance(self.user_id, int) or self.user_id <= 0:
            raise ValueError("El ID de usuario debe ser un entero positivo.")

        if isinstance(self.package_id, bool) or not isinstance(self.package_id, int) or self.package_id <= 0:
            raise ValueError("El ID del paquete debe ser un entero positivo.")

        if (
            isinstance(self.travelers_count, bool)
            or not isinstance(self.travelers_count, int)
            or self.travelers_count <= 0
        ):
            raise ValueError("La cantidad de viajeros debe ser al menos 1.")

        if self.total_amount < 0:
            raise ValueError("El monto total de la reserva no puede ser negativo.")

        if self.status not in ("CONFIRMED", "CANCELLED"):
            raise ValueError("Estado de reserva no válido.")

        if not self.created_at:
            self.created_at = datetime.now().isoformat(timespec="seconds")

    @staticmethod
    def calculate_amount(unit_price: float, travelers_count: int) -> float:
        if unit_price < 0:
            raise ValueError("El precio del paquete no puede ser negativo.")
        if travelers_count <= 0:
            raise ValueError("La cantidad de viajeros debe ser al menos 1.")
        return round(float(unit_price) * travelers_count, 2)

    def cancel(self) -> None:
        if self.status == "CANCELLED":
            raise ValueError("La reserva ya se encuentra cancelada.")
        self.status = "CANCELLED"

