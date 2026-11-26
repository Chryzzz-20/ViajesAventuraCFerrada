from dataclasses import dataclass


@dataclass
class Destination:
    id: int | None
    name: str
    country: str
    active: bool = True

    def validate(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("El nombre del destino es obligatorio.")
        if not self.country or not self.country.strip():
            raise ValueError("El país del destino es obligatorio.")
        
        self.name = self.name.strip()
        self.country = self.country.strip()

    def retire(self) -> None:
        self.active = False

