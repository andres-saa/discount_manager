<script setup lang="ts">
import { ref, onMounted } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Message from 'primevue/message'
import { api } from '../api'

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
  sort_order: null as number | null,
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    folders.value = await api.folders.list()
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  form.value = { name: '', description: null, sort_order: null }
  dialogVisible.value = true
}

function openEdit(row: Record<string, unknown>) {
  editingId.value = row.id as string
  form.value = {
    name: (row.name as string) || '',
    description: (row.description as string) || null,
    sort_order: (row.sort_order as number) ?? null,
  }
  dialogVisible.value = true
}

async function save() {
  error.value = ''
  saving.value = true
  try {
    const body = {
      name: form.value.name.trim(),
      description: form.value.description?.trim() || undefined,
      sort_order: form.value.sort_order ?? undefined,
    }
    if (editingId.value) {
      await api.folders.update(editingId.value, body)
    } else {
      await api.folders.create(body)
    }
    dialogVisible.value = false
    await load()
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    saving.value = false
  }
}

async function remove(row: Record<string, unknown>) {
  const name = (row.name as string) || 'esta carpeta'
  if (!confirm(`¿Eliminar la carpeta "${name}"?\n\nSi confirma, se quitará esta carpeta de todos los descuentos y cuponeras que la usen (cascade).`)) return
  const id = row.id as string
  removing.value = id
  error.value = ''
  try {
    await api.folders.delete(id, true)
    await load()
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    removing.value = null
  }
}

onMounted(load)
</script>

<template>
  <div class="view">
    <h1>Carpetas</h1>
    <p class="subtitle">Organice descuentos y cuponeras en carpetas. Al eliminar una carpeta, se quita de todos los elementos que la usen (cascade).</p>
    <Message v-if="error" severity="error" @close="error = ''">{{ error }}</Message>
    <div class="toolbar">
      <Button label="Nueva carpeta" icon="pi pi-plus" @click="openCreate" />
    </div>
    <DataTable :value="folders" :loading="loading" striped-rows data-key="id" responsive-layout="scroll" class="p-datatable-sm">
      <Column field="name" header="Nombre" sortable />
      <Column field="description" header="Descripción" />
      <Column field="sort_order" header="Orden" style="width: 6rem">
        <template #body="{ data }">
          {{ data.sort_order != null ? data.sort_order : '—' }}
        </template>
      </Column>
      <Column header="Acciones" style="width: 10rem">
        <template #body="{ data }">
          <Button icon="pi pi-pencil" text rounded size="small" :disabled="!!removing" @click="openEdit(data)" />
          <Button icon="pi pi-trash" text rounded severity="danger" size="small" :loading="removing === data.id" :disabled="!!removing" @click="remove(data)" />
        </template>
      </Column>
    </DataTable>

    <Dialog v-model:visible="dialogVisible" :header="editingId ? 'Editar carpeta' : 'Nueva carpeta'" modal :style="{ width: '28rem' }" @hide="dialogVisible = false">
      <div class="form-grid">
        <div class="field full">
          <label>Nombre</label>
          <InputText v-model="form.name" placeholder="Ej: Promos Febrero" class="w-full" />
        </div>
        <div class="field full">
          <label>Descripción (opcional)</label>
          <InputText v-model="form.description" placeholder="Descripción" class="w-full" />
        </div>
        <div class="field">
          <label>Orden (opcional)</label>
          <InputNumber v-model="form.sort_order" :min="0" placeholder="—" class="w-full" :show-buttons="false" />
        </div>
      </div>
      <template #footer>
        <Button label="Cancelar" text :disabled="saving" @click="dialogVisible = false" />
        <Button label="Guardar" icon="pi pi-check" :loading="saving" @click="save" />
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
.w-full { width: 100%; }
</style>
