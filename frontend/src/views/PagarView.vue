<script setup lang="ts">
import { ref } from 'vue'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Card from 'primevue/card'
import { useToast } from 'primevue/usetoast'
import { api } from '../api'

const toast = useToast()

const name = ref('')
const phone = ref('')
const email = ref('')
const address = ref('')

const cuponeraExpanded = ref(false)
const cuponeraCode = ref('')
const loadingRedeem = ref(false)
const redeemError = ref('')
const redeemResult = ref<{
  success: boolean
  message: string
  cuponera_name?: string
  discounts: Array<{ discount_id: string; discount: Record<string, unknown> }>
  uses_remaining_today?: number
  user?: { name: string; phone: string; email: string; address?: string }
} | null>(null)

async function applyCuponeraCode() {
  const code = cuponeraCode.value.trim()
  if (!code) {
    redeemError.value = 'Ingrese el código de la cuponera'
    return
  }
  loadingRedeem.value = true
  redeemError.value = ''
  redeemResult.value = null
  try {
    const res = await api.redeem(code, undefined, false)
    redeemResult.value = res
    if (res.success && res.user) {
      name.value = res.user.name ?? ''
      phone.value = res.user.phone ?? ''
      email.value = res.user.email ?? ''
      address.value = res.user.address ?? ''
      toast.add({
        severity: 'success',
        summary: 'Cuponera válida',
        detail: 'Datos del usuario cargados. Descuentos del día disponibles.',
        life: 4000,
      })
    } else if (!res.success) {
      redeemError.value = res.message
    }
  } catch (e) {
    redeemError.value = e instanceof Error ? e.message : String(e)
  } finally {
    loadingRedeem.value = false
  }
}

function toggleCuponera() {
  cuponeraExpanded.value = !cuponeraExpanded.value
  if (!cuponeraExpanded.value) {
    redeemError.value = ''
    redeemResult.value = null
  }
}
</script>

<template>
  <div class="view">
    <h1>Pagar</h1>
    <p class="subtitle">
      Complete sus datos o use su código de cuponera para cargar la información automáticamente.
    </p>

    <Card class="cuponera-card">
      <template #title>
        <button type="button" class="cuponera-toggle" @click="toggleCuponera">
          <i class="pi pi-ticket" />
          <span>Tienes cuponera activa</span>
          <i :class="cuponeraExpanded ? 'pi pi-chevron-up' : 'pi pi-chevron-down'" />
        </button>
      </template>
      <template #content v-if="cuponeraExpanded">
        <p class="cuponera-hint">
          Ingrese su código de cuponera. Si está vigente, se completarán sus datos y verá los descuentos del día.
        </p>
        <div class="cuponera-form">
          <InputText
            v-model="cuponeraCode"
            placeholder="Código de cuponera"
            class="code-input"
            @keyup.enter="applyCuponeraCode"
          />
          <Button
            label="Validar y cargar datos"
            icon="pi pi-check"
            :loading="loadingRedeem"
            @click="applyCuponeraCode"
          />
        </div>
        <Message v-if="redeemError" severity="error" @close="redeemError = ''">
          {{ redeemError }}
        </Message>
        <div v-if="redeemResult?.success" class="redeem-success">
          <p class="cuponera-name">{{ redeemResult.cuponera_name }}</p>
          <p v-if="redeemResult.uses_remaining_today != null" class="uses-remaining">
            Usos restantes hoy: <strong>{{ redeemResult.uses_remaining_today }}</strong>
          </p>
          <div v-if="redeemResult.discounts?.length" class="discount-list">
            <h4>Descuentos del día</h4>
            <ul>
              <li
                v-for="item in redeemResult.discounts"
                :key="item.discount_id"
                class="discount-item"
              >
                <strong>{{ (item.discount as Record<string, unknown>).name }}</strong>
                <span class="disc-type">({{ (item.discount as Record<string, unknown>).type }})</span>
              </li>
            </ul>
          </div>
        </div>
      </template>
    </Card>

    <Card class="form-card">
      <template #title>Datos del cliente</template>
      <template #content>
        <div class="form-grid">
          <div class="field">
            <label for="name">Nombre</label>
            <InputText id="name" v-model="name" placeholder="Nombre completo" />
          </div>
          <div class="field">
            <label for="phone">Teléfono</label>
            <InputText id="phone" v-model="phone" placeholder="Teléfono" />
          </div>
          <div class="field">
            <label for="email">Correo</label>
            <InputText id="email" v-model="email" placeholder="Correo electrónico" type="email" />
          </div>
          <div class="field full-width">
            <label for="address">Dirección</label>
            <InputText id="address" v-model="address" placeholder="Dirección de entrega" />
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<style scoped>
.view {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-width: 36rem;
}
.subtitle {
  color: #666;
  margin: 0;
}
.cuponera-card {
  margin-top: 0.25rem;
}
.cuponera-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0;
  border: none;
  background: none;
  font-size: 1rem;
  font-weight: 600;
  color: inherit;
  cursor: pointer;
  text-align: left;
}
.cuponera-toggle:hover {
  opacity: 0.9;
}
.cuponera-hint {
  color: #666;
  margin: 0 0 1rem 0;
  font-size: 0.95rem;
}
.cuponera-form {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}
.code-input {
  width: 14rem;
  font-family: monospace;
  letter-spacing: 0.05em;
}
.redeem-success {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--p-surface-border, #dee2e6);
}
.cuponera-name {
  font-weight: 600;
  margin: 0 0 0.5rem 0;
}
.uses-remaining {
  margin: 0.5rem 0 0 0;
}
.discount-list {
  margin-top: 0.75rem;
}
.discount-list h4 {
  margin: 0 0 0.5rem 0;
}
.discount-list ul {
  margin: 0;
  padding-left: 1.25rem;
}
.discount-item {
  margin-bottom: 0.25rem;
}
.disc-type {
  color: #666;
  font-size: 0.9rem;
  margin-left: 0.25rem;
}
.form-card {
  margin-top: 0.25rem;
}
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.field.full-width {
  grid-column: 1 / -1;
}
.field label {
  font-weight: 500;
  font-size: 0.9rem;
}
</style>
