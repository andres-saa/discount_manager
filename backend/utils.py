"""Utilidades: IDs únicos, códigos de cupón."""
import random
import string
from datetime import datetime


def new_id(prefix: str = "id") -> str:
    """Genera un ID único con prefijo."""
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    r = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{prefix}_{ts}_{r}"


def new_user_code(length: int = 8) -> str:
    """Código alfanumérico para usuario de cuponera (sin ambigüedades 0/O, 1/I)."""
    chars = string.ascii_uppercase + string.digits
    # Evitar 0,O y 1,I,L
    chars = "".join(c for c in chars if c not in "0O1IL")
    return "".join(random.choices(chars, k=length))


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"
