from dataclasses import dataclass
import re


@dataclass
class User:
    id: int | None
    full_name: str
    email: str
    password_hash: str
    active: bool = True

    def validate(self) -> None:
        if not self.full_name or not self.full_name.strip():
            raise ValueError("El nombre completo es obligatorio.")
        self.full_name = self.full_name.strip()

        clean_email = (self.email or "").strip().lower()
        if not clean_email or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", clean_email):
            raise ValueError("Debes ingresar un correo electrónico válido.")
        self.email = clean_email

        if not self.password_hash or not self.password_hash.strip():
            raise ValueError("El hash de contraseña no puede estar vacío.")
        
