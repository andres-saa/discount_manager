"""Validación por tipo de descuento: params, scope, conditions, limits requeridos."""
from typing import Any


def validate_discount_by_type(
    discount_type: str,
    params: dict,
    scope: dict,
    conditions: dict,
    limits: dict,
    selection_rule: str | None = None,
) -> tuple[bool, list[str]]:
    """
    Valida que para cada tipo de descuento estén los campos correctos.
    Devuelve (ok, lista de mensajes de error).
    """
    errors: list[str] = []
    scope_type = (scope or {}).get("scope_type") or "ALL_ITEMS"
    category_ids = list((scope or {}).get("category_ids") or [])
    product_ids = list((scope or {}).get("product_ids") or [])

    if discount_type == "CART_PERCENT_OFF":
        if params.get("pct") is None:
            errors.append("Debe indicar el porcentaje de descuento (params.pct).")
        else:
            pct = params.get("pct")
            if not isinstance(pct, (int, float)) or pct < 0 or pct > 100:
                errors.append("El porcentaje (pct) debe estar entre 0 y 100.")

    elif discount_type == "CART_AMOUNT_OFF":
        if params.get("amount") is None:
            errors.append("Debe indicar el valor del descuento (params.amount).")
        else:
            amt = params.get("amount")
            if not isinstance(amt, (int, float)) or amt <= 0:
                errors.append("El valor del descuento (amount) debe ser mayor que 0.")

    elif discount_type == "FREE_ITEM":
        free_item = params.get("free_item") or {}
        mode = free_item.get("mode") or "CHEAPEST_IN_SCOPE"
        if mode == "SPECIFIC_PRODUCT" and not free_item.get("product_id"):
            errors.append("En modo producto específico debe elegir el producto gratis (free_item.product_id).")
        req = (params.get("requires_purchase") or conditions.get("requires_purchase")) or {}
        req_type = req.get("type") or "NONE"
        if req_type == "MIN_SUBTOTAL_IN_SCOPE" and req.get("min_subtotal") is None:
            errors.append("Requisito de compra: indique subtotal mínimo (min_subtotal).")
        if req_type == "MIN_QTY_IN_SCOPE" and req.get("min_qty") is None:
            errors.append("Requisito de compra: indique cantidad mínima (min_qty).")
        if req_type == "BUY_X_IN_SCOPE":
            buy_x = req.get("buy_x")
            if buy_x is None or not isinstance(buy_x, (int, float)) or buy_x < 1:
                errors.append("Requisito de compra (Compra X unidades): indique X (buy_x >= 1).")
        max_free = limits.get("max_free_qty")
        if max_free is None or (isinstance(max_free, (int, float)) and max_free < 1):
            errors.append("Debe indicar límite de cantidad gratis (limits.max_free_qty >= 1).")
        if scope_type == "PRODUCT_IDS" and not product_ids:
            errors.append("Seleccione al menos un producto en el scope (compra estos).")
        elif scope_type == "CATEGORY_IDS" and not category_ids:
            errors.append("Seleccione al menos una categoría en el scope.")

    elif discount_type == "BUY_M_PAY_N":
        m = params.get("m")
        n = params.get("n")
        if m is None or not isinstance(m, (int, float)) or m < 1:
            errors.append("Debe indicar M (params.m >= 1): lleva M unidades.")
        if n is None or not isinstance(n, (int, float)) or n < 0 or (m is not None and n >= m):
            errors.append("Debe indicar N (params.n): paga N de cada M (0 <= N < M).")
        if scope_type == "PRODUCT_IDS" and not product_ids:
            errors.append("Seleccione los productos a los que aplica (compra estos, lleva M paga N).")
        if scope_type == "CATEGORY_IDS" and not category_ids:
            errors.append("Seleccione las categorías a los que aplica.")
        # Requisito de compra mínima (opcional pero recomendado)
        min_sub = conditions.get("min_subtotal")
        if min_sub is not None and (not isinstance(min_sub, (int, float)) or min_sub < 0):
            errors.append("Si indica requisito de compra mínima (conditions.min_subtotal), debe ser >= 0.")

    elif discount_type == "CATEGORY_PERCENT_OFF":
        if params.get("pct") is None:
            errors.append("Debe indicar el porcentaje de descuento (params.pct).")
        else:
            pct = params.get("pct")
            if not isinstance(pct, (int, float)) or pct < 0 or pct > 100:
                errors.append("El porcentaje (pct) debe estar entre 0 y 100.")
        if scope_type != "CATEGORY_IDS":
            errors.append("Este tipo requiere scope por categorías (scope_type CATEGORY_IDS).")
        if not category_ids:
            errors.append("Seleccione al menos una categoría.")

    elif discount_type == "BUY_X_GET_Y_PERCENT_OFF":
        x = params.get("x")
        y = params.get("y")
        y_pct = params.get("y_discount_pct")
        if x is None or not isinstance(x, (int, float)) or x < 1:
            errors.append("Debe indicar X (params.x >= 1): compra X.")
        if y is None or not isinstance(y, (int, float)) or y < 1:
            errors.append("Debe indicar Y (params.y >= 1): obtén Y con descuento.")
        if y_pct is None or not isinstance(y_pct, (int, float)) or y_pct < 0 or y_pct > 100:
            errors.append("Debe indicar el porcentaje de descuento en Y (params.y_discount_pct 0-100).")
        if scope_type == "PRODUCT_IDS" and not product_ids:
            errors.append("Seleccione los productos a los que aplica.")
        if scope_type == "CATEGORY_IDS" and not category_ids:
            errors.append("Seleccione las categorías a los que aplica.")

    return len(errors) == 0, errors
