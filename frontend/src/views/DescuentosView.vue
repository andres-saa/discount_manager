<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Dropdown from 'primevue/dropdown'
import MultiSelect from 'primevue/multiselect'
import Message from 'primevue/message'
import { useToast } from 'primevue/usetoast'
import { api } from '../api'

/** Tipos para el formulario de descuento (params/conditions/limits con campos usados por InputNumber y Dropdown) */
interface FreeItemParams {
  mode?: string
  product_id?: string
}
interface RequiresPurchase {
  type?: string
  min_subtotal?: number | null
  min_qty?: number | null
  buy_x?: number | null
}
interface DiscountParams {
  pct?: number | null
  amount?: number | null
  free_item?: FreeItemParams
  m?: number | null
  n?: number | null
  x?: number | null
  y?: number | null
  y_discount_pct?: number | null
  [key: string]: unknown
}
interface DiscountConditions {
  min_subtotal?: number | null
  requires_purchase?: RequiresPurchase
  min_qty_in_category?: number | null
  min_subtotal_in_category?: number | null
  [key: string]: unknown
}
interface DiscountLimits {
  max_discount_amount?: number | null
  max_free_qty?: number | null
  max_groups?: number | null
  [key: string]: unknown
}

const toast = useToast()

const discounts = ref<Array<Record<string, unknown>>>([])
const sites = ref<Array<Record<string, unknown>>>([])
const folders = ref<Array<Record<string, unknown>>>([])
const loading = ref(true)
const dialogVisible = ref(false)
const editingId = ref<string | null>(null)
const error = ref('')
const form = ref<{
  type: string
  name: string
  priority: number
  scope: { scope_type: string; category_ids: string[]; product_ids: string[]; exclude_category_ids: string[]; exclude_product_ids: string[] }
  conditions: DiscountConditions
  params: DiscountParams
  limits: DiscountLimits
  selection_rule: string
  site_ids: number[] | null
  folder: string
}>({
  type: 'CART_PERCENT_OFF',
  name: '',
  priority: 0,
  scope: { scope_type: 'ALL_ITEMS', category_ids: [], product_ids: [], exclude_category_ids: [], exclude_product_ids: [] },
  conditions: {},
  params: {},
  limits: {},
  selection_rule: 'CHEAPEST_UNITS',
  site_ids: null,
  folder: '',
})

// Opciones para selects (validadas por backend)
const categoryOptions = ref<Array<{ id: string; name: string }>>([])
const categoryOptionsLoading = ref(false)
const productOptions = ref<Array<{ id: string; name: string; category_id: string }>>([])
const productOptionsLoading = ref(false)
const productFilterQuery = ref('')

const typeOptions = [
  { label: '% descuento carrito', value: 'CART_PERCENT_OFF' },
  { label: 'Valor fijo carrito', value: 'CART_AMOUNT_OFF' },
  { label: 'Producto gratis', value: 'FREE_ITEM' },
  { label: 'M x N (paga N lleva M)', value: 'BUY_M_PAY_N' },
  { label: '% categoría', value: 'CATEGORY_PERCENT_OFF' },
  { label: 'Compra X obtén Y %', value: 'BUY_X_GET_Y_PERCENT_OFF' },
]
const scopeTypeOptions = [
  { label: 'Todos los ítems', value: 'ALL_ITEMS' },
  { label: 'Categorías', value: 'CATEGORY_IDS' },
  { label: 'Productos', value: 'PRODUCT_IDS' },
]
const selectionRuleOptions = [
  { label: 'Más baratos primero', value: 'CHEAPEST_UNITS' },
  { label: 'Más caros primero', value: 'MOST_EXPENSIVE_UNITS' },
]
const freeItemModeOptions = [
  { label: 'El más barato del scope', value: 'CHEAPEST_IN_SCOPE' },
  { label: 'Producto específico', value: 'SPECIFIC_PRODUCT' },
]
const requiresPurchaseTypeOptions = [
  { label: 'Ninguno', value: 'NONE' },
  { label: 'Subtotal mínimo (scope)', value: 'MIN_SUBTOTAL_IN_SCOPE' },
  { label: 'Cantidad mínima (scope)', value: 'MIN_QTY_IN_SCOPE' },
  { label: 'Compra X unidades', value: 'BUY_X_IN_SCOPE' },
]

// Descripciones de cada tipo de descuento (para mostrar al crear/editar)
const typeDescriptions: Record<string, string> = {
  CART_PERCENT_OFF: 'Descuento en porcentaje sobre el total del carrito. Ej: 10% de descuento en toda la compra. Puede limitarse a un tope en COP y exigir compra mínima.',
  CART_AMOUNT_OFF: 'Descuento de un valor fijo en COP sobre el total del carrito. Ej: $5.000 de descuento. Opcionalmente exige compra mínima.',
  FREE_ITEM: 'Regala uno o más productos: el más barato de una categoría/productos, o un producto específico. Puede exigir compra mínima (subtotal o cantidad) para activarse.',
  BUY_M_PAY_N: 'En categorías, productos o todo: compra M lleva N del mismo producto. Por cada M unidades de un mismo producto, el cliente paga N. No se mezclan productos (3 de un artículo + 2 de otro no forman grupo).',
  CATEGORY_PERCENT_OFF: 'Descuento en porcentaje solo sobre productos de ciertas categorías. El cliente debe llevar productos de esas categorías; el % aplica sobre ellos (con opcional tope en COP).',
  BUY_X_GET_Y_PERCENT_OFF: 'En categorías, productos o todo: compra X lleva Y del mismo producto con % de descuento. Por cada X unidades de un mismo producto, obtén Y con el % indicado. Ej: compra 2 lleva 1 al 50%.',
}
const typeDescription = computed(() => typeDescriptions[form.value.type] || '')

// Nombres reales del scope seleccionado (para el ejemplo debajo de lleva/compra)
const scopeSelectedNames = computed(() => {
  const scope = form.value.scope
  if (scope.scope_type === 'CATEGORY_IDS' && scope.category_ids?.length) {
    const ids = new Set(scope.category_ids)
    return categoryOptions.value.filter((c) => ids.has(c.id)).map((c) => c.name)
  }
  if (scope.scope_type === 'PRODUCT_IDS' && scope.product_ids?.length) {
    const ids = new Set(scope.product_ids)
    return productOptions.value.filter((p) => ids.has(p.id)).map((p) => p.name)
  }
  return []
})
const scopeExampleText = computed(() => {
  const names = scopeSelectedNames.value
  if (!names.length) return ''
  const list = names.slice(0, 5).join(', ') + (names.length > 5 ? ` y ${names.length - 5} más` : '')
  const t = form.value.type
  if (t === 'BUY_M_PAY_N') {
    const m = form.value.params.m ?? 3
    const n = form.value.params.n ?? 2
    return `Ej: Lleva ${m} paga ${n} en: ${list}.`
  }
  if (t === 'BUY_X_GET_Y_PERCENT_OFF') {
    const x = form.value.params.x ?? 2
    const y = form.value.params.y ?? 1
    const pct = form.value.params.y_discount_pct ?? 50
    return `Ej: Compra ${x} lleva ${y} al ${pct}% en: ${list}.`
  }
  if (t === 'FREE_ITEM') return `Ej: Producto gratis al comprar: ${list}.`
  if (t === 'CATEGORY_PERCENT_OFF') {
    const pct = form.value.params.pct ?? 10
    return `Ej: ${pct}% de descuento en: ${list}.`
  }
  return `Aplica a: ${list}.`
})

const filterFolder = ref<string | null>(null)
const folderOptions = computed(() => {
  const list = (folders.value || []).map((f) => ({ name: (f.name as string) || '', label: (f.name as string) || '' }))
  return [{ name: '', label: 'Sin carpeta' }, ...list]
})
const discountFolders = computed(() => {
  const set = new Set<string>()
  for (const d of discounts.value) {
    const f = (d.folder as string) ?? ''
    set.add(f)
  }
  return Array.from(set).sort((a, b) => (a === '' ? -1 : b === '' ? 1 : a.localeCompare(b)))
})
const discountsGroupedByFolder = computed(() => {
  const groups: Record<string, Array<Record<string, unknown>>> = {}
  for (const d of discounts.value) {
    const f = (d.folder as string) ?? ''
    if (filterFolder.value !== null && f !== filterFolder.value) continue
    if (!groups[f]) groups[f] = []
    groups[f].push(d)
  }
  return discountFolders.value
    .filter((f) => filterFolder.value === null || f === filterFolder.value)
    .map((f) => ({ folder: f, items: groups[f] || [] }))
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [d, s, f] = await Promise.all([api.discounts.list(), api.sites.list(), api.folders.list()])
    discounts.value = d
    sites.value = s
    folders.value = f
  } catch (e) {
    const message = getErrorMessage(e)
    error.value = message
    toast.add({ severity: 'error', summary: 'Error al cargar', detail: message, life: 8000 })
  } finally {
    loading.value = false
  }
}

async function loadCategoryOptions() {
  categoryOptionsLoading.value = true
  try {
    const list = await api.menus.categories(form.value.site_ids ?? null)
    categoryOptions.value = list
  } catch {
    categoryOptions.value = []
  } finally {
    categoryOptionsLoading.value = false
  }
}

async function loadProductOptions(searchQ?: string) {
  productOptionsLoading.value = true
  try {
    const q = searchQ ?? productFilterQuery.value
    let ids: string[] = form.value.scope.product_ids?.length ? [...form.value.scope.product_ids] : []
    const freeItem = form.value.params.free_item
    if (form.value.type === 'FREE_ITEM' && freeItem?.product_id)
      ids = [...new Set([...ids, freeItem.product_id])]
    const idsParam = ids.length ? ids : undefined
    const res = await api.menus.products({
      site_ids: form.value.site_ids ?? null,
      q: q || undefined,
      limit: undefined, // Sin límite = cargar todos los productos
      offset: undefined,
      ids: idsParam,
    })
    productOptions.value = res.items
  } catch {
    productOptions.value = []
  } finally {
    productOptionsLoading.value = false
  }
}

function onProductFilter(event: { value?: string } | string) {
  const query = (typeof event === 'string' ? event : event?.value ?? '').trim()
  productFilterQuery.value = query
  const local = query
    ? productOptions.value.filter((p) => (p.name || '').toLowerCase().includes(query.toLowerCase()))
    : productOptions.value
  if (local.length > 0) return
  if (query.length >= 2) {
    loadProductOptions(query)
  } else if (!query) {
    loadProductOptions('')
  }
}

watch(
  () => form.value.site_ids,
  () => {
    if (!dialogVisible.value) return
    if (form.value.scope.scope_type === 'CATEGORY_IDS') loadCategoryOptions()
    if (form.value.scope.scope_type === 'PRODUCT_IDS') loadProductOptions()
  },
  { deep: true }
)

watch(
  () => form.value.scope.scope_type,
  (type) => {
    if (!dialogVisible.value) return
    if (type === 'CATEGORY_IDS') loadCategoryOptions()
    if (type === 'PRODUCT_IDS') loadProductOptions()
  }
)

const ALL_ITEMS_SCOPE = { scope_type: 'ALL_ITEMS', category_ids: [] as string[], product_ids: [] as string[], exclude_category_ids: [] as string[], exclude_product_ids: [] as string[] }

watch(
  () => form.value.type,
  (type) => {
    if (type === 'CART_PERCENT_OFF' || type === 'CART_AMOUNT_OFF') {
      form.value.scope = { ...ALL_ITEMS_SCOPE }
    }
    if (type === 'CATEGORY_PERCENT_OFF') form.value.scope.scope_type = 'CATEGORY_IDS'
    if (type === 'FREE_ITEM') {
      if (!form.value.params.free_item) form.value.params.free_item = { mode: 'CHEAPEST_IN_SCOPE' }
      if (!form.value.conditions.requires_purchase) form.value.conditions.requires_purchase = { type: 'NONE' }
    }
  }
)

function openCreate() {
  editingId.value = null
  form.value = {
    type: 'CART_PERCENT_OFF',
    name: '',
    priority: 0,
    scope: { scope_type: 'ALL_ITEMS', category_ids: [], product_ids: [], exclude_category_ids: [], exclude_product_ids: [] },
    conditions: {},
    params: {},
    limits: {},
    selection_rule: 'CHEAPEST_UNITS',
    site_ids: null,
    folder: '',
  }
  categoryOptions.value = []
  productOptions.value = []
  productFilterQuery.value = ''
  dialogVisible.value = true
}

function openEdit(row: Record<string, unknown>) {
  editingId.value = row.id as string
  const scope = (row.scope as Record<string, unknown>) || {}
  form.value = {
    type: (row.type as string) || 'CART_PERCENT_OFF',
    name: (row.name as string) || '',
    priority: (row.priority as number) || 0,
    scope: {
      scope_type: (scope.scope_type as string) || 'ALL_ITEMS',
      category_ids: [...(scope.category_ids as string[]) || []],
      product_ids: [...(scope.product_ids as string[]) || []],
      exclude_category_ids: [...(scope.exclude_category_ids as string[]) || []],
      exclude_product_ids: [...(scope.exclude_product_ids as string[]) || []],
    },
    conditions: (row.conditions && typeof row.conditions === 'object') ? { ...(row.conditions as Record<string, unknown>) } as DiscountConditions : {},
    params: (row.params && typeof row.params === 'object') ? { ...(row.params as Record<string, unknown>) } as DiscountParams : {},
    limits: (row.limits && typeof row.limits === 'object') ? { ...(row.limits as Record<string, unknown>) } as DiscountLimits : {},
    selection_rule: (row.selection_rule as string) || 'CHEAPEST_UNITS',
    site_ids: (row.site_ids as number[] | null) ?? null,
    folder: (row.folder as string) ?? '',
  }
  if (form.value.type === 'CATEGORY_PERCENT_OFF') form.value.scope.scope_type = 'CATEGORY_IDS'
  ensureFreeItemAndRequiresPurchase()
  categoryOptions.value = []
  productOptions.value = []
  productFilterQuery.value = ''
  dialogVisible.value = true
  if (form.value.scope.scope_type === 'CATEGORY_IDS') loadCategoryOptions()
  if (form.value.scope.scope_type === 'PRODUCT_IDS' || form.value.type === 'FREE_ITEM') loadProductOptions()
}

function getErrorMessage(e: unknown): string {
  const msg = e instanceof Error ? e.message : String(e)
  try {
    const d = JSON.parse(msg)
    if (d && typeof d.message === 'string') {
      const extra = d.errors ? (Array.isArray(d.errors) ? d.errors.join(', ') : JSON.stringify(d.errors)) : ''
      return extra ? `${d.message} ${extra}` : d.message
    }
  } catch (_) {}
  return msg
}

async function save() {
  error.value = ''
  const nameTrim = (form.value.name || '').trim()
  if (!nameTrim) {
    const message = 'El nombre del descuento es obligatorio.'
    error.value = message
    toast.add({ severity: 'error', summary: 'Error de validación', detail: message, life: 6000 })
    return
  }
  try {
    const scope = (form.value.type === 'CART_PERCENT_OFF' || form.value.type === 'CART_AMOUNT_OFF')
      ? { scope_type: 'ALL_ITEMS' as const, category_ids: [], product_ids: [], exclude_category_ids: [], exclude_product_ids: [] }
      : form.value.scope
    const body = {
      type: form.value.type,
      name: nameTrim,
      priority: form.value.priority,
      scope,
      conditions: form.value.conditions,
      params: form.value.params,
      limits: form.value.limits,
      selection_rule: form.value.selection_rule,
      site_ids: form.value.site_ids,
      folder: form.value.folder || undefined,
    }
    if (editingId.value) {
      await api.discounts.update(editingId.value, body)
    } else {
      await api.discounts.create(body)
    }
    dialogVisible.value = false
    await load()
    toast.add({ severity: 'success', summary: 'Guardado', detail: 'Descuento guardado correctamente.', life: 4000 })
  } catch (e) {
    const message = getErrorMessage(e)
    error.value = message
    toast.add({ severity: 'error', summary: 'Error al guardar', detail: message, life: 8000 })
  }
}

async function remove(id: string) {
  if (!confirm('¿Eliminar este descuento?')) return
  error.value = ''
  try {
    await api.discounts.delete(id)
    await load()
    toast.add({ severity: 'success', summary: 'Eliminado', detail: 'Descuento eliminado.', life: 4000 })
  } catch (e) {
    const message = getErrorMessage(e)
    error.value = message
    toast.add({ severity: 'error', summary: 'Error al eliminar', detail: message, life: 8000 })
  }
}

function ensureFreeItemAndRequiresPurchase() {
  if (form.value.type !== 'FREE_ITEM') return
  if (!form.value.params.free_item) form.value.params.free_item = { mode: 'CHEAPEST_IN_SCOPE' }
  if (!form.value.conditions.requires_purchase) form.value.conditions.requires_purchase = { type: 'NONE' }
}

watch(() => form.value.type, () => ensureFreeItemAndRequiresPurchase())

function onDialogShow() {
  ensureFreeItemAndRequiresPurchase()
  if (form.value.scope.scope_type === 'CATEGORY_IDS') loadCategoryOptions()
  if (form.value.scope.scope_type === 'PRODUCT_IDS' || form.value.type === 'FREE_ITEM') loadProductOptions()
}

onMounted(load)
</script>

<template>
  <div class="view">
    <h1>Descuentos</h1>
    <p class="subtitle">Reglas de descuento aplicables por sede. Categorías y productos se cargan desde el backend (selects con filtro).</p>
    <Message v-if="error" severity="error" @close="error = ''">{{ error }}</Message>
    <div class="toolbar">
      <Button label="Nuevo descuento" icon="pi pi-plus" @click="openCreate" />
      <Dropdown v-model="filterFolder" :options="discountFolders" placeholder="Todas las carpetas" class="filter-folder" :show-clear="true" />
    </div>
    <div v-if="loading" class="loading-msg">Cargando…</div>
    <template v-else>
      <section v-for="g in discountsGroupedByFolder" :key="g.folder || '_'" class="folder-section">
        <h3 class="folder-title">
          <i class="pi pi-folder" />
          {{ g.folder || 'Sin carpeta' }}
          <span class="folder-count">({{ g.items.length }})</span>
        </h3>
        <DataTable :value="g.items" striped-rows data-key="id" responsive-layout="scroll" class="p-datatable-sm">
          <Column field="name" header="Nombre" sortable />
          <Column field="type" header="Tipo" />
          <Column field="priority" header="Prioridad" style="width: 6rem" />
          <Column header="Sedes" style="width: 10rem">
            <template #body="{ data }">
              {{ (!data.site_ids || (data.site_ids as number[]).length === 0) ? 'Todas' : (data.site_ids as number[]).length + ' sedes' }}
            </template>
          </Column>
          <Column header="Acciones" style="width: 10rem">
            <template #body="{ data }">
              <Button icon="pi pi-pencil" text rounded size="small" @click="openEdit(data)" />
              <Button icon="pi pi-trash" text rounded severity="danger" size="small" @click="remove(data.id as string)" />
            </template>
          </Column>
        </DataTable>
      </section>
    </template>

    <Dialog v-model:visible="dialogVisible" :header="editingId ? 'Editar descuento' : 'Nuevo descuento'" modal :style="{ width: '36rem' }" :content-style="{ maxHeight: '85vh', overflow: 'auto' }" @show="onDialogShow" @hide="dialogVisible = false">
      <div class="form-grid">
        <div class="field">
          <span class="label-with-info">
            <label>Nombre <span class="required">*</span></label>
            <i class="pi pi-info-circle info-icon" v-tooltip="'Nombre interno del descuento para identificarlo en listados y reportes. Es obligatorio.'" />
          </span>
          <InputText v-model="form.name" placeholder="Ej: 10% carrito" class="w-full" :class="{ 'p-invalid': !(form.name || '').trim() }" />
          <small v-if="!(form.name || '').trim()" class="p-error">El nombre es obligatorio.</small>
        </div>
        <div class="field">
          <span class="label-with-info">
            <label>Tipo</label>
            <i class="pi pi-info-circle info-icon" v-tooltip="'Tipo de regla de descuento. Cada tipo tiene su propia lógica (carrito, producto gratis, MxN, etc.).'" />
          </span>
          <Dropdown v-model="form.type" :options="typeOptions" option-label="label" option-value="value" class="w-full" />
        </div>
        <p v-if="typeDescription" class="type-description full">{{ typeDescription }}</p>
        <div class="field">
          <span class="label-with-info">
            <label>Prioridad</label>
            <i class="pi pi-info-circle info-icon" v-tooltip="'Cuando hay varios descuentos aplicables, se usa este número para ordenar. Mayor prioridad = se evalúa antes.'" />
          </span>
          <InputNumber v-model="form.priority" :min="0" class="w-full" />
        </div>
        <div class="field full">
          <span class="label-with-info">
            <label>Carpeta (para agrupar)</label>
            <i class="pi pi-info-circle info-icon" v-tooltip="'Carpeta para organizar descuentos en la lista (ej: Promos Febrero, Black Friday). Opcional.'" />
          </span>
          <Dropdown v-model="form.folder" :options="folderOptions" option-label="label" option-value="name" placeholder="Sin carpeta" :show-clear="true" class="w-full" />
        </div>
        <div class="field full">
          <span class="label-with-info">
            <label>Sedes (vacío = todas)</label>
            <i class="pi pi-info-circle info-icon" v-tooltip="'Sedes donde aplica este descuento. Si no selecciona ninguna, aplica en todas las sedes.'" />
          </span>
          <MultiSelect v-model="form.site_ids" :options="sites" option-label="site_name" option-value="site_id" placeholder="Todas" filter class="w-full" />
        </div>
        <!-- Scope: no se muestra para descuento en todo el carrito (CART_*); solo para FREE_ITEM, BUY_M_*, BUY_X_*, CATEGORY_* -->
        <template v-if="['FREE_ITEM','BUY_M_PAY_N','BUY_X_GET_Y_PERCENT_OFF'].includes(form.type) || (form.type === 'CATEGORY_PERCENT_OFF')">
          <div class="field full">
            <span class="label-with-info">
              <label>Scope: a qué aplica</label>
              <i class="pi pi-info-circle info-icon" v-tooltip="'Define a qué productos o categorías aplica esta regla: todos los ítems, solo ciertas categorías o solo ciertos productos.'" />
            </span>
            <Dropdown v-if="form.type !== 'CATEGORY_PERCENT_OFF'" v-model="form.scope.scope_type" :options="scopeTypeOptions" option-label="label" option-value="value" class="w-full" />
            <span v-else class="scope-fixed">Solo categorías (fijo para este tipo)</span>
          </div>
          <div v-if="form.scope.scope_type === 'CATEGORY_IDS'" class="field full">
            <label>{{ form.type === 'BUY_M_PAY_N' ? 'Categorías participantes (cada producto de estas categorías aplica M×N por separado)' : (form.type === 'BUY_X_GET_Y_PERCENT_OFF' ? 'Categorías (compra estos)' : 'Categorías') }}</label>
            <MultiSelect v-model="form.scope.category_ids" :options="categoryOptions" option-label="name" option-value="id" placeholder="Seleccione categorías" filter :loading="categoryOptionsLoading" class="w-full" />
          </div>
          <div v-if="form.scope.scope_type === 'PRODUCT_IDS'" class="field full">
            <label>{{ form.type === 'BUY_M_PAY_N' ? 'Productos participantes (cada producto aplica M×N por separado: M unidades del mismo producto = paga N)' : (form.type === 'BUY_X_GET_Y_PERCENT_OFF' ? 'Productos (compra estos)' : 'Productos') }}</label>
            <MultiSelect v-model="form.scope.product_ids" :options="productOptions" option-label="name" option-value="id" placeholder="Buscar o seleccionar productos" filter :loading="productOptionsLoading" class="w-full" @filter="onProductFilter" />
          </div>
          <p v-if="scopeExampleText" class="scope-example">{{ scopeExampleText }}</p>
        </template>

        <!-- CART_PERCENT_OFF -->
        <template v-if="form.type === 'CART_PERCENT_OFF'">
          <div class="field full section-hint" v-tooltip="'Descuento en porcentaje sobre todo el carrito. Opcional: tope máximo en COP y compra mínima para activar.'">
            <span class="section-label"><i class="pi pi-percentage" /> Parámetros: % carrito</span>
          </div>
          <div class="field">
            <label>% descuento</label>
            <InputNumber v-model="form.params.pct" :min="0" :max="100" class="w-full" />
          </div>
          <div class="field">
            <label>Máx. descuento (COP)</label>
            <InputNumber v-model="form.limits.max_discount_amount" :min="0" placeholder="Opcional" class="w-full" />
          </div>
          <div class="field full">
            <label>Requisito: compra mínima (COP)</label>
            <InputNumber v-model="form.conditions.min_subtotal" :min="0" placeholder="Opcional" class="w-full" />
          </div>
        </template>

        <!-- CART_AMOUNT_OFF -->
        <template v-if="form.type === 'CART_AMOUNT_OFF'">
          <div class="field full section-hint" v-tooltip="'Descuento de valor fijo en COP sobre todo el carrito. Opcional: compra mínima para activar.'">
            <span class="section-label"><i class="pi pi-wallet" /> Parámetros: valor fijo carrito</span>
          </div>
          <div class="field">
            <label>Valor descuento (COP)</label>
            <InputNumber v-model="form.params.amount" :min="0" class="w-full" />
          </div>
          <div class="field full">
            <label>Requisito: compra mínima (COP)</label>
            <InputNumber v-model="form.conditions.min_subtotal" :min="0" placeholder="Opcional" class="w-full" />
          </div>
        </template>

        <!-- FREE_ITEM: producto gratis, requisito de compra -->
        <template v-if="form.type === 'FREE_ITEM'">
          <div class="field full section-hint" v-tooltip="'Regala uno o más productos. Elige el más barato del scope o un producto específico. Opcional: exigir compra mínima (subtotal o cantidad).'">
            <span class="section-label"><i class="pi pi-gift" /> Parámetros: producto gratis</span>
          </div>
          <div class="field full">
            <label>Qué es gratis</label>
            <Dropdown v-model="form.params.free_item!.mode" :options="freeItemModeOptions" option-label="label" option-value="value" class="w-full" />
          </div>
          <div v-if="form.params.free_item?.mode === 'SPECIFIC_PRODUCT'" class="field full">
            <label>Producto gratis</label>
            <Dropdown v-model="form.params.free_item!.product_id" :options="productOptions" option-label="name" option-value="id" placeholder="Seleccione producto" filter :loading="productOptionsLoading" class="w-full" @filter="onProductFilter" />
          </div>
          <div class="field full">
            <label>Requisito de compra</label>
            <Dropdown v-model="form.conditions.requires_purchase!.type" :options="requiresPurchaseTypeOptions" option-label="label" option-value="value" placeholder="Ninguno" class="w-full" />
          </div>
          <div v-if="form.conditions.requires_purchase?.type === 'MIN_SUBTOTAL_IN_SCOPE'" class="field full">
            <label>Subtotal mínimo (COP)</label>
            <InputNumber v-model="form.conditions.requires_purchase!.min_subtotal" :min="0" class="w-full" />
          </div>
          <div v-if="form.conditions.requires_purchase?.type === 'MIN_QTY_IN_SCOPE'" class="field full">
            <span class="label-with-info">
              <label>Cantidad mínima</label>
              <i class="pi pi-info-circle info-icon" v-tooltip="'Cantidad mínima de unidades (del scope) que el cliente debe comprar para obtener el producto gratis.'" />
            </span>
            <InputNumber v-model="form.conditions.requires_purchase!.min_qty" :min="1" class="w-full" />
          </div>
          <div v-if="form.conditions.requires_purchase?.type === 'BUY_X_IN_SCOPE'" class="field full">
            <span class="label-with-info">
              <label>Compra X unidades (del scope)</label>
              <i class="pi pi-info-circle info-icon" v-tooltip="'Número de unidades (de los productos/categorías del scope) que el cliente debe comprar para obtener el producto gratis. Ej: 2 = debe llevar al menos 2 unidades para recibir 1 gratis.'" />
            </span>
            <InputNumber v-model="form.conditions.requires_purchase!.buy_x" :min="1" class="w-full" placeholder="Ej: 2" />
          </div>
          <div class="field">
            <span class="label-with-info">
              <label>Cantidad gratis máx.</label>
              <i class="pi pi-info-circle info-icon" v-tooltip="'Máximo de unidades gratis que el cliente puede llevarse en una sola compra. Ej: 1 = un producto gratis; 2 = hasta dos unidades gratis (ej. 2x1).'" />
            </span>
            <InputNumber v-model="form.limits.max_free_qty" :min="1" class="w-full" />
          </div>
        </template>

        <!-- BUY_M_PAY_N: lleva M paga N, mismo producto -->
        <template v-if="form.type === 'BUY_M_PAY_N'">
          <div class="field full scope-notice">
            <i class="pi pi-info-circle" /> En categorías, productos o todo: <strong>compra M lleva N del mismo producto</strong>. No se mezclan productos.
          </div>
          <div class="field full section-hint" v-tooltip="'Scope arriba define dónde aplica (categorías, productos o todos). Lleva M, paga N, por el mismo producto.'">
            <span class="section-label"><i class="pi pi-shopping-cart" /> Parámetros: lleva M paga N</span>
          </div>
          <div class="field">
            <label>Lleva (M)</label>
            <InputNumber v-model="form.params.m" :min="1" class="w-full" />
          </div>
          <div class="field">
            <label>Paga (N)</label>
            <InputNumber v-model="form.params.n" :min="0" class="w-full" />
          </div>
          <div class="field">
            <span class="label-with-info">
              <label>Máx. grupos</label>
              <i class="pi pi-info-circle info-icon" v-tooltip="'Límite de grupos que pueden recibir el descuento. Ej: lleva 3 paga 2 con máx. 2 grupos = aunque compre 9 unidades, solo 2 grupos (6 unidades) tienen descuento; las otras 3 se pagan completas. Vacío = sin límite.'" />
            </span>
            <InputNumber v-model="form.limits.max_groups" :min="1" placeholder="Opcional" class="w-full" />
          </div>
          <div class="field full">
            <label>Requisito: compra mínima (COP)</label>
            <InputNumber v-model="form.conditions.min_subtotal" :min="0" placeholder="Opcional" class="w-full" />
          </div>
        </template>

        <!-- CATEGORY_PERCENT_OFF -->
        <template v-if="form.type === 'CATEGORY_PERCENT_OFF'">
          <div class="field full section-hint" v-tooltip="'Descuento en % solo sobre productos de las categorías elegidas. Opcional: tope en COP, cantidad o subtotal mínimo en categoría.'">
            <span class="section-label"><i class="pi pi-tag" /> Parámetros: % categoría</span>
          </div>
          <div class="field">
            <label>% descuento</label>
            <InputNumber v-model="form.params.pct" :min="0" :max="100" class="w-full" />
          </div>
          <div class="field">
            <label>Máx. descuento (COP)</label>
            <InputNumber v-model="form.limits.max_discount_amount" :min="0" placeholder="Opcional" class="w-full" />
          </div>
          <div class="field">
            <label>Mín. cantidad en categoría</label>
            <InputNumber v-model="form.conditions.min_qty_in_category" :min="0" placeholder="Opcional" class="w-full" />
          </div>
          <div class="field">
            <label>Mín. subtotal en categoría (COP)</label>
            <InputNumber v-model="form.conditions.min_subtotal_in_category" :min="0" placeholder="Opcional" class="w-full" />
          </div>
        </template>

        <!-- BUY_X_GET_Y_PERCENT_OFF: compra X obtén Y con %, mismo producto -->
        <template v-if="form.type === 'BUY_X_GET_Y_PERCENT_OFF'">
          <div class="field full scope-notice">
            <i class="pi pi-info-circle" /> En categorías, productos o todo: <strong>compra X lleva Y del mismo producto</strong> con % de descuento. No se mezclan productos.
          </div>
          <div class="field full section-hint" v-tooltip="'Scope arriba define dónde aplica. Compra X, lleva Y con % de descuento, por el mismo producto.'">
            <span class="section-label"><i class="pi pi-bolt" /> Parámetros: compra X obtén Y %</span>
          </div>
          <div class="field">
            <label>Compra (X)</label>
            <InputNumber v-model="form.params.x" :min="1" class="w-full" />
          </div>
          <div class="field">
            <label>Obtén (Y)</label>
            <InputNumber v-model="form.params.y" :min="1" class="w-full" />
          </div>
          <div class="field">
            <label>% descuento en Y</label>
            <InputNumber v-model="form.params.y_discount_pct" :min="0" :max="100" class="w-full" />
          </div>
          <div class="field">
            <span class="label-with-info">
              <label>Máx. grupos</label>
              <i class="pi pi-info-circle info-icon" v-tooltip="'Límite de veces que aplica la promoción (cada grupo = compra X, obtén Y con %). Ej: compra 2 lleva 1 al 50% con máx. 2 grupos = aunque compre 6 unidades, solo 2 grupos tienen el descuento. Vacío = sin límite.'" />
            </span>
            <InputNumber v-model="form.limits.max_groups" :min="1" placeholder="Opcional" class="w-full" />
          </div>
          <div class="field full">
            <label>Requisito: compra mínima (COP)</label>
            <InputNumber v-model="form.conditions.min_subtotal" :min="0" placeholder="Opcional" class="w-full" />
          </div>
        </template>
      </div>
      <template #footer>
        <Button label="Cancelar" text @click="dialogVisible = false" />
        <Button label="Guardar" icon="pi pi-check" :disabled="!(form.name || '').trim()" @click="save" />
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.view { display: flex; flex-direction: column; gap: 1rem; }
.subtitle { color: #666; margin: 0; }
.toolbar { display: flex; gap: 0.5rem; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.field { display: flex; flex-direction: column; gap: 0.25rem; }
.field.full { grid-column: 1 / -1; }
.field label { font-weight: 500; }
.required { color: #ff6200; }
.w-full { width: 100%; }
.scope-fixed { color: #666; font-size: 0.9rem; }
.filter-folder { min-width: 12rem; }
.loading-msg { padding: 1rem; color: #666; }
.folder-section { margin-bottom: 1.5rem; }
.folder-title { display: flex; align-items: center; gap: 0.5rem; margin: 0 0 0.5rem 0; font-size: 1rem; color: #495057; }
.folder-title .folder-count { color: #868e96; font-weight: normal; }

.label-with-info { display: inline-flex; align-items: center; gap: 0.35rem; }
.info-icon { color: #6c757d; font-size: 0.85rem; cursor: help; }
.type-description { grid-column: 1 / -1; margin: 0; padding: 0.6rem 0.75rem; background: #e7f3ff; border-left: 4px solid #0d6efd; border-radius: 6px; font-size: 0.9rem; color: #0a58ca; line-height: 1.4; }
.section-hint { margin-bottom: 0; padding: 0.4rem 0; }
.section-label { display: inline-flex; align-items: center; gap: 0.4rem; font-weight: 600; font-size: 0.9rem; color: #495057; }
.scope-example { grid-column: 1 / -1; margin: 0; padding: 0.5rem 0.75rem; background: #e8f5e9; border-left: 4px solid #2e7d32; border-radius: 6px; font-size: 0.9rem; color: #1b5e20; line-height: 1.4; }
.scope-notice { grid-column: 1 / -1; margin: 0 0 0.5rem 0; padding: 0.5rem 0.75rem; background: #fff3e0; border-left: 4px solid #e65100; border-radius: 6px; font-size: 0.9rem; color: #bf360c; line-height: 1.4; display: flex; align-items: flex-start; gap: 0.5rem; }
.scope-notice i { flex-shrink: 0; margin-top: 0.1rem; }
</style>

<style>
/* Modo oscuro: cajas de información en formulario de descuentos */
html.theme-dark .type-description {
  background: #1e2a3a !important;
  border-left-color: #3b82f6 !important;
  color: #93c5fd !important;
}
html.theme-dark .scope-example {
  background: #1a2e1a !important;
  border-left-color: #22c55e !important;
  color: #86efac !important;
}
html.theme-dark .scope-notice {
  background: #2e251a !important;
  border-left-color: #f59e0b !important;
  color: #fcd34d !important;
}
html.theme-dark .section-label {
  color: #d0d0d0 !important;
}
</style>
