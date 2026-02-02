"""CRUD de reglas de descuento."""
from fastapi import APIRouter, HTTPException

from discount_validation import validate_discount_by_type
from menu_validation import validate_discount_scope_full
from models import DiscountRule, DiscountRuleCreate, DiscountRuleUpdate
from storage import delete_discount, get_discount, insert_discount, read_discounts, update_discount
from utils import new_id, now_iso

router = APIRouter(prefix="/discounts", tags=["discounts"])


@router.get("", response_model=list[DiscountRule])
def list_discounts():
    return read_discounts()


@router.get("/{discount_id}", response_model=DiscountRule)
def get_discount_route(discount_id: str):
    d = get_discount(discount_id)
    if not d:
        raise HTTPException(status_code=404, detail="Descuento no encontrado")
    return d


@router.post("", response_model=DiscountRule, status_code=201)
def create_discount(body: DiscountRuleCreate):
    site_ids = body.site_ids
    scope_d = body.scope.model_dump()
    ok, errors = validate_discount_scope_full(site_ids, scope_d)
    if not ok:
        raise HTTPException(status_code=400, detail={"message": "Scope inválido para las sedes seleccionadas", "errors": errors})
    ok2, errors2 = validate_discount_by_type(
        body.type, body.params, scope_d, body.conditions, body.limits, body.selection_rule
    )
    if not ok2:
        raise HTTPException(status_code=400, detail={"message": "Datos incorrectos para este tipo de descuento", "errors": errors2})
    discount_id = new_id("disc")
    now = now_iso()
    doc = {
        "id": discount_id,
        "type": body.type,
        "name": body.name,
        "priority": body.priority,
        "stacking_policy": body.stacking_policy,
        "scope": body.scope.model_dump(),
        "conditions": body.conditions,
        "params": body.params,
        "limits": body.limits,
        "selection_rule": body.selection_rule,
        "apply_as": body.apply_as,
        "audit": body.audit,
        "site_ids": body.site_ids,
        "folder": body.folder,
        "created_at": now,
        "updated_at": now,
    }
    return insert_discount(doc)


@router.patch("/{discount_id}", response_model=DiscountRule)
def update_discount_route(discount_id: str, body: DiscountRuleUpdate):
    d = get_discount(discount_id)
    if not d:
        raise HTTPException(status_code=404, detail="Descuento no encontrado")
    upd = body.model_dump(exclude_unset=True)
    if "scope" in upd and upd["scope"] is not None:
        scope = upd["scope"]
        if hasattr(scope, "model_dump"):
            scope = scope.model_dump()
        upd["scope"] = scope
    if "scope" in upd and hasattr(upd.get("scope"), "model_dump"):
        upd["scope"] = upd["scope"].model_dump()
    scope_final = upd.get("scope") or d.get("scope") or {}
    site_ids = upd.get("site_ids") or d.get("site_ids")
    ok, errors = validate_discount_scope_full(site_ids, scope_final)
    if not ok:
        raise HTTPException(
            status_code=400,
            detail={"message": "Scope inválido para las sedes", "errors": errors},
        )
    discount_type = upd.get("type") or d.get("type")
    params = upd.get("params") or d.get("params") or {}
    conditions = upd.get("conditions") or d.get("conditions") or {}
    limits = upd.get("limits") or d.get("limits") or {}
    sel_rule = upd.get("selection_rule") or d.get("selection_rule")
    ok2, errors2 = validate_discount_by_type(
        discount_type, params, scope_final, conditions, limits, sel_rule
    )
    if not ok2:
        raise HTTPException(
            status_code=400,
            detail={"message": "Datos incorrectos para este tipo de descuento", "errors": errors2},
        )
    upd["updated_at"] = now_iso()
    result = update_discount(discount_id, upd)
    return result


@router.delete("/{discount_id}", status_code=204)
def delete_discount_route(discount_id: str):
    if not delete_discount(discount_id):
        raise HTTPException(status_code=404, detail="Descuento no encontrado")
