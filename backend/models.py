"""Modelos Pydantic para la API."""
from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, EmailStr, field_validator
import phonenumbers


# --- Site (solo lectura desde API) ---
class Site(BaseModel):
    site_id: int
    site_name: str
    site_address: Optional[str] = None
    site_phone: Optional[str] = None
    city_name: Optional[str] = None
    country_name: Optional[str] = None
    show_on_web: bool = True


# --- Scope para descuentos (según discounts_example) ---
class Scope(BaseModel):
    scope_type: str = "ALL_ITEMS"  # ALL_ITEMS | CATEGORY_IDS | PRODUCT_IDS
    category_ids: list[str] = Field(default_factory=list)
    product_ids: list[str] = Field(default_factory=list)
    exclude_category_ids: list[str] = Field(default_factory=list)
    exclude_product_ids: list[str] = Field(default_factory=list)


# --- Discount rule (regla de descuento) ---
class DiscountRule(BaseModel):
    id: str
    type: str  # CART_PERCENT_OFF, CART_AMOUNT_OFF, FREE_ITEM, BUY_M_PAY_N, CATEGORY_PERCENT_OFF, BUY_X_GET_Y_PERCENT_OFF
    name: str
    priority: int = 0
    stacking_policy: dict = Field(default_factory=lambda: {"mode": "EXCLUSIVE", "exclusive_group": "default"})
    scope: Scope = Field(default_factory=Scope)
    conditions: dict = Field(default_factory=dict)
    params: dict = Field(default_factory=dict)
    limits: dict = Field(default_factory=dict)
    selection_rule: str = "CHEAPEST_UNITS"
    apply_as: str = "CART_LEVEL"
    audit: dict = Field(default_factory=dict)
    # Sedes donde aplica: null = todas, si no lista de site_id
    site_ids: Optional[list[int]] = None
    folder: Optional[str] = None  # Carpeta para agrupar (ej. "Promos Febrero")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class DiscountRuleCreate(BaseModel):
    type: str
    name: str = Field(..., min_length=1, description="Nombre obligatorio del descuento")
    priority: int = 0
    stacking_policy: dict = Field(default_factory=lambda: {"mode": "EXCLUSIVE", "exclusive_group": "default"})
    scope: Scope = Field(default_factory=Scope)
    conditions: dict = Field(default_factory=dict)
    params: dict = Field(default_factory=dict)
    limits: dict = Field(default_factory=dict)
    selection_rule: str = "CHEAPEST_UNITS"
    apply_as: str = "CART_LEVEL"
    audit: dict = Field(default_factory=dict)
    site_ids: Optional[list[int]] = None
    folder: Optional[str] = None


class DiscountRuleUpdate(BaseModel):
    type: Optional[str] = None
    name: Optional[str] = Field(None, min_length=1)
    priority: Optional[int] = None
    stacking_policy: Optional[dict] = None
    scope: Optional[Scope] = None
    conditions: Optional[dict] = None
    params: Optional[dict] = None
    limits: Optional[dict] = None
    selection_rule: Optional[str] = None
    apply_as: Optional[str] = None
    audit: Optional[dict] = None
    site_ids: Optional[list[int]] = None
    folder: Optional[str] = None


# --- Cuponera ---
class Cuponera(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    uses_per_day: int = 1  # cuántas veces puede usar el descuento por día cada usuario
    # Calendario: "YYYY-MM-DD" -> [discount_id, ...]
    calendar: dict[str, list[str]] = Field(default_factory=dict)
    # Sedes donde aplica la cuponera: null = todas
    site_ids: Optional[list[int]] = None
    folder: Optional[str] = None  # Carpeta para agrupar (ej. "2026 / Eventos")
    active: bool = True
    # Vigencia: si se definen, el canje solo es válido entre estas fechas (YYYY-MM-DD)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class CuponeraCreate(BaseModel):
    name: str
    description: Optional[str] = None
    uses_per_day: int = 1
    calendar: dict[str, list[str]] = Field(default_factory=dict)
    site_ids: Optional[list[int]] = None
    folder: Optional[str] = None
    active: bool = True
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class CuponeraUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    uses_per_day: Optional[int] = None
    calendar: Optional[dict[str, list[str]]] = None
    site_ids: Optional[list[int]] = None
    folder: Optional[str] = None
    active: Optional[bool] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


# --- Folder (carpeta para agrupar descuentos y cuponeras) ---
class Folder(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    sort_order: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class FolderCreate(BaseModel):
    name: str
    description: Optional[str] = None
    sort_order: Optional[int] = None


class FolderUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None


# --- Usuario de cuponera ---
class CuponeraUser(BaseModel):
    id: str
    cuponera_id: str
    code: str  # código único para canjear
    name: str  # Nombre completo (se mantiene para compatibilidad)
    first_name: Optional[str] = None  # Nuevo: nombre separado
    last_name: Optional[str] = None   # Nuevo: apellido separado
    phone: str
    phone_code: Optional[str] = None  # Nuevo: código de país del teléfono (ej. "+57")
    email: str
    address: Optional[str] = None
    created_at: Optional[str] = None


class CuponeraUserCreate(BaseModel):
    cuponera_id: Optional[str] = None  # opcional si se pasa en la URL
    code: Optional[str] = None  # opcional: si no se envía, el sistema lo genera; no se permiten duplicados en cuponeras vigentes
    first_name: str = Field(..., min_length=1, description="Nombre del usuario")
    last_name: str = Field(..., min_length=1, description="Apellido del usuario")
    phone: str = Field(..., min_length=1, description="Teléfono del usuario")
    phone_code: str = Field(default="+57", description="Código de país del teléfono (ej. +57, +1). Por defecto +57 (Colombia)")
    email: EmailStr = Field(..., description="Email del usuario")
    address: Optional[str] = None
    
    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v):
        """Validar formato de email."""
        if not v or not isinstance(v, str):
            raise ValueError('El email es obligatorio')
        email_str = v.strip()
        if '@' not in email_str or '.' not in email_str.split('@')[-1]:
            raise ValueError('Email inválido. Debe tener formato: ejemplo@dominio.com')
        return email_str
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v, info):
        """Validar que el teléfono coincida con el código de país."""
        if not v or not isinstance(v, str):
            raise ValueError('El teléfono es obligatorio')
        
        phone = v.strip()
        # Validar que solo contenga dígitos (y opcionalmente espacios/guiones que luego se eliminan)
        phone_cleaned = phone.replace(' ', '').replace('-', '')
        if not phone_cleaned.isdigit():
            raise ValueError('El teléfono solo debe contener números (sin letras ni caracteres especiales)')
        
        # Obtener phone_code del contexto de validación
        phone_code = info.data.get('phone_code', '+57')
        
        try:
            # Si ya tiene +, parsear en formato E.164; si no, anteponer phone_code
            if phone_cleaned.startswith('+'):
                parsed = phonenumbers.parse(phone_cleaned, None)
            else:
                parsed = phonenumbers.parse(f"{phone_code}{phone_cleaned}", None)
            
            # Usar is_possible_number (más tolerante) o is_valid_number
            if phonenumbers.is_valid_number(parsed):
                return phone_cleaned
            if phonenumbers.is_possible_number(parsed):
                return phone_cleaned
            # Colombia (+57): aceptar 9-10 dígitos que empiecen con 3 (móviles sin 0 inicial)
            if phone_code in ('+57', '57') and 9 <= len(phone_cleaned) <= 10 and phone_cleaned.startswith('3'):
                return phone_cleaned
            raise ValueError(f'Número de teléfono inválido para el código de país {phone_code}. Colombia: 10 dígitos, empezando con 3 (ej. 3226893988)')
        except phonenumbers.NumberParseException:
            # Si falla el parse, verificar formato básico para Colombia
            if phone_code in ('+57', '57') and 9 <= len(phone_cleaned) <= 10 and phone_cleaned.startswith('3'):
                return phone_cleaned
            raise ValueError(f'Formato de teléfono inválido para el código de país {phone_code}')


class CuponeraUserUpdate(BaseModel):
    """Campos opcionales para actualizar un usuario de cuponera."""
    code: Optional[str] = None
    first_name: Optional[str] = Field(None, min_length=1)
    last_name: Optional[str] = Field(None, min_length=1)
    phone: Optional[str] = Field(None, min_length=1)
    phone_code: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    
    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v):
        """Validar formato de email si se proporciona."""
        if v is None:
            return v
        if not isinstance(v, str):
            raise ValueError('Email debe ser texto')
        email_str = v.strip()
        if not email_str:
            return None
        if '@' not in email_str or '.' not in email_str.split('@')[-1]:
            raise ValueError('Email inválido. Debe tener formato: ejemplo@dominio.com')
        return email_str
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v, info):
        """Validar que el teléfono coincida con el código de país si se proporciona."""
        if v is None:
            return v
        if not isinstance(v, str):
            raise ValueError('Teléfono debe ser texto')
        
        phone = v.strip()
        if not phone:
            return None
        
        # Validar que solo contenga dígitos (y opcionalmente espacios/guiones)
        phone_cleaned = phone.replace(' ', '').replace('-', '')
        if not phone_cleaned.isdigit():
            raise ValueError('El teléfono solo debe contener números (sin letras ni caracteres especiales)')
            
        # Obtener phone_code del contexto
        phone_code = info.data.get('phone_code')
        if not phone_code:
            # Si no se está actualizando phone_code, no podemos validar aquí
            # La validación se hará en el router con el código existente
            return phone_cleaned
        
        try:
            if phone_cleaned.startswith('+'):
                parsed = phonenumbers.parse(phone_cleaned, None)
            else:
                parsed = phonenumbers.parse(f"{phone_code}{phone_cleaned}", None)
            
            if phonenumbers.is_valid_number(parsed) or phonenumbers.is_possible_number(parsed):
                return phone_cleaned
            if phone_code in ('+57', '57') and 9 <= len(phone_cleaned) <= 10 and phone_cleaned.startswith('3'):
                return phone_cleaned
            raise ValueError(f'Número de teléfono inválido para el código de país {phone_code}')
        except phonenumbers.NumberParseException:
            if phone_code in ('+57', '57') and 9 <= len(phone_cleaned) <= 10 and phone_cleaned.startswith('3'):
                return phone_cleaned
            raise ValueError(f'Formato de teléfono inválido para el código de país {phone_code}')


# --- Uso del cupón (registro por día) ---
class CuponeraUsageRecord(BaseModel):
    cuponera_id: str
    user_code: str
    date: str  # YYYY-MM-DD
    uses_count: int = 0


# --- Respuesta canjear código ---
class RedeemDiscountItem(BaseModel):
    discount: dict[str, Any]
    discount_id: str


class RedeemUserInfo(BaseModel):
    """Datos del usuario de cuponera para auto-completar formularios (p. ej. en pago)."""
    name: str  # Nombre completo (se mantiene para compatibilidad)
    first_name: Optional[str] = None  # Nuevo: nombre separado
    last_name: Optional[str] = None   # Nuevo: apellido separado
    phone: str
    phone_code: Optional[str] = None  # Nuevo: código de país (ej. "+57")
    email: str
    address: Optional[str] = None


class RedeemResponse(BaseModel):
    success: bool
    message: str
    cuponera_name: Optional[str] = None
    discounts: list[RedeemDiscountItem] = Field(default_factory=list)
    uses_remaining_today: Optional[int] = None  # cuántas veces puede usar aún hoy
    user: Optional[RedeemUserInfo] = None  # datos del usuario si el código es válido (para auto-completar)
    cuponera_site_ids: Optional[list[int]] = None  # sedes donde aplica la cuponera; null = todas
    free_product: Optional[dict[str, Any]] = None  # info del producto gratis si el descuento es FREE_ITEM
    discount_categories: Optional[list[dict[str, Any]]] = None  # info de categorías si el descuento es CATEGORY_*
    discount_products: Optional[list[dict[str, Any]]] = None  # info de productos si el descuento es PRODUCT_*
