"""Menús por sede y catálogo (categorías/productos) para selects con limit/offset y búsqueda."""
from fastapi import APIRouter, HTTPException, Query

from menu_catalog import get_categories, get_products
from storage import read_menu

router = APIRouter(prefix="/menus", tags=["menus"])


@router.get("/site/{site_id}")
def get_menu(site_id: int):
    menu = read_menu(site_id)
    if menu is None:
        raise HTTPException(status_code=404, detail="Menú no encontrado para esta sede")
    return menu


@router.get("/categories")
def list_categories(
    site_ids: str | None = Query(None, description="IDs de sedes separados por coma; vacío = todas las permitidas"),
):
    """Lista de categorías para selects. Validado por backend según sedes."""
    ids = None
    if site_ids and site_ids.strip():
        try:
            ids = [int(x.strip()) for x in site_ids.split(",") if x.strip()]
        except ValueError:
            pass
    return get_categories(ids)


@router.get("/products")
def list_products(
    site_ids: str | None = Query(None, description="IDs de sedes separados por coma; vacío = todas"),
    q: str | None = Query(None, description="Búsqueda en nombre/descripción"),
    limit: int | None = Query(None, ge=1, le=10000, description="Límite de resultados (opcional, si no se especifica devuelve todos)"),
    offset: int = Query(0, ge=0),
    ids: str | None = Query(None, description="IDs de productos a incluir siempre (p. ej. ya seleccionados), separados por coma"),
):
    """Lista de productos con paginación opcional y búsqueda. Si no se especifica limit, devuelve todos los productos."""
    sid_list = None
    if site_ids and site_ids.strip():
        try:
            sid_list = [int(x.strip()) for x in site_ids.split(",") if x.strip()]
        except ValueError:
            pass
    ids_include = None
    if ids and ids.strip():
        ids_include = [x.strip() for x in ids.split(",") if x.strip()]
    
    # Si no se especifica limit, usar un valor muy alto para obtener todos
    actual_limit = limit if limit is not None else 999999
    items, total = get_products(site_ids=sid_list, q=q, limit=actual_limit, offset=offset, ids_to_include=ids_include)
    return {"items": items, "total": total}
