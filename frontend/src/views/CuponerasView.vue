<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Dropdown from 'primevue/dropdown'
import MultiSelect from 'primevue/multiselect'
import DatePicker from 'primevue/datepicker'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'
import { api } from '../api'

const router = useRouter()
const cuponeras = ref<Array<Record<string, unknown>>>([])
const discounts = ref<Array<Record<string, unknown>>>([])
const sites = ref<Array<Record<string, unknown>>>([])
const folders = ref<Array<Record<string, unknown>>>([])
const loading = ref(true)
const saving = ref(false)
const removing = ref<string | null>(null)
const dialogVisible = ref(false)
const editingId = ref<string | null>(null)
const error = ref('')
const form = ref({
  name: '',
  description: '' as string | null,
  uses_per_day: 1,
  calendar: {} as Record<string, string[]>,
  site_ids: null as number[] | null,
  active: true,
  folder: '' as string,
  start_date: null as string | null,
  end_date: null as string | null,
})

// Calendario grande: mes/año visible
const calendarMonth = ref(new Date().getMonth())
const calendarYear = ref(new Date().getFullYear())
const WEEKDAYS = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
const MONTH_NAMES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

// Panel del día seleccionado
const dayPanelVisible = ref(false)
const selectedDateKey = ref<string | null>(null)
const selectedDayDiscountIds = ref<string[]>([])

const currentMonthLabel = computed(() => `${MONTH_NAMES[calendarMonth.value]} ${calendarYear.value}`)

// DatePicker usa Date; form guarda YYYY-MM-DD
function toDate(s: string | null): Date | null {
  if (!s || s.length < 10) return null
  const d = new Date(s + 'T12:00:00')
  return isNaN(d.getTime()) ? null : d
}
function toDateStr(d: Date | null): string | null {
  if (!d) return null
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}
const startDateModel = computed({
  get: () => toDate(form.value.start_date),
  set: (v: Date | null) => { form.value.start_date = toDateStr(v) },
})
const endDateModel = computed({
  get: () => toDate(form.value.end_date),
  set: (v: Date | null) => { form.value.end_date = toDateStr(v) },
})

const folderOptions = computed(() => {
  const list = (folders.value || []).map((f) => ({ name: (f.name as string) || '', label: (f.name as string) || '' }))
  return [{ name: '', label: 'Sin carpeta' }, ...list]
})
const filterFolder = ref<string | null>(null)
const cuponeraFolders = computed(() => {
  const set = new Set<string>()
  for (const c of cuponeras.value) {
    const f = (c.folder as string) ?? ''
    set.add(f)
  }
  return Array.from(set).sort((a, b) => (a === '' ? -1 : b === '' ? 1 : a.localeCompare(b)))
})
const cuponerasGroupedByFolder = computed(() => {
  const groups: Record<string, Array<Record<string, unknown>>> = {}
  for (const c of cuponeras.value) {
    const f = (c.folder as string) ?? ''
    if (filterFolder.value !== null && f !== filterFolder.value) continue
    if (!groups[f]) groups[f] = []
    groups[f].push(c)
  }
  return cuponeraFolders.value
    .filter((f) => filterFolder.value === null || f === filterFolder.value)
    .map((f) => ({ folder: f, items: groups[f] || [] }))
})

const vigenciaStart = computed(() => (form.value.start_date || '').trim() || null)
const vigenciaEnd = computed(() => (form.value.end_date || '').trim() || null)

function isDateInVigencia(dateKey: string): boolean {
  const start = vigenciaStart.value
  const end = vigenciaEnd.value
  if (!start && !end) return true
  if (start && dateKey < start) return false
  if (end && dateKey > end) return false
  return true
}

const calendarDays = computed(() => {
  const year = calendarYear.value
  const month = calendarMonth.value
  const first = new Date(year, month, 1)
  const last = new Date(year, month + 1, 0)
  const startDow = first.getDay()
  const daysInMonth = last.getDate()
  const rows: Array<Array<{ dateKey: string; day: number; isCurrentMonth: boolean; isToday: boolean; isInVigencia: boolean }>> = []
  let row: Array<{ dateKey: string; day: number; isCurrentMonth: boolean; isToday: boolean; isInVigencia: boolean }> = []
  const today = new Date()
  const todayKey = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`

  const pad = (n: number) => String(n).padStart(2, '0')
  const toKey = (y: number, m: number, d: number) => `${y}-${pad(m)}-${pad(d)}`

  // Días vacíos al inicio
  for (let i = 0; i < startDow; i++) {
    const prev = new Date(year, month, -startDow + i + 1)
    const dateKey = toKey(prev.getFullYear(), prev.getMonth() + 1, prev.getDate())
    row.push({
      dateKey,
      day: prev.getDate(),
      isCurrentMonth: false,
      isToday: false,
      isInVigencia: isDateInVigencia(dateKey),
    })
  }
  // Días del mes
  for (let d = 1; d <= daysInMonth; d++) {
    const dateKey = toKey(year, month + 1, d)
    row.push({
      dateKey,
      day: d,
      isCurrentMonth: true,
      isToday: dateKey === todayKey,
      isInVigencia: isDateInVigencia(dateKey),
    })
    if (row.length === 7) {
      rows.push(row)
      row = []
    }
  }
  // Rellenar última fila
  if (row.length > 0) {
    let nextD = 1
    while (row.length < 7) {
      const next = new Date(year, month + 1, nextD)
      const dateKey = toKey(next.getFullYear(), next.getMonth() + 1, next.getDate())
      row.push({
        dateKey,
        day: next.getDate(),
        isCurrentMonth: false,
        isToday: false,
        isInVigencia: isDateInVigencia(dateKey),
      })
      nextD++
    }
    rows.push(row)
  }
  return rows
})

function getDiscountNamesForDate(dateKey: string): string[] {
  const ids = form.value.calendar[dateKey] || []
  return ids.map((id) => (discounts.value.find((d) => d.id === id) as { name?: string } | undefined)?.name || id)
}

function hasDiscounts(dateKey: string): boolean {
  const ids = form.value.calendar[dateKey] || []
  return ids.length > 0
}

function openDayPanel(dateKey: string) {
  if (!isDateInVigencia(dateKey)) return
  selectedDateKey.value = dateKey
  selectedDayDiscountIds.value = [...(form.value.calendar[dateKey] || [])]
  dayPanelVisible.value = true
}

function saveDayDiscounts() {
  if (!selectedDateKey.value) return
  if (selectedDayDiscountIds.value.length) {
    form.value.calendar[selectedDateKey.value] = [...selectedDayDiscountIds.value]
  } else {
    delete form.value.calendar[selectedDateKey.value]
  }
  dayPanelVisible.value = false
  selectedDateKey.value = null
}

function clearDayDiscounts() {
  if (!selectedDateKey.value) return
  delete form.value.calendar[selectedDateKey.value]
  selectedDayDiscountIds.value = []
  dayPanelVisible.value = false
  selectedDateKey.value = null
}

function prevMonth() {
  if (calendarMonth.value === 0) {
    calendarMonth.value = 11
    calendarYear.value--
  } else {
    calendarMonth.value--
  }
}

function nextMonth() {
  if (calendarMonth.value === 11) {
    calendarMonth.value = 0
    calendarYear.value++
  } else {
    calendarMonth.value++
  }
}

function goToToday() {
  const t = new Date()
  calendarMonth.value = t.getMonth()
  calendarYear.value = t.getFullYear()
}

function selectedDateLabel(): string {
  if (!selectedDateKey.value) return ''
  const parts = selectedDateKey.value.split('-').map(Number)
  const y = parts[0] ?? 0
  const m = (parts[1] ?? 1) - 1
  const d = parts[2] ?? 1
  const date = new Date(y, m, d)
  return date.toLocaleDateString('es-CO', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [c, d, s, f] = await Promise.all([api.cuponeras.list(), api.discounts.list(), api.sites.list(), api.folders.list()])
    cuponeras.value = c
    discounts.value = d
    sites.value = s
    folders.value = f
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  form.value = { name: '', description: null, uses_per_day: 1, calendar: {}, site_ids: null, active: true, folder: '', start_date: null, end_date: null }
  calendarMonth.value = new Date().getMonth()
  calendarYear.value = new Date().getFullYear()
  dayPanelVisible.value = false
  dialogVisible.value = true
}

function openEdit(row: Record<string, unknown>) {
  editingId.value = row.id as string
  form.value = {
    name: (row.name as string) || '',
    description: (row.description as string) || null,
    uses_per_day: (row.uses_per_day as number) ?? 1,
    calendar: { ...((row.calendar as Record<string, string[]>) || {}) },
    site_ids: (row.site_ids as number[] | null) ?? null,
    active: (row.active as boolean) ?? true,
    folder: (row.folder as string) ?? '',
    start_date: (row.start_date as string) || null,
    end_date: (row.end_date as string) || null,
  }
  calendarMonth.value = new Date().getMonth()
  calendarYear.value = new Date().getFullYear()
  dayPanelVisible.value = false
  dialogVisible.value = true
}

async function save() {
  error.value = ''
  saving.value = true
  try {
    const body = {
      name: form.value.name,
      description: form.value.description || undefined,
      uses_per_day: form.value.uses_per_day,
      calendar: form.value.calendar,
      site_ids: form.value.site_ids,
      active: form.value.active,
      folder: form.value.folder || undefined,
      start_date: form.value.start_date || undefined,
      end_date: form.value.end_date || undefined,
    }
    if (editingId.value) {
      await api.cuponeras.update(editingId.value, body)
    } else {
      await api.cuponeras.create(body)
    }
    dialogVisible.value = false
    await load()
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    saving.value = false
  }
}

async function remove(id: string) {
  if (!confirm('¿Eliminar esta cuponera?')) return
  removing.value = id
  error.value = ''
  try {
    await api.cuponeras.delete(id)
    await load()
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    removing.value = null
  }
}

function goToUsers(row: Record<string, unknown>) {
  router.push({ name: 'CuponeraUsuarios', params: { id: row.id as string } })
}

onMounted(load)
</script>

<template>
  <div class="view">
    <h1>Cuponeras</h1>
    <p class="subtitle">Cada cuponera tiene un calendario: asigne descuentos por día. Los usuarios con código canjean los descuentos del día (según usos/día).</p>
    <Message v-if="error" severity="error" @close="error = ''">{{ error }}</Message>
    <div class="toolbar">
      <Button label="Nueva cuponera" icon="pi pi-plus" @click="openCreate" />
      <Dropdown v-model="filterFolder" :options="cuponeraFolders" placeholder="Todas las carpetas" class="filter-folder" :show-clear="true" />
    </div>
    <div v-if="loading" class="loading-block">
      <ProgressSpinner style="width: 40px; height: 40px" stroke-width="3" />
      <span>Cargando…</span>
    </div>
    <template v-else>
      <section v-for="g in cuponerasGroupedByFolder" :key="g.folder || '_'" class="folder-section">
        <h3 class="folder-title">
          <i class="pi pi-folder" />
          {{ g.folder || 'Sin carpeta' }}
          <span class="folder-count">({{ g.items.length }})</span>
        </h3>
        <DataTable :value="g.items" striped-rows data-key="id" responsive-layout="scroll" class="p-datatable-sm">
          <Column field="name" header="Nombre" sortable />
          <Column field="uses_per_day" header="Usos/día" style="width: 6rem" />
          <Column header="Vigencia" style="width: 11rem">
            <template #body="{ data }">
              <span v-if="!data.start_date && !data.end_date">—</span>
              <span v-else>{{ (data.start_date || '…') }} – {{ (data.end_date || '…') }}</span>
            </template>
          </Column>
          <Column header="Días con descuento" style="width: 8rem">
            <template #body="{ data }">
              {{ Object.keys(data.calendar || {}).length }} días
            </template>
          </Column>
          <Column field="active" header="Activa" style="width: 6rem">
            <template #body="{ data }">
              {{ data.active ? 'Sí' : 'No' }}
            </template>
          </Column>
          <Column header="Acciones" style="width: 12rem">
            <template #body="{ data }">
              <Button label="Usuarios" icon="pi pi-users" text rounded size="small" :disabled="!!removing" @click="goToUsers(data)" />
              <Button icon="pi pi-pencil" text rounded size="small" :disabled="!!removing" @click="openEdit(data)" />
              <Button icon="pi pi-trash" text rounded severity="danger" size="small" :loading="removing === data.id" :disabled="!!removing" @click="remove(data.id as string)" />
            </template>
          </Column>
        </DataTable>
      </section>
    </template>

    <Dialog
      v-model:visible="dialogVisible"
      :header="editingId ? 'Editar cuponera' : 'Nueva cuponera'"
      modal
      :style="{ width: 'min(96vw, 56rem)' }"
      :content-style="{ maxHeight: '90vh', overflow: 'auto' }"
      class="cuponera-dialog"
      @hide="dialogVisible = false"
    >
      <div class="cuponera-form">
        <section class="form-section">
          <h3>Datos de la cuponera</h3>
          <div class="form-grid">
            <div class="field full">
              <label>Nombre</label>
              <InputText v-model="form.name" placeholder="Ej: Cuponera Febrero" class="w-full" />
            </div>
            <div class="field full">
              <label>Descripción (opcional)</label>
              <InputText v-model="form.description" placeholder="Descripción" class="w-full" />
            </div>
            <div class="field">
              <label>Usos por día por usuario</label>
              <InputNumber v-model="form.uses_per_day" :min="1" class="w-full" />
            </div>
            <div class="field">
              <label>Inicio vigencia</label>
              <DatePicker v-model="startDateModel" date-format="yy-mm-dd" show-icon show-button-bar :show-clear="true" placeholder="Sin límite" class="w-full" input-class="w-full" />
              <small class="field-hint">Si se deja vacío, no hay límite de inicio.</small>
            </div>
            <div class="field">
              <label>Fin vigencia</label>
              <DatePicker v-model="endDateModel" date-format="yy-mm-dd" show-icon show-button-bar :show-clear="true" placeholder="Sin límite" class="w-full" input-class="w-full" />
              <small class="field-hint">Si se deja vacío, no hay límite de fin.</small>
            </div>
            <div class="field full">
              <label>Carpeta (para agrupar)</label>
              <Dropdown v-model="form.folder" :options="folderOptions" option-label="label" option-value="name" placeholder="Sin carpeta" :show-clear="true" class="w-full" />
            </div>
            <div class="field full">
              <label>Sedes (vacío = todas)</label>
              <MultiSelect v-model="form.site_ids" :options="sites" option-label="site_name" option-value="site_id" placeholder="Todas" filter class="w-full" />
            </div>
          </div>
        </section>

        <section class="calendar-section">
          <h3>Calendario: descuentos por día</h3>
          <p class="calendar-hint">Solo puede asignar descuentos a días dentro de la vigencia (inicio y fin). Los días fuera de vigencia aparecen bloqueados.</p>
          <div class="calendar-wrap">
            <div class="calendar-header">
              <Button icon="pi pi-chevron-left" text rounded @click="prevMonth" aria-label="Mes anterior" />
              <span class="calendar-title">{{ currentMonthLabel }}</span>
              <Button icon="pi pi-chevron-right" text rounded @click="nextMonth" aria-label="Mes siguiente" />
              <Button label="Hoy" text rounded size="small" @click="goToToday" class="btn-today" />
            </div>
            <div class="calendar-grid">
              <div v-for="w in WEEKDAYS" :key="w" class="calendar-weekday">{{ w }}</div>
              <template v-for="(row, ri) in calendarDays" :key="ri">
                <button
                  v-for="cell in row"
                  :key="cell.dateKey"
                  type="button"
                  class="calendar-day"
                  :class="{
                    'other-month': !cell.isCurrentMonth,
                    'today': cell.isToday,
                    'has-discounts': hasDiscounts(cell.dateKey),
                    'outside-vigencia': !cell.isInVigencia,
                  }"
                  :disabled="!cell.isInVigencia"
                  :title="cell.isInVigencia ? 'Asignar descuentos' : 'Fuera de vigencia'"
                  @click="openDayPanel(cell.dateKey)"
                >
                  <span class="day-num">{{ cell.day }}</span>
                  <span v-if="hasDiscounts(cell.dateKey)" class="day-badge">
                    {{ (form.calendar[cell.dateKey] || []).length }}
                  </span>
                </button>
              </template>
            </div>
          </div>
        </section>
      </div>
      <template #footer>
        <Button label="Cancelar" text :disabled="saving" @click="dialogVisible = false" />
        <Button label="Guardar cuponera" icon="pi pi-check" :loading="saving" @click="save" />
      </template>
    </Dialog>

    <!-- Panel del día: descuentos para la fecha seleccionada -->
    <Dialog
      v-model:visible="dayPanelVisible"
      :header="'Descuentos para ' + selectedDateLabel()"
      modal
      :style="{ width: '22rem' }"
      :dismissable-mask="true"
      @hide="selectedDateKey = null"
    >
      <div class="day-panel">
        <label>Descuentos activos este día</label>
        <MultiSelect
          v-model="selectedDayDiscountIds"
          :options="discounts"
          option-label="name"
          option-value="id"
          placeholder="Seleccione uno o más descuentos"
          filter
          class="w-full"
        />
      </div>
      <template #footer>
        <Button label="Quitar día" severity="secondary" text @click="clearDayDiscounts" />
        <Button label="Guardar" icon="pi pi-check" @click="saveDayDiscounts" />
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.view { display: flex; flex-direction: column; gap: 1rem; }
.subtitle { color: #666; margin: 0; }
.toolbar { display: flex; gap: 0.5rem; }

.cuponera-form { display: flex; flex-direction: column; gap: 1.5rem; }
.form-section h3, .calendar-section h3 { margin: 0 0 0.75rem 0; font-size: 1rem; color: #333; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.field { display: flex; flex-direction: column; gap: 0.25rem; }
.field.full { grid-column: 1 / -1; }
.field label { font-weight: 500; }
.field-hint { display: block; margin-top: 0.2rem; font-size: 0.8rem; color: #6c757d; }
.w-full { width: 100%; }

.calendar-section { margin-top: 0.5rem; }
.calendar-hint { color: #666; font-size: 0.9rem; margin: 0 0 1rem 0; }
.calendar-wrap { background: #f8f9fa; border-radius: 12px; padding: 1rem; border: 1px solid #dee2e6; }
.calendar-header { display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap; }
.calendar-title { font-weight: 600; font-size: 1.1rem; min-width: 10rem; text-align: center; }
.btn-today { margin-left: 0.5rem; }

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
  max-width: 100%;
}
.calendar-weekday {
  padding: 0.5rem;
  text-align: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: #495057;
  text-transform: uppercase;
}
.calendar-day {
  aspect-ratio: 1;
  min-height: 3.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  transition: background 0.15s, box-shadow 0.15s;
  font-size: 0.95rem;
}
.calendar-day:hover {
  background: #e9ecef;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
.calendar-day.other-month {
  background: #f1f3f5;
  color: #868e96;
}
.calendar-day.other-month:hover { background: #e9ecef; }
.calendar-day.today {
  border-color: #ff6200;
  background: #fff8f5;
  font-weight: 600;
}
.calendar-day.today:hover { background: #ffefe8; }
.calendar-day.has-discounts {
  background: #e8f5e9;
  border-color: #51b46d;
}
.calendar-day.has-discounts:hover { background: #c8e6c9; }
.calendar-day.outside-vigencia,
.calendar-day:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #e9ecef !important;
  color: #868e96;
}
.calendar-day.outside-vigencia:hover,
.calendar-day:disabled:hover { background: #e9ecef !important; box-shadow: none; }
.day-num { line-height: 1; }
.day-badge {
  font-size: 0.7rem;
  background: #51b46d;
  color: #fff;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 1.25rem;
}

.day-panel { display: flex; flex-direction: column; gap: 0.75rem; }
.day-panel label { font-weight: 500; }

.filter-folder { min-width: 12rem; }
.loading-block {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 2rem;
  color: #666;
}
.loading-block span { font-size: 0.95rem; }
.folder-section { margin-bottom: 1.5rem; }
.folder-title { display: flex; align-items: center; gap: 0.5rem; margin: 0 0 0.5rem 0; font-size: 1rem; color: #495057; }
.folder-title .folder-count { color: #868e96; font-weight: normal; }

/* Tema oscuro: calendario cuponera */
html.theme-dark .calendar-section h3,
html.theme-dark .form-section h3 { color: #e5e7eb; }
html.theme-dark .calendar-hint { color: #9ca3af; }
html.theme-dark .calendar-wrap {
  background: #1f2937;
  border-color: #374151;
}
html.theme-dark .calendar-title { color: #f3f4f6; }
html.theme-dark .calendar-weekday { color: #9ca3af; }
html.theme-dark .calendar-day {
  background: #111827;
  border-color: #374151;
  color: #e5e7eb;
}
html.theme-dark .calendar-day:hover {
  background: #374151;
  box-shadow: 0 1px 4px rgba(0,0,0,0.3);
}
html.theme-dark .calendar-day.other-month {
  background: #1f2937;
  color: #6b7280;
}
html.theme-dark .calendar-day.other-month:hover { background: #374151; }
html.theme-dark .calendar-day.today {
  border-color: #ff6200;
  background: #3d2914;
  color: #fef3c7;
}
html.theme-dark .calendar-day.today:hover { background: #4a3518; }
html.theme-dark .calendar-day.has-discounts {
  background: #1a3d24;
  border-color: #51b46d;
  color: #a7f3d0;
}
html.theme-dark .calendar-day.has-discounts:hover { background: #22543d; }
html.theme-dark .calendar-day.outside-vigencia,
html.theme-dark .calendar-day:disabled {
  background: #1f2937 !important;
  color: #6b7280;
}
html.theme-dark .calendar-day.outside-vigencia:hover,
html.theme-dark .calendar-day:disabled:hover { background: #1f2937 !important; box-shadow: none; }
html.theme-dark .day-badge { background: #51b46d; color: #fff; }
html.theme-dark .subtitle,
html.theme-dark .loading-block { color: #9ca3af; }
html.theme-dark .field-hint { color: #9ca3af; }
html.theme-dark .folder-title { color: #d1d5db; }
html.theme-dark .folder-title .folder-count { color: #9ca3af; }
</style>
