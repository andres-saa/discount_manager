"""CRUD de cuponeras."""
from fastapi import APIRouter, HTTPException

from models import Cuponera, CuponeraCreate, CuponeraUpdate
from storage import read_cuponeras, write_cuponeras
from utils import new_id, now_iso

router = APIRouter(prefix="/cuponeras", tags=["cuponeras"])


@router.get("", response_model=list[Cuponera])
def list_cuponeras():
    return read_cuponeras()


@router.get("/{cuponera_id}", response_model=Cuponera)
def get_cuponera(cuponera_id: str):
    for c in read_cuponeras():
        if c.get("id") == cuponera_id:
            return c
    raise HTTPException(status_code=404, detail="Cuponera no encontrada")


@router.post("", response_model=Cuponera, status_code=201)
def create_cuponera(body: CuponeraCreate):
    cuponera_id = new_id("cup")
    now = now_iso()
    doc = {
        "id": cuponera_id,
        "name": body.name,
        "description": body.description,
        "uses_per_day": body.uses_per_day,
        "calendar": body.calendar,
        "site_ids": body.site_ids,
        "folder": body.folder,
        "active": body.active,
        "start_date": body.start_date,
        "end_date": body.end_date,
        "created_at": now,
        "updated_at": now,
    }
    data = read_cuponeras()
    data.append(doc)
    write_cuponeras(data)
    return doc


@router.patch("/{cuponera_id}", response_model=Cuponera)
def update_cuponera(cuponera_id: str, body: CuponeraUpdate):
    data = read_cuponeras()
    for i, c in enumerate(data):
        if c.get("id") == cuponera_id:
            upd = body.model_dump(exclude_unset=True)
            c.update(upd)
            c["updated_at"] = now_iso()
            write_cuponeras(data)
            return c
    raise HTTPException(status_code=404, detail="Cuponera no encontrada")


@router.delete("/{cuponera_id}", status_code=204)
def delete_cuponera(cuponera_id: str):
    data = read_cuponeras()
    new_data = [c for c in data if c.get("id") != cuponera_id]
    if len(new_data) == len(data):
        raise HTTPException(status_code=404, detail="Cuponera no encontrada")
    write_cuponeras(new_data)
