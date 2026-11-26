import hashlib
import hmac
import secrets

from src.domain.user import User
from src.persistence.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repo: UserRepository | None = None) -> None:
        self.user_repo = user_repo or UserRepository()
        self.user_repo.init_table()

    @staticmethod
    def _validate_raw_password(password: str) -> None:
        if not isinstance(password, str) or len(password.strip()) < 8:
            raise ValueError(
                "La contraseña debe tener al menos 8 caracteres útiles."
            )

    @staticmethod
    def hash_password(password: str) -> str:
        AuthService._validate_raw_password(password)
        salt = secrets.token_hex(16)
        iterations = 100_000
        derived = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
        )
        return f"pbkdf2_sha256${iterations}${salt}${derived.hex()}"

    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        try:
            algorithm, iter_str, salt, expected_hex = stored_hash.split("$", 3)
            if algorithm != "pbkdf2_sha256":
                return False
            iterations = int(iter_str)
            computed = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt.encode("utf-8"),
                iterations,
            )
            return hmac.compare_digest(computed.hex(), expected_hex)
        except Exception:
            return False

    def register(self, full_name: str, email: str, password: str) -> User:
        clean_email = (email or "").strip().lower()
        existing = self.user_repo.get_by_email(clean_email)
        if existing:
            raise ValueError("Ya existe una cuenta registrada con ese correo.")

        password_hash = self.hash_password(password)
        user = User(
            id=None,
            full_name=full_name,
            email=clean_email,
            password_hash=password_hash,
            active=True,
        )
        user.validate()
        return self.user_repo.create(user)

    def login(self, email: str, password: str) -> User:
        clean_email = (email or "").strip().lower()
        if not clean_email or not password:
            raise ValueError("Debes ingresar correo y contraseña.")

        user = self.user_repo.get_by_email(clean_email)
        if not user or not user.active:
            raise LookupError("Credenciales inválidas o cuenta inactiva.")

        if not self.verify_password(password, user.password_hash):
            raise LookupError("Credenciales inválidas o cuenta inactiva.")

        return user
    
