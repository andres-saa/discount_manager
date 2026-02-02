<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import { api } from '../api'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const cuponeraId = computed(() => route.params.id as string)
const cuponera = ref<Record<string, unknown> | null>(null)
const users = ref<Array<Record<string, unknown>>>([])
const loading = ref(true)
const saving = ref(false)
const removing = ref<string | null>(null)
const dialogVisible = ref(false)
const editingUserId = ref<string | null>(null)
const error = ref('')
const form = ref({
  code: '' as string | null,
  first_name: '',
  last_name: '',
  phone: '',
  phone_code: '+57',
  email: '',
  address: '' as string | null,
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [c, u] = await Promise.all([
      api.cuponeras.get(cuponeraId.value),
      api.cuponeraUsers.list(cuponeraId.value),
    ])
    cuponera.value = c
    users.value = u
  } catch (e) {
    const errorMsg = e instanceof Error ? e.message : String(e)
    error.value = errorMsg
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: errorMsg,
      life: 5000,
    })
  } finally {
    loading.value = false
  }
}

function openRegister() {
  editingUserId.value = null
  form.value = {
    code: null,
    first_name: '',
    last_name: '',
    phone: '',
    phone_code: '+57',
    email: '',
    address: null,
  }
  dialogVisible.value = true
}

function openEdit(user: Record<string, unknown>) {
  editingUserId.value = user.id as string
  form.value = {
    code: (user.code as string) ?? '',
    first_name: (user.first_name as string) ?? (user.name as string)?.toString().split(/\s+/)[0] ?? '',
    last_name: (user.last_name as string) ?? (user.name as string)?.toString().split(/\s+/).slice(1).join(' ') ?? '',
    phone: (user.phone as string) ?? '',
    phone_code: (user.phone_code as string) ?? '+57',
    email: (user.email as string) ?? '',
    address: (user.address as string) ?? '',
  }
  dialogVisible.value = true
}

async function submit() {
  error.value = ''
  const firstName = form.value.first_name?.trim()
  const lastName = form.value.last_name?.trim()
  const email = form.value.email?.trim()
  const phone = form.value.phone?.trim()

  // Validaciones del lado del cliente
  if (!firstName) {
    error.value = 'El nombre es obligatorio.'
    toast.add({
      severity: 'warn',
      summary: 'Validación',
      detail: 'El nombre es obligatorio.',
      life: 4000,
    })
    return
  }
  if (!lastName) {
    error.value = 'El apellido es obligatorio.'
    toast.add({
      severity: 'warn',
      summary: 'Validación',
      detail: 'El apellido es obligatorio.',
      life: 4000,
    })
    return
  }
  if (!email) {
    error.value = 'El email es obligatorio.'
    toast.add({
      severity: 'warn',
      summary: 'Validación',
      detail: 'El email es obligatorio.',
      life: 4000,
    })
    return
  }
  // Validación básica de formato email
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email)) {
    error.value = 'Email inválido. Debe tener formato: ejemplo@dominio.com'
    toast.add({
      severity: 'warn',
      summary: 'Validación',
      detail: 'Email inválido. Debe tener formato: ejemplo@dominio.com',
      life: 4000,
    })
    return
  }
  if (!phone) {
    error.value = 'El teléfono es obligatorio.'
    toast.add({
      severity: 'warn',
      summary: 'Validación',
      detail: 'El teléfono es obligatorio.',
      life: 4000,
    })
    return
  }
  // Validar que el teléfono solo contenga números (y opcionalmente espacios/guiones)
  const phoneOnlyDigits = phone.replace(/[\s\-]/g, '')
  if (!/^\d+$/.test(phoneOnlyDigits)) {
    error.value = 'El teléfono solo debe contener números.'
    toast.add({
      severity: 'warn',
      summary: 'Validación',
      detail: 'El teléfono solo debe contener números (sin letras).',
      life: 4000,
    })
    return
  }

  const phoneCode = (form.value.phone_code?.trim() || '+57').replace(/^(\d+)$/, '+$1')
  const payload = {
    first_name: firstName,
    last_name: lastName,
    phone: phoneOnlyDigits, // Enviar solo dígitos
    phone_code: phoneCode,
    email: email,
    address: form.value.address?.trim() || undefined,
  } as Record<string, unknown>
  if (!editingUserId.value) {
    payload.code = form.value.code?.trim() || undefined
  } else {
    if (form.value.code != null && form.value.code !== '') {
      payload.code = form.value.code.trim()
    }
  }

  saving.value = true
  try {
    if (editingUserId.value) {
      await api.cuponeraUsers.update(cuponeraId.value, editingUserId.value, payload)
      toast.add({
        severity: 'success',
        summary: 'Éxito',
        detail: 'Usuario actualizado correctamente.',
        life: 3000,
      })
    } else {
      await api.cuponeraUsers.create(cuponeraId.value, payload)
      toast.add({
        severity: 'success',
        summary: 'Éxito',
        detail: 'Usuario registrado correctamente.',
        life: 3000,
      })
    }
    dialogVisible.value = false
    editingUserId.value = null
    await load()
  } catch (e) {
    const errorMsg = e instanceof Error ? e.message : String(e)
    error.value = errorMsg
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: errorMsg,
      life: 5000,
    })
  } finally {
    saving.value = false
  }
}

async function remove(userId: string) {
  if (!confirm('¿Eliminar este usuario?')) return
  removing.value = userId
  error.value = ''
  try {
    await api.cuponeraUsers.delete(cuponeraId.value, userId)
    toast.add({
      severity: 'success',
      summary: 'Éxito',
      detail: 'Usuario eliminado correctamente.',
      life: 3000,
    })
    await load()
  } catch (e) {
    const errorMsg = e instanceof Error ? e.message : String(e)
    error.value = errorMsg
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: errorMsg,
      life: 5000,
    })
  } finally {
    removing.value = null
  }
}

function goBack() {
  router.push({ name: 'Cuponeras' })
}

onMounted(load)
</script>

<template>
  <div class="view">
    <div class="header-row">
      <Button icon="pi pi-arrow-left" text rounded @click="goBack" />
      <h1>Usuarios: {{ cuponera?.name ?? '…' }}</h1>
    </div>
    <p class="subtitle">Puede indicar un código a mano o dejarlo vacío para que el sistema lo genere. No se permiten códigos duplicados en cuponeras vigentes; puede reutilizar un código si ya no está en una cuponera vigente (ej. renovar cliente).</p>
    <Message v-if="error" severity="error" @close="error = ''">{{ error }}</Message>
    <div class="toolbar">
      <Button label="Registrar usuario" icon="pi pi-user-plus" @click="openRegister" />
    </div>
    <DataTable :value="users" :loading="loading" striped-rows data-key="id" responsive-layout="scroll" class="p-datatable-sm">
      <Column field="code" header="Código" style="font-family: monospace; font-weight: 600" />
      <Column header="Nombre">
        <template #body="{ data }">
          {{ [data.first_name, data.last_name].filter(Boolean).join(' ') || data.name || '—' }}
        </template>
      </Column>
      <Column header="Teléfono">
        <template #body="{ data }">
          {{ data.phone_code ? `${data.phone_code} ${data.phone}` : data.phone || '—' }}
        </template>
      </Column>
      <Column field="email" header="Correo" />
      <Column field="address" header="Dirección (opcional)" />
      <Column header="Acciones" style="width: 8rem">
        <template #body="{ data }">
          <Button icon="pi pi-pencil" text rounded size="small" title="Editar" :disabled="!!removing" @click="openEdit(data)" />
          <Button icon="pi pi-trash" text rounded severity="danger" size="small" title="Eliminar" :loading="removing === data.id" :disabled="!!removing" @click="remove(data.id as string)" />
        </template>
      </Column>
    </DataTable>

    <Dialog v-model:visible="dialogVisible" :header="editingUserId ? 'Editar usuario' : 'Registrar usuario en cuponera'" modal :style="{ width: '28rem' }" @hide="dialogVisible = false; editingUserId = null">
      <div class="form-grid">
        <div class="field full">
          <label>Código (opcional)</label>
          <InputText v-model="form.code" placeholder="Dejar vacío para generar automáticamente" class="w-full" style="font-family: monospace; letter-spacing: 0.05em" />
          <small class="field-hint">No puede repetirse en otra cuponera vigente. Si el cliente tuvo código antes en una cuponera ya finalizada, puede usar el mismo.</small>
        </div>
        <div class="field half">
          <label>Nombre <span class="required">*</span></label>
          <InputText v-model="form.first_name" placeholder="Nombre" class="w-full" />
        </div>
        <div class="field half">
          <label>Apellido <span class="required">*</span></label>
          <InputText v-model="form.last_name" placeholder="Apellido" class="w-full" />
        </div>
        <div class="field half">
          <label>Código país teléfono</label>
          <InputText v-model="form.phone_code" placeholder="+57" class="w-full" />
          <small class="field-hint">Ej. +57 (Colombia), +1 (EE.UU.). Por defecto +57.</small>
        </div>
        <div class="field half">
          <label>Teléfono <span class="required">*</span></label>
          <InputText v-model="form.phone" placeholder="300 123 4567" class="w-full" />
        </div>
        <div class="field full">
          <label>Correo electrónico <span class="required">*</span></label>
          <InputText v-model="form.email" type="email" placeholder="email@ejemplo.com" class="w-full" />
        </div>
        <div class="field full">
          <label>Dirección (opcional)</label>
          <InputText v-model="form.address" placeholder="Dirección" class="w-full" />
        </div>
      </div>
      <template #footer>
        <Button label="Cancelar" text :disabled="saving" @click="dialogVisible = false; editingUserId = null" />
        <Button :label="editingUserId ? 'Guardar' : 'Registrar'" icon="pi pi-check" :loading="saving" @click="submit" />
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.view { display: flex; flex-direction: column; gap: 1rem; }
.header-row { display: flex; align-items: center; gap: 0.75rem; }
.subtitle { color: #666; margin: 0; }
.toolbar { display: flex; gap: 0.5rem; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-grid .field.full { grid-column: 1 / -1; }
.field { display: flex; flex-direction: column; gap: 0.25rem; }
.field.full { width: 100%; }
.field.half { width: 100%; }
.field label { font-weight: 500; }
.field .required { color: #c00; }
.field-hint { display: block; margin-top: 0.2rem; font-size: 0.8rem; color: #6c757d; }
.w-full { width: 100%; }
</style>
