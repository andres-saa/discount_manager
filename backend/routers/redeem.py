"""Canjear código de cuponera: obtener descuentos del día y registrar uso."""
from datetime import date

from fastapi import APIRouter, HTTPException, Query

from models import RedeemDiscountItem, RedeemResponse, RedeemUserInfo
from storage import read_cuponeras, read_cuponera_usage, read_cuponera_users, read_discounts, write_cuponera_usage, read_menu

router = APIRouter(prefix="", tags=["redeem"])


def _is_cuponera_vigent(cuponera: dict, today: str) -> bool:
    """Cuponera vigente = activa y hoy dentro de start_date..end_date."""
    if not cuponera.get("active"):
        return False
    start = (cuponera.get("start_date") or "").strip() or None
    end = (cuponera.get("end_date") or "").strip() or None
    if start and today < start:
        return False
    if end and today > end:
        return False
    return True


def _get_product_info(product_id: str, site_ids: list[int] | None) -> dict | None:
    """Busca info del producto en los menús de las sedes especificadas."""
    if not product_id:
        return None
    
    # Si no hay site_ids, buscar en todas las sedes disponibles
    from storage import read_sites_filtered
    if not site_ids:
        site_ids = [s["site_id"] for s in read_sites_filtered() if s.get("site_id")]
    
    for site_id in site_ids:
        menu = read_menu(site_id)
        if not menu:
            continue
        
        for cat in menu.get("categorias") or []:
            for prod in cat.get("products") or []:
                if str(prod.get("producto_id")) == str(product_id):
                    return {
                        "product_id": str(product_id),
                        "name": (prod.get("producto_descripcion") or prod.get("english_name") or "").strip(),
                        "price": float(prod.get("productogeneral_precio") or 0),
                        "image": prod.get("productogeneral_urlimagen") or "",
                        "category_id": str(cat.get("categoria_id") or ""),
                    }
    
    return None


def _get_categories_info(category_ids: list[str], site_ids: list[int] | None) -> list[dict]:
    """Busca info de las categorías en los menús de las sedes especificadas."""
    if not category_ids:
        return []
    
    from storage import read_sites_filtered
    if not site_ids:
        site_ids = [s["site_id"] for s in read_sites_filtered() if s.get("site_id")]
    
    categories_found = {}
    category_ids_set = set(str(cid) for cid in category_ids)
    
    for site_id in site_ids:
        menu = read_menu(site_id)
        if not menu:
            continue
        
        for cat in menu.get("categorias") or []:
            cat_id = str(cat.get("categoria_id") or "")
            if cat_id in category_ids_set and cat_id not in categories_found:
                categories_found[cat_id] = {
                    "category_id": cat_id,
                    "name": (cat.get("categoria_nombre") or cat.get("categoria_descripcion") or "").strip(),
                    "image": cat.get("categoria_urlimagen") or "",
                }
        
        # Si ya encontramos todas las categorías, salir
        if len(categories_found) == len(category_ids_set):
            break
    
    return list(categories_found.values())


@router.get("/redeem", response_model=RedeemResponse)
def redeem_code(
    code: str = Query(..., description="Código del usuario en la cuponera"),
    use_date: str | None = Query(None, alias="date", description="Fecha YYYY-MM-DD (por defecto hoy)"),
    record_use: bool = Query(False, description="Si true, registra un uso para hoy (consumir una de las veces del día)"),
):
    """Devuelve los descuentos del día para el código. Si el código pertenece a varias cuponeras (pasadas y vigente), devuelve la cuponera vigente."""
    today = use_date or date.today().isoformat()
    code_upper = (code or "").strip().upper()
    if not code_upper:
        raise HTTPException(status_code=400, detail="Código requerido")

    users = read_cuponera_users()
    cuponeras = read_cuponeras()
    cuponera_map = {c.get("id"): c for c in cuponeras if c.get("id")}

    # Buscar usuario + cuponera vigente (si el código está en varias cuponeras, priorizar la vigente)
    user = None
    cuponera = None
    vigent_candidates = []
    for u in users:
        if (u.get("code") or "").strip().upper() != code_upper:
            continue
        c = cuponera_map.get(u.get("cuponera_id") or "")
        if not c:
            continue
        if _is_cuponera_vigent(c, today):
            vigent_candidates.append((u, c))
    if vigent_candidates:
        user, cuponera = vigent_candidates[0]
        cuponera_id = cuponera.get("id")
    else:
        # Código no existe o no tiene cuponera vigente
        for u in users:
            if (u.get("code") or "").strip().upper() == code_upper:
                c = cuponera_map.get(u.get("cuponera_id") or "")
                if c and not c.get("active"):
                    return RedeemResponse(success=False, message="Cuponera no activa")
                if c:
                    start_date = (c.get("start_date") or "").strip()
                    end_date = (c.get("end_date") or "").strip()
                    if start_date and today < start_date:
                        return RedeemResponse(
                            success=False,
                            message=f"La cuponera aún no ha comenzado. Vigencia desde el {start_date}.",
                        )
                    if end_date and today > end_date:
                        return RedeemResponse(
                            success=False,
                            message=f"La cuponera ya finalizó. Vigencia hasta el {end_date}. Puede renovar al cliente en una cuponera vigente con el mismo código.",
                        )
        return RedeemResponse(success=False, message="Código no válido o no hay cuponera vigente para este código")

    calendar = cuponera.get("calendar") or {}
    discount_ids = calendar.get(today) or []
    
    # Construir user_info con nombre dividido y phone_code
    user_info = None
    if user:
        full_name = (user.get("name") or "").strip()
        first_name = user.get("first_name") or ""
        last_name = user.get("last_name") or ""
        
        # Si no hay first_name/last_name pero hay name, dividir el nombre completo
        if not first_name and not last_name and full_name:
            name_parts = full_name.split(None, 1)  # Divide en 2 partes máximo
            first_name = name_parts[0] if len(name_parts) > 0 else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        user_info = RedeemUserInfo(
            name=full_name,
            first_name=first_name,
            last_name=last_name,
            phone=user.get("phone") or "",
            phone_code=user.get("phone_code") or "+57",  # Default a Colombia si no está especificado
            email=user.get("email") or "",
            address=user.get("address") or "",
        )

    cuponera_site_ids = cuponera.get("site_ids")  # null = todas las sedes

    if not discount_ids:
        return RedeemResponse(
            success=True,
            message="No hay descuentos configurados para esta fecha.",
            cuponera_name=cuponera.get("name"),
            discounts=[],
            uses_remaining_today=0,
            user=user_info,
            cuponera_site_ids=cuponera_site_ids,
        )

    # Obtener reglas de descuento
    all_discounts = read_discounts()
    discount_map = {d.get("id"): d for d in all_discounts if d.get("id")}
    discounts_for_day = []
    free_product_info = None
    discount_categories_info = None
    discount_products_info = None
    
    for did in discount_ids:
        if did in discount_map:
            discount = discount_map[did]
            discounts_for_day.append(
                RedeemDiscountItem(discount_id=did, discount=discount)
            )
            
            discount_type = discount.get("type") or ""
            scope = discount.get("scope") or {}
            params = discount.get("params") or {}
            
            # Si es FREE_ITEM, obtener info del producto y (si aplica) categorías o productos del scope para requires_purchase
            if discount_type == "FREE_ITEM":
                free_item = params.get("free_item") or {}
                product_id = free_item.get("product_id")
                if product_id:
                    product_info = _get_product_info(product_id, cuponera_site_ids)
                    if product_info:
                        free_product_info = product_info
                        limits = discount.get("limits") or {}
                        free_product_info["max_qty"] = limits.get("max_free_qty", 1)
                scope_type = scope.get("scope_type") or ""
                category_ids = scope.get("category_ids") or []
                product_ids = scope.get("product_ids") or []
                if scope_type == "CATEGORY_IDS" and category_ids:
                    discount_categories_info = _get_categories_info(category_ids, cuponera_site_ids)
                # Incluir discount_products si hay product_ids (aunque scope_type sea ALL_ITEMS)
                if product_ids:
                    prods = []
                    for pid in product_ids:
                        prod_info = _get_product_info(str(pid), cuponera_site_ids)
                        if prod_info:
                            prods.append(prod_info)
                    if prods:
                        discount_products_info = prods
            # Si es descuento por CATEGORÍA, obtener info de las categorías
            elif discount_type in ("CATEGORY_PERCENT_OFF", "CATEGORY_AMOUNT_OFF", "BUY_M_PAY_N"):
                scope_type = scope.get("scope_type") or ""
                category_ids = scope.get("category_ids") or []
                product_ids_scope = scope.get("product_ids") or []
                if scope_type == "CATEGORY_IDS" and category_ids:
                    discount_categories_info = _get_categories_info(category_ids, cuponera_site_ids)
                # BUY_M_PAY_N: incluir discount_products si hay product_ids (aunque scope_type sea ALL_ITEMS)
                if discount_type == "BUY_M_PAY_N" and product_ids_scope:
                    prods = []
                    for pid in product_ids_scope:
                        prod_info = _get_product_info(str(pid), cuponera_site_ids)
                        if prod_info:
                            prods.append(prod_info)
                    if prods:
                        discount_products_info = prods
            
            # BUY_X_GET_Y_PERCENT_OFF: puede tener scope por categoría o producto
            elif discount_type == "BUY_X_GET_Y_PERCENT_OFF":
                scope_type = scope.get("scope_type") or ""
                category_ids = scope.get("category_ids") or []
                product_ids_scope = scope.get("product_ids") or []
                if scope_type == "CATEGORY_IDS" and category_ids:
                    discount_categories_info = _get_categories_info(category_ids, cuponera_site_ids)
                if product_ids_scope:
                    prods = []
                    for pid in product_ids_scope:
                        prod_info = _get_product_info(str(pid), cuponera_site_ids)
                        if prod_info:
                            prods.append(prod_info)
                    if prods:
                        discount_products_info = prods
            # Si es descuento por PRODUCTO, obtener info de los productos
            elif discount_type in ("PRODUCT_PERCENT_OFF", "PRODUCT_AMOUNT_OFF"):
                product_ids = scope.get("product_ids") or []
                if product_ids:
                    prods = []
                    for pid in product_ids:
                        prod_info = _get_product_info(str(pid), cuponera_site_ids)
                        if prod_info:
                            prods.append(prod_info)
                    if prods:
                        discount_products_info = prods

    # Normalizar tipos por si MongoDB/JSON devuelve otro tipo
    uses_per_day = int(cuponera.get("uses_per_day") or 1)
    cuponera_id_str = str(cuponera_id or "")
    today_str = str(today or "")

    usage_list = read_cuponera_usage()
    current_count = 0
    for rec in usage_list:
        rec_cid = str(rec.get("cuponera_id") or "")
        rec_code = (rec.get("user_code") or "").strip().upper()
        rec_date = str(rec.get("date") or "")
        if rec_cid == cuponera_id_str and rec_code == code_upper and rec_date == today_str:
            current_count = int(rec.get("uses_count") or 0)
            break

    uses_remaining = max(0, uses_per_day - current_count)

    if record_use and uses_remaining > 0:
        # Incrementar uso
        found = False
        for rec in usage_list:
            rec_cid = str(rec.get("cuponera_id") or "")
            rec_code = (rec.get("user_code") or "").strip().upper()
            rec_date = str(rec.get("date") or "")
            if rec_cid == cuponera_id_str and rec_code == code_upper and rec_date == today_str:
                rec["uses_count"] = int(rec.get("uses_count") or 0) + 1
                found = True
                break
        if not found:
            usage_list.append({
                "cuponera_id": cuponera_id_str,
                "user_code": code_upper,
                "date": today_str,
                "uses_count": 1,
            })
        write_cuponera_usage(usage_list)
        uses_remaining = max(0, uses_remaining - 1)

    return RedeemResponse(
        success=True,
        message="Descuentos del día.",
        cuponera_name=cuponera.get("name"),
        discounts=discounts_for_day,
        uses_remaining_today=uses_remaining,
        user=user_info,
        cuponera_site_ids=cuponera_site_ids,
        free_product=free_product_info,
        discount_categories=discount_categories_info,
        discount_products=discount_products_info,
    )
