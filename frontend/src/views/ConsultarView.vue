<script setup lang="ts">
import { ref } from 'vue'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Card from 'primevue/card'
import { api } from '../api'

const code = ref('')
const loading = ref(false)
const result = ref<{
  success: boolean
  message: string
  cuponera_name?: string
  discounts: Array<{ discount_id: string; discount: Record<string, unknown> }>
  uses_remaining_today?: number
} | null>(null)
const error = ref('')

async function consultar(recordUse = false) {
  const c = code.value.trim()
  if (!c) {
    error.value = 'Ingrese el código'
    return
  }
  loading.value = true
  error.value = ''
  result.value = null
  try {
    const res = await api.redeem(c, undefined, recordUse)
    result.value = res
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="view">
    <h1>Consultar cupón</h1>
    <p class="subtitle">Con el código del usuario y la fecha de hoy se obtienen los descuentos del día. Opcionalmente puede registrar un uso (consumir una de las veces permitidas por día).</p>
    <Message v-if="error" severity="error" @close="error = ''">{{ error }}</Message>
    <div class="consultar-form">
      <InputText v-model="code" placeholder="Código del usuario" class="code-input" @keyup.enter="consultar(false)" />
      <Button label="Consultar" icon="pi pi-search" :loading="loading" @click="consultar(false)" />
      <Button label="Consultar y registrar uso" icon="pi pi-check" severity="secondary" :loading="loading" @click="consultar(true)" />
    </div>
    <Card v-if="result" class="result-card">
      <template #title>
        {{ result.success ? (result.cuponera_name || 'Descuentos') : 'Resultado' }}
      </template>
      <template #content>
        <p>{{ result.message }}</p>
        <p v-if="result.uses_remaining_today != null" class="uses-remaining">
          Usos restantes hoy: <strong>{{ result.uses_remaining_today }}</strong>
        </p>
        <div v-if="result.discounts?.length" class="discount-list">
          <h4>Descuentos del día</h4>
          <ul>
            <li v-for="item in result.discounts" :key="item.discount_id" class="discount-item">
              <strong>{{ (item.discount as Record<string, unknown>).name }}</strong>
              <span class="disc-type">({{ (item.discount as Record<string, unknown>).type }})</span>
            </li>
          </ul>
        </div>
      </template>
    </Card>
  </div>
</template>

<style scoped>
.view { display: flex; flex-direction: column; gap: 1rem; max-width: 32rem; }
.subtitle { color: #666; margin: 0; }
.consultar-form { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.code-input { width: 14rem; font-family: monospace; letter-spacing: 0.05em; }
.result-card { margin-top: 1rem; }
.uses-remaining { margin-top: 0.5rem; }
.discount-list { margin-top: 1rem; }
.discount-list h4 { margin: 0 0 0.5rem 0; }
.discount-list ul { margin: 0; padding-left: 1.25rem; }
.discount-item { margin-bottom: 0.25rem; }
.disc-type { color: #666; font-size: 0.9rem; margin-left: 0.25rem; }
</style>
