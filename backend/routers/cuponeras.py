"""CRUD de cuponeras."""
from fastapi import APIRouter, HTTPException, Query

from models import Cuponera, CuponeraCreate, CuponeraUpdate
from storage import (
    delete_cuponera,
    get_cuponera,
    insert_cuponera,
    read_cuponeras,
    read_cuponera_usage,
    update_cuponera,
    write_cuponera_usage,
)
from utils import new_id, now_iso

router = APIRouter(prefix="/cuponeras", tags=["cuponeras"])


@router.get("", response_model=list[Cuponera])
def list_cuponeras():
    return read_cuponeras()


@router.get("/{cuponera_id}", response_model=Cuponera)
def get_cuponera_route(cuponera_id: str):
    c = get_cuponera(cuponera_id)
    if not c:
        raise HTTPException(status_code=404, detail="Cuponera no encontrada")
    return c


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
    return insert_cuponera(doc)


@router.patch("/{cuponera_id}", response_model=Cuponera)
def update_cuponera_route(cuponera_id: str, body: CuponeraUpdate):
    c = get_cuponera(cuponera_id)
    if not c:
        raise HTTPException(status_code=404, detail="Cuponera no encontrada")
    upd = body.model_dump(exclude_unset=True)
    upd["updated_at"] = now_iso()
    result = update_cuponera(cuponera_id, upd)
    return result


@router.delete("/{cuponera_id}", status_code=204)
def delete_cuponera_route(cuponera_id: str):
    if not delete_cuponera(cuponera_id):
        raise HTTPException(status_code=404, detail="Cuponera no encontrada")


@router.post("/{cuponera_id}/usage/reset")
def reset_usage(
    cuponera_id: str,
    user_code: str = Query(..., description="Código del usuario en la cuponera"),
    date: str = Query(..., description="Fecha YYYY-MM-DD a resetear"),
):
    """
    Resetea los usos registrados para un código en una fecha.
    Así el usuario vuelve a tener uses_remaining_today = uses_per_day para ese día.
    """
    if not get_cuponera(cuponera_id):
        raise HTTPException(status_code=404, detail="Cuponera no encontrada")

    code_upper = (user_code or "").strip().upper()
    if not code_upper:
        raise HTTPException(status_code=400, detail="user_code requerido")

    date_str = (date or "").strip()
    if not date_str or len(date_str) < 10:
        raise HTTPException(status_code=400, detail="date requerido (YYYY-MM-DD)")

    cuponera_id_str = str(cuponera_id)
    usage_list = read_cuponera_usage()
    new_list = []
    found = False
    for rec in usage_list:
        rec_cid = str(rec.get("cuponera_id") or "")
        rec_code = (rec.get("user_code") or "").strip().upper()
        rec_date = str(rec.get("date") or "")
        if rec_cid == cuponera_id_str and rec_code == code_upper and rec_date == date_str:
            found = True
            continue
        new_list.append(rec)
    if found:
        write_cuponera_usage(new_list)
    return {"ok": True, "message": "Usos reseteados para esa fecha.", "had_record": found}
