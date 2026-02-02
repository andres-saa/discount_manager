import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import cuponeras, cuponera_users, discounts, folders, menus, redeem, sites
from sync_service import run_sync_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
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
