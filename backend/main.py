import asyncio
import json
import os
import shutil
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import DATA_DIR, MENUS_DIR, SITES_JSON
from routers import cuponeras, cuponera_users, discounts, folders, menus, redeem, sites
from storage import read_sites, write_sites, write_menu
from sync_service import run_sync_loop


def _seed_data_if_needed():
    """Si data/ está vacío, copiar sites.json y menu_site_4.json desde backend."""
    base = os.path.dirname(os.path.abspath(__file__))
    # Sites: copiar o cargar solo si el archivo origen tiene contenido válido
    if not os.path.exists(SITES_JSON) or (os.path.exists(SITES_JSON) and os.path.getsize(SITES_JSON) == 0):
        src = os.path.join(base, "sites.json")
        if os.path.exists(src) and os.path.getsize(src) > 0:
            try:
                os.makedirs(DATA_DIR, exist_ok=True)
                with open(src, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data:
                    write_sites(data)
            except (json.JSONDecodeError, OSError):
                pass
    sites_list = read_sites()
    if not sites_list:
        src = os.path.join(base, "sites.json")
        if os.path.exists(src) and os.path.getsize(src) > 0:
            try:
                with open(src, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data:
                    write_sites(data)
            except (json.JSONDecodeError, OSError):
                pass
    # Menú sede 4: solo si el archivo existe, tiene contenido y es JSON válido
    menu_src = os.path.join(base, "menu_site_4.json")
    menu_dst = os.path.join(MENUS_DIR, "site_4.json")
    if os.path.exists(menu_src) and os.path.getsize(menu_src) > 0 and not os.path.exists(menu_dst):
        try:
            os.makedirs(MENUS_DIR, exist_ok=True)
            with open(menu_src, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data and isinstance(data, dict):
                write_menu(4, data)
        except (json.JSONDecodeError, OSError):
            pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    _seed_data_if_needed()
    task = asyncio.create_task(run_sync_loop())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Salchimonster Descuentos API",
    description="API para gestión de descuentos, cuponeras y canje de códigos",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sites.router)
app.include_router(menus.router)
app.include_router(folders.router)
app.include_router(discounts.router)
app.include_router(cuponeras.router)
app.include_router(cuponera_users.router)
app.include_router(redeem.router)


@app.get("/")
def root():
    return {"message": "Bienvenido a la API de Salchimonster Descuentos"}


@app.get("/health")
def health():
    return {"status": "ok"}
