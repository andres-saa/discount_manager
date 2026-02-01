"""Configuración y rutas de datos."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SITES_JSON = os.path.join(DATA_DIR, "sites.json")
MENUS_DIR = os.path.join(DATA_DIR, "menus")
DISCOUNTS_JSON = os.path.join(DATA_DIR, "discounts.json")
FOLDERS_JSON = os.path.join(DATA_DIR, "folders.json")
CUPONERAS_JSON = os.path.join(DATA_DIR, "cuponeras.json")
CUPONERA_USAGE_JSON = os.path.join(DATA_DIR, "cuponera_usage.json")

SITES_API_URL = "https://backend.salchimonster.com/sites"
MENU_API_URL_TEMPLATE = "https://backend.salchimonster.com/tiendas/{site_id}/products-light"

SYNC_INTERVAL_MINUTES = 10
