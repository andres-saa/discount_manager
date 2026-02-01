"""Catálogo de categorías y productos desde menús (para selects validados por backend)."""
from storage import read_menu, read_sites_filtered


def _normalize_id(value) -> str:
    return str(value) if value is not None else ""


def _product_name(prod: dict) -> str:
    return (prod.get("producto_descripcion") or prod.get("english_name") or "").strip() or _normalize_id(prod.get("producto_id"))


def _category_name(cat: dict) -> str:
    return (cat.get("categoria_descripcion") or cat.get("english_name") or "").strip() or _normalize_id(cat.get("categoria_id"))


def _site_ids_resolved(site_ids: list[int] | None) -> list[int]:
    if site_ids is not None and len(site_ids) > 0:
        return site_ids
    return [s["site_id"] for s in read_sites_filtered() if s.get("site_id") is not None]


def get_categories(site_ids: list[int] | None = None) -> list[dict]:
    """Lista única de categorías (id, name) de los menús de las sedes indicadas."""
    resolved = _site_ids_resolved(site_ids)
    seen: set[str] = set()
    out: list[dict] = []
    for site_id in resolved:
        menu = read_menu(site_id)
        if not menu:
            continue
        for cat in menu.get("categorias") or []:
            cid = _normalize_id(cat.get("categoria_id"))
            if not cid or cid in seen:
                continue
            seen.add(cid)
            out.append({"id": cid, "name": _category_name(cat)})
    out.sort(key=lambda x: (x["name"].lower(), x["id"]))
    return out


def get_products(
    site_ids: list[int] | None = None,
    q: str | None = None,
    limit: int = 20,
    offset: int = 0,
    ids_to_include: list[str] | None = None,
) -> tuple[list[dict], int]:
    """
    Lista de productos (id, name, category_id) de los menús de las sedes.
    q: búsqueda en nombre/descripción (case-insensitive).
    ids_to_include: ids que deben aparecer en la respuesta (p. ej. ya seleccionados).
    Devuelve (items, total_count).
    """
    resolved = _site_ids_resolved(site_ids)
    q_clean = (q or "").strip().lower()
    # Recolectar todos los productos de las sedes (por sitio, pueden repetirse producto_id)
    all_products: dict[str, dict] = {}
    for site_id in resolved:
        menu = read_menu(site_id)
        if not menu:
            continue
        for cat in menu.get("categorias") or []:
            cid = _normalize_id(cat.get("categoria_id"))
            for prod in cat.get("products") or []:
                pid = _normalize_id(prod.get("producto_id"))
                if not pid:
                    continue
                name = _product_name(prod)
                if pid not in all_products:
                    all_products[pid] = {"id": pid, "name": name, "category_id": cid}
            for prod in cat.get("products") or []:
                for pres in prod.get("lista_presentacion") or []:
                    pid = _normalize_id(pres.get("producto_id"))
                    if not pid:
                        continue
                    if pid not in all_products:
                        name = _product_name(prod) or pid
                        all_products[pid] = {"id": pid, "name": name, "category_id": cid}

    # Incluir siempre los ids_to_include (pueden no estar en all_products si son de otra sede)
    if ids_to_include:
        for pid in ids_to_include:
            pid = _normalize_id(pid)
            if pid and pid not in all_products:
                all_products[pid] = {"id": pid, "name": pid, "category_id": ""}

    items_list = list(all_products.values())
    if q_clean:
        items_list = [p for p in items_list if q_clean in (p.get("name") or "").lower()]
    total = len(items_list)
    items_list.sort(key=lambda x: (x.get("name") or "").lower())
    page = items_list[offset : offset + limit]
    return page, total
    
    # Recolectar todos los productos de las sedes (por sitio, pueden repetirse producto_id)
    all_products: dict[str, dict] = {}
    for site_id in resolved:
        menu = read_menu(site_id)
        if not menu:
            continue
        for cat in menu.get("categorias") or []:
            cid = _normalize_id(cat.get("categoria_id"))
            for prod in cat.get("products") or []:
                pid = _normalize_id(prod.get("producto_id"))
                if not pid:
                    continue
                name = _product_name(prod)
                if pid not in all_products:
                    all_products[pid] = {"id": pid, "name": name, "category_id": cid}
            for prod in cat.get("products") or []:
                for pres in prod.get("lista_presentacion") or []:
                    pid = _normalize_id(pres.get("producto_id"))
                    if not pid:
                        continue
                    if pid not in all_products:
                        name = _product_name(prod) or pid
                        all_products[pid] = {"id": pid, "name": name, "category_id": cid}

    # Incluir siempre los all_ids_to_include (pueden no estar en all_products si son de otra sede)
    if all_ids_to_include:
        for pid in all_ids_to_include:
            pid = _normalize_id(pid)
            if pid and pid not in all_products:
                all_products[pid] = {"id": pid, "name": pid, "category_id": ""}

    items_list = list(all_products.values())
    if q_clean:
        items_list = [p for p in items_list if q_clean in (p.get("name") or "").lower()]
    total = len(items_list)
    items_list.sort(key=lambda x: (x.get("name") or "").lower())
    page = items_list[offset : offset + limit]
    return page, total
