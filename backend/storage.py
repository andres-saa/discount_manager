"""Almacenamiento en archivos JSON locales."""
import json
import os
from pathlib import Path

from config import (
    CUPONERA_USAGE_JSON,
    CUPONERA_USERS_JSON,
    CUPONERAS_JSON,
    DISCOUNTS_JSON,
    FOLDERS_JSON,
    MENUS_DIR,
    SITES_JSON,
)


def _ensure_dir(path: str):
    """Crea directorio si no existe."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def _load_json(path: str, default):
    """Carga JSON desde archivo. Retorna default si no existe o está vacío."""
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if data is not None else default
    except (json.JSONDecodeError, OSError):
        return default


def _save_json(path: str, data):
    """Guarda datos en JSON."""
    _ensure_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# --- Sites ---
def _site_allowed(s: dict) -> bool:
    if s.get("site_id") == 32:
        return False
    if (s.get("time_zone") or "") != "America/Bogota":
        return False
    return s.get("show_on_web") is True


def read_sites() -> list[dict]:
    data = _load_json(SITES_JSON, [])
    return data if isinstance(data, list) else []


def read_sites_filtered() -> list[dict]:
    """Sedes filtradas: solo time_zone America/Bogota, sin site_id 32."""
    return [s for s in read_sites() if _site_allowed(s)]


def write_sites(data: list[dict]):
    _save_json(SITES_JSON, data if data else [])


# --- Menus (por sede) ---
def _menu_path(site_id: int) -> str:
    return os.path.join(MENUS_DIR, f"site_{site_id}.json")


def read_menu(site_id: int) -> dict | None:
    path = _menu_path(site_id)
    data = _load_json(path, None)
    if data is None or not isinstance(data, dict):
        return None
    return data


def write_menu(site_id: int, data: dict):
    data_with_site = {**data, "site_id": site_id}
    Path(MENUS_DIR).mkdir(parents=True, exist_ok=True)
    _save_json(_menu_path(site_id), data_with_site)


def list_menu_site_ids() -> list[int]:
    ids = []
    if not os.path.isdir(MENUS_DIR):
        return ids
    for name in os.listdir(MENUS_DIR):
        if name.startswith("site_") and name.endswith(".json"):
            try:
                sid = int(name[5:-5])
                ids.append(sid)
            except ValueError:
                pass
    return ids


# --- Discounts ---
def _read_discounts_list() -> list[dict]:
    data = _load_json(DISCOUNTS_JSON, [])
    return data if isinstance(data, list) else []


def read_discounts() -> list[dict]:
    return _read_discounts_list()


def get_discount(discount_id: str) -> dict | None:
    for d in _read_discounts_list():
        if d.get("id") == discount_id:
            return d
    return None


def insert_discount(doc: dict) -> dict:
    items = _read_discounts_list()
    items.append(doc)
    _save_json(DISCOUNTS_JSON, items)
    return doc


def update_discount(discount_id: str, upd: dict) -> dict | None:
    items = _read_discounts_list()
    for i, d in enumerate(items):
        if d.get("id") == discount_id:
            items[i] = {**d, **upd}
            _save_json(DISCOUNTS_JSON, items)
            return items[i]
    return None


def delete_discount(discount_id: str) -> bool:
    items = _read_discounts_list()
    new_items = [d for d in items if d.get("id") != discount_id]
    if len(new_items) == len(items):
        return False
    _save_json(DISCOUNTS_JSON, new_items)
    _remove_discount_from_cuponera_calendars(discount_id)
    return True


def _remove_discount_from_cuponera_calendars(discount_id: str) -> int:
    """Quita discount_id de todos los calendarios de cuponeras."""
    cuponeras = read_cuponeras()
    modified = 0
    for c in cuponeras:
        cal = c.get("calendar") or {}
        new_cal = {}
        changed = False
        for date_key, ids in cal.items():
            if not isinstance(ids, list):
                new_cal[date_key] = ids
                continue
            new_ids = [x for x in ids if x != discount_id]
            if new_ids != ids:
                changed = True
            if new_ids:
                new_cal[date_key] = new_ids
        if changed:
            update_cuponera(c["id"], {"calendar": new_cal})
            modified += 1
    return modified


def write_discounts(data: list[dict]):
    _save_json(DISCOUNTS_JSON, data if data else [])


# --- Folders ---
def _read_folders_list() -> list[dict]:
    data = _load_json(FOLDERS_JSON, [])
    return data if isinstance(data, list) else []


def read_folders() -> list[dict]:
    return _read_folders_list()


def get_folder(folder_id: str) -> dict | None:
    for f in _read_folders_list():
        if f.get("id") == folder_id:
            return f
    return None


def insert_folder(doc: dict) -> dict:
    items = _read_folders_list()
    items.append(doc)
    _save_json(FOLDERS_JSON, items)
    return doc


def update_folder(folder_id: str, upd: dict) -> dict | None:
    items = _read_folders_list()
    for i, f in enumerate(items):
        if f.get("id") == folder_id:
            old_name = str(f.get("name") or "").strip()
            items[i] = {**f, **upd}
            new_name = str(items[i].get("name") or "").strip()
            _save_json(FOLDERS_JSON, items)
            if old_name and new_name and old_name != new_name:
                _update_folder_refs(old_name, new_name)
            return items[i]
    return None


def _update_folder_refs(old_name: str, new_name: str):
    """Actualiza referencias de folder en descuentos y cuponeras al renombrar."""
    changed_d, changed_c = False, False
    items_d = _read_discounts_list()
    for i, d in enumerate(items_d):
        if d.get("folder") == old_name:
            items_d[i] = {**d, "folder": new_name}
            changed_d = True
    if changed_d:
        _save_json(DISCOUNTS_JSON, items_d)
    items_c = _read_cuponeras_list()
    for i, c in enumerate(items_c):
        if c.get("folder") == old_name:
            items_c[i] = {**c, "folder": new_name}
            changed_c = True
    if changed_c:
        _save_json(CUPONERAS_JSON, items_c)


def delete_folder_only(folder_id: str) -> bool:
    items = _read_folders_list()
    new_items = [f for f in items if f.get("id") != folder_id]
    if len(new_items) == len(items):
        return False
    _save_json(FOLDERS_JSON, new_items)
    return True


def delete_folder_by_id(folder_id: str) -> bool:
    doc = get_folder(folder_id)
    if not doc:
        return False
    folder_name = (doc.get("name") or "").strip()
    if folder_name:
        cascade_clear_folder(folder_name)
    return delete_folder_only(folder_id)


def cascade_clear_folder(folder_name: str) -> tuple[int, int]:
    """Pone folder='' en todos los descuentos y cuponeras que usan esta carpeta."""
    if not folder_name:
        return 0, 0
    d_count, c_count = 0, 0
    items_d = _read_discounts_list()
    for i, d in enumerate(items_d):
        if d.get("folder") == folder_name:
            items_d[i] = {**d, "folder": ""}
            d_count += 1
    if d_count:
        _save_json(DISCOUNTS_JSON, items_d)
    items_c = _read_cuponeras_list()
    for i, c in enumerate(items_c):
        if c.get("folder") == folder_name:
            items_c[i] = {**c, "folder": ""}
            c_count += 1
    if c_count:
        _save_json(CUPONERAS_JSON, items_c)
    return d_count, c_count


def write_folders(data: list[dict]):
    _save_json(FOLDERS_JSON, data if data else [])


# --- Cuponeras ---
def _read_cuponeras_list() -> list[dict]:
    data = _load_json(CUPONERAS_JSON, [])
    return data if isinstance(data, list) else []


def read_cuponeras() -> list[dict]:
    return _read_cuponeras_list()


def get_cuponera(cuponera_id: str) -> dict | None:
    for c in _read_cuponeras_list():
        if c.get("id") == cuponera_id:
            return c
    return None


def insert_cuponera(doc: dict) -> dict:
    items = _read_cuponeras_list()
    items.append(doc)
    _save_json(CUPONERAS_JSON, items)
    return doc


def update_cuponera(cuponera_id: str, upd: dict) -> dict | None:
    items = _read_cuponeras_list()
    for i, c in enumerate(items):
        if c.get("id") == cuponera_id:
            items[i] = {**c, **upd}
            _save_json(CUPONERAS_JSON, items)
            return items[i]
    return None


def delete_cuponera(cuponera_id: str) -> bool:
    items = _read_cuponeras_list()
    new_items = [c for c in items if c.get("id") != cuponera_id]
    if len(new_items) == len(items):
        return False
    _save_json(CUPONERAS_JSON, new_items)
    users = _read_cuponera_users_list()
    new_users = [u for u in users if u.get("cuponera_id") != cuponera_id]
    _save_json(CUPONERA_USERS_JSON, new_users)
    usage = read_cuponera_usage()
    new_usage = [u for u in usage if u.get("cuponera_id") != cuponera_id]
    write_cuponera_usage(new_usage)
    return True


def write_cuponeras(data: list[dict]):
    _save_json(CUPONERAS_JSON, data if data else [])


# --- Cuponera usage ---
def read_cuponera_usage() -> list[dict]:
    data = _load_json(CUPONERA_USAGE_JSON, [])
    return data if isinstance(data, list) else []


def write_cuponera_usage(data: list[dict]):
    _save_json(CUPONERA_USAGE_JSON, data if data else [])


# --- Cuponera users ---
def _read_cuponera_users_list() -> list[dict]:
    data = _load_json(CUPONERA_USERS_JSON, [])
    return data if isinstance(data, list) else []


def read_cuponera_users() -> list[dict]:
    return _read_cuponera_users_list()


def get_cuponera_user(cuponera_id: str, user_id: str) -> dict | None:
    for u in _read_cuponera_users_list():
        if u.get("cuponera_id") == cuponera_id and u.get("id") == user_id:
            return u
    return None


def insert_cuponera_user(doc: dict) -> dict:
    items = _read_cuponera_users_list()
    items.append(doc)
    _save_json(CUPONERA_USERS_JSON, items)
    return doc


def update_cuponera_user(cuponera_id: str, user_id: str, upd: dict) -> dict | None:
    items = _read_cuponera_users_list()
    for i, u in enumerate(items):
        if u.get("cuponera_id") == cuponera_id and u.get("id") == user_id:
            items[i] = {**u, **upd}
            _save_json(CUPONERA_USERS_JSON, items)
            return items[i]
    return None


def delete_cuponera_user(cuponera_id: str, user_id: str) -> bool:
    items = _read_cuponera_users_list()
    new_items = [
        u for u in items
        if not (u.get("cuponera_id") == cuponera_id and u.get("id") == user_id)
    ]
    if len(new_items) == len(items):
        return False
    _save_json(CUPONERA_USERS_JSON, new_items)
    return True


def write_cuponera_users(data: list[dict]):
    _save_json(CUPONERA_USERS_JSON, data if data else [])
