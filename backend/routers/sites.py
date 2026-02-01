"""Sedes (solo lectura desde JSON local, sincronizado con API). Filtro: time_zone America/Bogota, sin site_id 32."""
from fastapi import APIRouter, HTTPException

from storage import read_sites_filtered

router = APIRouter(prefix="/sites", tags=["sites"])


@router.get("")
def list_sites():
    return read_sites_filtered()


@router.get("/{site_id}")
def get_site(site_id: int):
    for s in read_sites_filtered():
        if s.get("site_id") == site_id:
            return s
    raise HTTPException(status_code=404, detail="Sede no encontrada")
