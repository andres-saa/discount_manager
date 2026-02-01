"""CRUD de usuarios de cuponera (registro y códigos)."""
import json
import os
from datetime import date

from fastapi import APIRouter, HTTPException

from models import CuponeraUser, CuponeraUserCreate, CuponeraUserUpdate
from storage import read_cuponeras
from utils import new_id, new_user_code, now_iso

from config import DATA_DIR

CUPONERA_USERS_JSON = os.path.join(DATA_DIR, "cuponera_users.json")


def _read_cuponera_users() -> list[dict]:
    if not os.path.exists(CUPONERA_USERS_JSON):
        return []
    with open(CUPONERA_USERS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_cuponera_users(data: list[dict]):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CUPONERA_USERS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


router = APIRouter(prefix="/cuponeras", tags=["cuponera-users"])


def _is_cuponera_vigent(cuponera: dict, today: str) -> bool:
    """Cuponera vigente = activa y hoy dentro de start_date..end_date."""
    if not cuponera.get("active"):
        return False
    start = (cuponera.get("start_date") or "").strip() or None
    end = (cuponera.get("end_date") or "").strip() or None
    if start and today < start:
        return False
    if end and today > end:
        return False
    return True


def _is_code_used_in_vigent_cuponera(code: str, exclude_user_id: str | None = None) -> bool:
    """True si el código ya está usado por otro usuario en una cuponera vigente."""
    code_upper = (code or "").strip().upper()
    if not code_upper:
        return False
    today = date.today().isoformat()
    users = _read_cuponera_users()
    cuponeras = {c["id"]: c for c in read_cuponeras() if c.get("id")}
    for u in users:
        if u.get("id") == exclude_user_id:
            continue
        if (u.get("code") or "").strip().upper() != code_upper:
            continue
        cuponera = cuponeras.get(u.get("cuponera_id") or "")
        if cuponera and _is_cuponera_vigent(cuponera, today):
            return True
    return False


@router.get("/{cuponera_id}/users", response_model=list[CuponeraUser])
def list_cuponera_users(cuponera_id: str):
    cuponeras = read_cuponeras()
    if not any(c.get("id") == cuponera_id for c in cuponeras):
        raise HTTPException(status_code=404, detail="Cuponera no encontrada")
    users = [u for u in _read_cuponera_users() if u.get("cuponera_id") == cuponera_id]
    return users


@router.post("/{cuponera_id}/users", response_model=CuponeraUser, status_code=201)
def register_cuponera_user(cuponera_id: str, body: CuponeraUserCreate):
    import phonenumbers
    
    cuponeras = read_cuponeras()
    if not any(c.get("id") == cuponera_id for c in cuponeras):
        raise HTTPException(status_code=404, detail="Cuponera no encontrada")
    if body.cuponera_id is not None and body.cuponera_id != cuponera_id:
        raise HTTPException(status_code=400, detail="cuponera_id no coincide")
    users = _read_cuponera_users()

    code_raw = (body.code or "").strip()
    if code_raw:
        code = code_raw.upper()
        if _is_code_used_in_vigent_cuponera(code):
            raise HTTPException(
                status_code=400,
                detail="Este código ya está en uso en una cuponera vigente. Use otro código o deje vacío para que el sistema genere uno.",
            )
    else:
        code = new_user_code(8)
        while _is_code_used_in_vigent_cuponera(code):
            code = new_user_code(8)

    user_id = new_id("usr")
    now = now_iso()

    first_name = (body.first_name or "").strip()
    last_name = (body.last_name or "").strip()
    if not first_name:
        raise HTTPException(status_code=400, detail="El nombre es obligatorio")
    if not last_name:
        raise HTTPException(status_code=400, detail="El apellido es obligatorio")

    full_name = f"{first_name} {last_name}".strip()

    # Código de país: normalizar (ej. "57" -> "+57")
    phone_code_raw = (body.phone_code or "+57").strip()
    if not phone_code_raw.startswith("+"):
        phone_code = f"+{phone_code_raw}" if phone_code_raw else "+57"
    else:
        phone_code = phone_code_raw or "+57"
    
    # Validar teléfono con código de país
    phone = (body.phone or "").strip()
    if phone:
        # Limpiar espacios y guiones
        phone_cleaned = phone.replace(' ', '').replace('-', '')
        if not phone_cleaned.isdigit():
            raise HTTPException(
                status_code=400,
                detail="El teléfono solo debe contener números (sin letras ni caracteres especiales)."
            )
        
        try:
            if phone_cleaned.startswith('+'):
                parsed = phonenumbers.parse(phone_cleaned, None)
            else:
                parsed = phonenumbers.parse(f"{phone_code}{phone_cleaned}", None)
            
            if not phonenumbers.is_valid_number(parsed):
                raise HTTPException(
                    status_code=400,
                    detail=f"Número de teléfono inválido para el código de país {phone_code}. Verifique que el número corresponda al país."
                )
            phone = phone_cleaned  # Usar solo dígitos
        except phonenumbers.NumberParseException:
            raise HTTPException(
                status_code=400,
                detail=f"Formato de teléfono inválido. Verifique que coincida con el código de país {phone_code}."
            )

    doc = {
        "id": user_id,
        "cuponera_id": cuponera_id,
        "code": code,
        "name": full_name,
        "first_name": first_name,
        "last_name": last_name,
        "phone": phone,
        "phone_code": phone_code,
        "email": (body.email or "").strip(),
        "address": (body.address or "").strip() or None,
        "created_at": now,
    }
    users.append(doc)
    _write_cuponera_users(users)
    return doc


@router.get("/{cuponera_id}/users/{user_id}", response_model=CuponeraUser)
def get_cuponera_user(cuponera_id: str, user_id: str):
    users = _read_cuponera_users()
    for u in users:
        if u.get("cuponera_id") == cuponera_id and u.get("id") == user_id:
            return u
    raise HTTPException(status_code=404, detail="Usuario no encontrado")


@router.patch("/{cuponera_id}/users/{user_id}", response_model=CuponeraUser)
def update_cuponera_user(cuponera_id: str, user_id: str, body: CuponeraUserUpdate):
    import phonenumbers
    
    cuponeras = read_cuponeras()
    if not any(c.get("id") == cuponera_id for c in cuponeras):
        raise HTTPException(status_code=404, detail="Cuponera no encontrada")
    users = _read_cuponera_users()
    index = None
    for i, u in enumerate(users):
        if u.get("cuponera_id") == cuponera_id and u.get("id") == user_id:
            index = i
            break
    if index is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    doc = users[index]

    # Código: validar duplicados si se cambia
    if body.code is not None:
        code_raw = (body.code or "").strip()
        if code_raw:
            code = code_raw.upper()
            if _is_code_used_in_vigent_cuponera(code, exclude_user_id=user_id):
                raise HTTPException(
                    status_code=400,
                    detail="Este código ya está en uso en una cuponera vigente.",
                )
            doc["code"] = code

    # Nombre: actualizar solo los campos enviados
    if body.first_name is not None or body.last_name is not None:
        first_name = (body.first_name or doc.get("first_name") or "").strip()
        last_name = (body.last_name or doc.get("last_name") or "").strip()
        if not first_name and not last_name:
            # Fallback desde name si no hay first/last en doc
            name_parts = (doc.get("name") or "").strip().split(None, 1)
            first_name = name_parts[0] if name_parts else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""
        doc["first_name"] = first_name
        doc["last_name"] = last_name
        doc["name"] = f"{first_name} {last_name}".strip()

    # Phone y phone_code: validar coherencia
    phone_updated = body.phone is not None
    phone_code_updated = body.phone_code is not None
    
    # Actualizar phone_code primero si se envía
    if phone_code_updated:
        phone_code_raw = (body.phone_code or "+57").strip()
        phone_code = f"+{phone_code_raw}" if phone_code_raw and not phone_code_raw.startswith("+") else (phone_code_raw or "+57")
        doc["phone_code"] = phone_code
    
    # Validar teléfono con código de país
    if phone_updated:
        phone = (body.phone or "").strip()
        if phone:
            # Limpiar espacios y guiones
            phone_cleaned = phone.replace(' ', '').replace('-', '')
            if not phone_cleaned.isdigit():
                raise HTTPException(
                    status_code=400,
                    detail="El teléfono solo debe contener números (sin letras ni caracteres especiales)."
                )
            
            current_phone_code = doc.get("phone_code") or "+57"
            # Intentar parsear el teléfono con el código de país actual
            try:
                # Si el teléfono ya tiene +, parsearlo directamente
                if phone_cleaned.startswith('+'):
                    parsed = phonenumbers.parse(phone_cleaned, None)
                else:
                    # Añadir código de país y parsear
                    parsed = phonenumbers.parse(f"{current_phone_code}{phone_cleaned}", None)
                
                if not phonenumbers.is_valid_number(parsed):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Número de teléfono inválido para el código de país {current_phone_code}. Verifique que el número corresponda al país."
                    )
                doc["phone"] = phone_cleaned
            except phonenumbers.NumberParseException:
                raise HTTPException(
                    status_code=400,
                    detail=f"Formato de teléfono inválido. Verifique que coincida con el código de país {current_phone_code}."
                )
        else:
            doc["phone"] = ""
    
    if body.email is not None:
        doc["email"] = (body.email or "").strip()
    if body.address is not None:
        val = (body.address or "").strip()
        doc["address"] = val if val else None

    _write_cuponera_users(users)
    return doc


@router.delete("/{cuponera_id}/users/{user_id}", status_code=204)
def delete_cuponera_user(cuponera_id: str, user_id: str):
    users = _read_cuponera_users()
    new_users = [u for u in users if not (u.get("cuponera_id") == cuponera_id and u.get("id") == user_id)]
    if len(new_users) == len(users):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    _write_cuponera_users(new_users)
