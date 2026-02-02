"""CRUD de carpetas. Borrado con cascade: quita la carpeta de descuentos y cuponeras."""
from fastapi import APIRouter, HTTPException, Query

from models import Folder, FolderCreate, FolderUpdate
from storage import cascade_clear_folder, delete_folder_by_id, get_folder, insert_folder, read_folders, update_folder, write_folders
from utils import new_id, now_iso

router = APIRouter(prefix="/folders", tags=["folders"])


@router.get("", response_model=list[Folder])
def list_folders():
    items = read_folders()
    return sorted(items, key=lambda x: (x.get("sort_order") is None, x.get("sort_order") or 0, (x.get("name") or "").lower()))


@router.get("/{folder_id}", response_model=Folder)
def get_folder_route(folder_id: str):
    f = get_folder(folder_id)
    if not f:
        raise HTTPException(status_code=404, detail="Carpeta no encontrada")
    return f


@router.post("", response_model=Folder, status_code=201)
def create_folder_route(body: FolderCreate):
    name = (body.name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="El nombre es obligatorio")
    for f in read_folders():
        if (f.get("name") or "").strip().lower() == name.lower():
            raise HTTPException(status_code=400, detail="Ya existe una carpeta con ese nombre")
    folder_id = new_id("folder")
    now = now_iso()
    doc = {
        "id": folder_id,
        "name": name,
        "description": body.description or None,
        "sort_order": body.sort_order,
        "created_at": now,
        "updated_at": now,
    }
    return insert_folder(doc)


@router.patch("/{folder_id}", response_model=Folder)
def update_folder_route(folder_id: str, body: FolderUpdate):
    f = get_folder(folder_id)
    if not f:
        raise HTTPException(status_code=404, detail="Carpeta no encontrada")
    upd = body.model_dump(exclude_unset=True)
    if "name" in upd and upd["name"] is not None:
        name = (upd["name"] or "").strip()
        if not name:
            raise HTTPException(status_code=400, detail="El nombre no puede estar vacío")
        for other in read_folders():
            if other.get("id") != folder_id and (other.get("name") or "").strip().lower() == name.lower():
                raise HTTPException(status_code=400, detail="Ya existe otra carpeta con ese nombre")
        upd["name"] = name
    upd["updated_at"] = now_iso()
    result = update_folder(folder_id, upd)
    return result


@router.delete("/{folder_id}", status_code=204)
def delete_folder_route(
    folder_id: str,
    cascade: bool = Query(True, description="Si es true, quita esta carpeta de todos los descuentos y cuponeras que la usen"),
):
    if not get_folder(folder_id):
        raise HTTPException(status_code=404, detail="Carpeta no encontrada")
    if cascade:
        delete_folder_by_id(folder_id)
    else:
        delete_folder_only(folder_id)
