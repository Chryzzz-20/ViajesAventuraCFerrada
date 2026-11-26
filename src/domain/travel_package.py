from dataclasses import dataclass, field
from datetime import date


@dataclass
class TravelPackage:
    id: int | None
    name: str
    start_date: date
    end_date: date
    total_cost: float
    destination_ids: list[int] = field(default_factory=list)
    active: bool = True

    def validate(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("El nombre del paquete es obligatorio.")
        self.name = self.name.strip()

        if self.end_date < self.start_date:
            raise ValueError(
                "La fecha de término no puede ser anterior a la fecha de inicio."
            )

        if self.total_cost < 0:
            raise ValueError("El costo total del paquete no puede ser negativo.")

        if not self.destination_ids:
            raise ValueError(
                "Debes asociar al menos un destino al paquete turístico."
            )

    @staticmethod
    def calculate_cost_from_prices(prices: list[float]) -> float:
        if not prices:
            raise ValueError(
                "Se necesita al menos un costo de destino para calcular el paquete."
            )
        total = 0.0
        for price in prices:
            if price < 0:
                raise ValueError(
                    "El costo de un destino no puede ser negativo."
                )
            total += float(price)
        return round(total, 2)

    def deactivate(self) -> None:
        self.active = False

