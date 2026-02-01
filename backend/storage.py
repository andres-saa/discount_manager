"""Almacenamiento en JSON locales."""
import json
import os
from pathlib import Path
from typing import Any

from config import (
    CUPONERAS_JSON,
    CUPONERA_USAGE_JSON,
    DATA_DIR,
    DISCOUNTS_JSON,
    FOLDERS_JSON,
    MENUS_DIR,
    SITES_JSON,
)


def _ensure_data_dir():
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    Path(MENUS_DIR).mkdir(parents=True, exist_ok=True)


def _read_json(path: str, default: Any = None) -> Any:
    if default is None and path == SITES_JSON:
        default = []
    if default is None and path == DISCOUNTS_JSON:
        default = []
    if default is None and path == CUPONERAS_JSON:
        default = []
    if default is None and path == FOLDERS_JSON:
        default = []
    if default is None and path == CUPONERA_USAGE_JSON:
        default = []
    if not os.path.exists(path):
        return default if default is not None else {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: str, data: Any):
    _ensure_data_dir()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# --- Sites ---
# Sedes permitidas: time_zone America/Bogota, excluir site_id 32, show_on_web true
def _site_allowed(s: dict) -> bool:
    if s.get("site_id") == 32:
        return False
    if (s.get("time_zone") or "") != "America/Bogota":
        return False
    return s.get("show_on_web") is True


def read_sites() -> list[dict]:
    return _read_json(SITES_JSON, [])


def read_sites_filtered() -> list[dict]:
    """Sedes filtradas: solo time_zone America/Bogota, sin site_id 32."""
    return [s for s in read_sites() if _site_allowed(s)]


def write_sites(data: list[dict]):
    _write_json(SITES_JSON, data)


# --- Menus (por sede) ---
def menu_path(site_id: int) -> str:
    return os.path.join(MENUS_DIR, f"site_{site_id}.json")


def read_menu(site_id: int) -> dict | None:
    p = menu_path(site_id)
    if not os.path.exists(p):
        return None
    return _read_json(p, {})


def write_menu(site_id: int, data: dict):
    _ensure_data_dir()
    _write_json(menu_path(site_id), data)


def list_menu_site_ids() -> list[int]:
    if not os.path.isdir(MENUS_DIR):
        return []
    ids = []
    for f in os.listdir(MENUS_DIR):
        if f.startswith("site_") and f.endswith(".json"):
            try:
                ids.append(int(f[5:-5]))
            except ValueError:
                pass
    return ids


# --- Discounts ---
def read_discounts() -> list[dict]:
    return _read_json(DISCOUNTS_JSON, [])


def write_discounts(data: list[dict]):
    _write_json(DISCOUNTS_JSON, data)


# --- Folders ---
def read_folders() -> list[dict]:
    return _read_json(FOLDERS_JSON, [])


def write_folders(data: list[dict]):
    _write_json(FOLDERS_JSON, data)


def cascade_clear_folder(folder_name: str) -> tuple[int, int]:
    """Pone folder='' en todos los descuentos y cuponeras que usan esta carpeta. Devuelve (discounts_updated, cuponeras_updated)."""
    disc_count = 0
    cup_count = 0
    if not folder_name:
        return disc_count, cup_count
    data_d = read_discounts()
    for d in data_d:
        if (d.get("folder") or "") == folder_name:
            d["folder"] = ""
            disc_count += 1
    if disc_count:
        write_discounts(data_d)
    data_c = read_cuponeras()
    for c in data_c:
        if (c.get("folder") or "") == folder_name:
            c["folder"] = ""
            cup_count += 1
    if cup_count:
        write_cuponeras(data_c)
    return disc_count, cup_count


# --- Cuponeras ---
def read_cuponeras() -> list[dict]:
    return _read_json(CUPONERAS_JSON, [])


def write_cuponeras(data: list[dict]):
    _write_json(CUPONERAS_JSON, data)


# --- Cuponera usage (por día y código) ---
def read_cuponera_usage() -> list[dict]:
    return _read_json(CUPONERA_USAGE_JSON, [])


def write_cuponera_usage(data: list[dict]):
    _write_json(CUPONERA_USAGE_JSON, data)
