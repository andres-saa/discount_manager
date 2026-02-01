"""CRUD de carpetas. Borrado con cascade: quita la carpeta de descuentos y cuponeras."""
from fastapi import APIRouter, HTTPException, Query

from models import Folder, FolderCreate, FolderUpdate
from storage import cascade_clear_folder, read_folders, write_folders
from utils import new_id, now_iso

router = APIRouter(prefix="/folders", tags=["folders"])


@router.get("", response_model=list[Folder])
def list_folders():
    items = read_folders()
    return sorted(items, key=lambda x: (x.get("sort_order") is None, x.get("sort_order") or 0, (x.get("name") or "").lower()))


@router.get("/{folder_id}", response_model=Folder)
def get_folder(folder_id: str):
    items = read_folders()
    for f in items:
        if f.get("id") == folder_id:
            return f
    raise HTTPException(status_code=404, detail="Carpeta no encontrada")


@router.post("", response_model=Folder, status_code=201)
def create_folder(body: FolderCreate):
    items = read_folders()
    name = (body.name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="El nombre es obligatorio")
    for f in items:
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
    items.append(doc)
    write_folders(items)
    return doc


@router.patch("/{folder_id}", response_model=Folder)
def update_folder(folder_id: str, body: FolderUpdate):
    items = read_folders()
    for i, f in enumerate(items):
        if f.get("id") == folder_id:
            upd = body.model_dump(exclude_unset=True)
            if "name" in upd and upd["name"] is not None:
                name = (upd["name"] or "").strip()
                if not name:
                    raise HTTPException(status_code=400, detail="El nombre no puede estar vacío")
                for other in items:
                    if other.get("id") != folder_id and (other.get("name") or "").strip().lower() == name.lower():
                        raise HTTPException(status_code=400, detail="Ya existe otra carpeta con ese nombre")
                upd["name"] = name
            f.update(upd)
            f["updated_at"] = now_iso()
            write_folders(items)
            return f
    raise HTTPException(status_code=404, detail="Carpeta no encontrada")


@router.delete("/{folder_id}", status_code=204)
def delete_folder(
    folder_id: str,
    cascade: bool = Query(True, description="Si es true, quita esta carpeta de todos los descuentos y cuponeras que la usen"),
):
    items = read_folders()
    folder_doc = None
    for f in items:
        if f.get("id") == folder_id:
            folder_doc = f
            break
    if not folder_doc:
        raise HTTPException(status_code=404, detail="Carpeta no encontrada")
    folder_name = folder_doc.get("name") or ""
    if cascade:
        cascade_clear_folder(folder_name)
    new_items = [f for f in items if f.get("id") != folder_id]
    write_folders(new_items)
