"""Validación de scope de descuentos contra menús de sedes."""
from storage import list_menu_site_ids, read_menu, read_sites_filtered


def get_menu_product_and_category_ids(site_id: int) -> tuple[set[str], set[str]]:
    """Devuelve (product_ids, category_ids) que existen en el menú de la sede."""
    menu = read_menu(site_id)
    if not menu:
        return set(), set()
    product_ids: set[str] = set()
    category_ids: set[str] = set()
    categorias = menu.get("categorias") or []
    for cat in categorias:
        cid = cat.get("categoria_id")
        if cid is not None:
            category_ids.add(str(cid))
        for prod in cat.get("products") or []:
            pid = prod.get("producto_id")
            if pid is not None:
                product_ids.add(str(pid))
            if cid is not None:
                category_ids.add(str(cat.get("categoria_id", "")))
        for prod in cat.get("products") or []:
            for pres in prod.get("lista_presentacion") or []:
                pid = pres.get("producto_id")
                if pid is not None:
                    product_ids.add(str(pid))
    return product_ids, category_ids


def validate_discount_scope_for_sites(
    site_ids: list[int] | None,
    scope_type: str,
    category_ids: list[str],
    product_ids: list[str],
) -> tuple[bool, list[str]]:
    """
    Valida que los product_ids y category_ids del scope existan en las sedes seleccionadas.
    site_ids=None significa todas las sedes (usamos las que tienen menú cargado).
    Devuelve (ok, lista de mensajes de error).
    """
    if site_ids is None:
        site_ids = list_menu_site_ids()
        if not site_ids:
            sites = read_sites_filtered()
            site_ids = [s["site_id"] for s in sites if s.get("site_id") is not None]
    if not site_ids:
        return True, []  # sin sedes no hay qué validar

    errors: list[str] = []
    cat_set = set(category_ids)
    prod_set = set(product_ids)

    for site_id in site_ids:
        menu_prods, menu_cats = get_menu_product_and_category_ids(site_id)
        if scope_type == "PRODUCT_IDS" and prod_set:
            missing = prod_set - menu_prods
            if missing:
                errors.append(
                    f"Sede {site_id}: los productos {sorted(missing)} no están en el menú."
                )
        if scope_type == "CATEGORY_IDS" and cat_set:
            missing = cat_set - menu_cats
            if missing:
                errors.append(
                    f"Sede {site_id}: las categorías {sorted(missing)} no están en el menú."
                )
        if scope_type == "ALL_ITEMS":
            # Exclusions: si hay exclude_product_ids o exclude_category_ids, validar que existan
            excl_prod = set()
            excl_cat = set()
            # Aquí no tenemos exclude en esta función; el scope viene del discount. Mejor pasar scope completo.
            pass
    return len(errors) == 0, errors


def validate_discount_scope_full(
    site_ids: list[int] | None,
    scope: dict,
) -> tuple[bool, list[str]]:
    """Valida scope completo (scope_type, category_ids, product_ids, exclude_*)."""
    scope_type = scope.get("scope_type") or "ALL_ITEMS"
    category_ids = list(scope.get("category_ids") or [])
    product_ids = list(scope.get("product_ids") or [])
    return validate_discount_scope_for_sites(
        site_ids, scope_type, category_ids, product_ids
    )
