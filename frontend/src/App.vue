<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import type { MenuItem } from 'primevue/menuitem'
import Toast from 'primevue/toast'
import Button from 'primevue/button'

const THEME_KEY = 'app-theme'
type Theme = 'light' | 'dark'

const theme = ref<Theme>((localStorage.getItem(THEME_KEY) as Theme) || 'dark')

function applyTheme(value: Theme) {
  const root = document.documentElement
  if (value === 'dark') {
    root.classList.add('theme-dark')
  } else {
    root.classList.remove('theme-dark')
  }
  localStorage.setItem(THEME_KEY, value)
}

function toggleTheme() {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
}

watch(theme, applyTheme)
onMounted(() => applyTheme(theme.value))

const menuItems: MenuItem[] = [
  { label: 'Carpetas', icon: 'pi pi-folder', to: '/carpetas' },
  { label: 'Descuentos', icon: 'pi pi-percentage', to: '/descuentos' },
  { label: 'Cuponeras', icon: 'pi pi-calendar', to: '/cuponeras' },
  { label: 'Consultar cupón', icon: 'pi pi-ticket', to: '/consultar' },
  // { label: 'Pagar', icon: 'pi pi-credit-card', to: '/pag   ar' },
  { label: 'Documentación', icon: 'pi pi-book', to: '/manual' },
]
</script>

<template>
  <div class="layout">
    <Toast />
    <header class="header" :class="{ 'header-dark': theme === 'dark' }">
      <nav class="nav">
        <RouterLink to="/" class="brand">Cuponera Salchimonster</RouterLink>
        <RouterLink v-for="item in menuItems" :key="item.to" :to="item.to" class="nav-link" active-class="active">
          <i :class="item.icon" />
          <span>{{ item.label }}</span>
        </RouterLink>
        <Button
          :icon="theme === 'dark' ? 'pi pi-sun' : 'pi pi-moon'"
          :aria-label="theme === 'dark' ? 'Tema claro' : 'Tema oscuro'"
          text
          rounded
          class="theme-toggle"
          @click="toggleTheme"
        />
      </nav>
    </header>
    <main class="main">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.header {
  background: linear-gradient(135deg, #ff6200 0%, #cc4e00 100%);
  color: white;
  padding: 0.75rem 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  transition: background 0.2s ease, box-shadow 0.2s ease;
}
.header.header-dark {
  background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
  box-shadow: 0 2px 8px rgba(0,0,0,0.4);
}
.nav {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}
.theme-toggle {
  margin-left: auto;
  color: rgba(255,255,255,0.95) !important;
}
.theme-toggle:hover {
  color: white !important;
  background: rgba(255,255,255,0.2) !important;
}
.brand {
  font-weight: 700;
  font-size: 1.25rem;
  color: white;
  text-decoration: none;
  margin-right: 0.5rem;
}
.nav-link {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  color: rgba(255,255,255,0.9);
  text-decoration: none;
  padding: 0.4rem 0.75rem;
  border-radius: 6px;
  transition: background 0.2s;
}
.nav-link:hover {
  background: rgba(255,255,255,0.15);
  color: white;
}
.nav-link.active {
  background: rgba(255,255,255,0.25);
  color: white;
}
.main {
  flex: 1;
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}
</style>

<style>
:root {
  --brand: #ff6200;
  --brand-dark: #cc4e00;
  /* Botón principal = color dominante */
  --p-primary-500: #ff6200;
  --p-primary-600: #e55800;
  --p-primary-700: #cc4e00;
  --p-primary-color: #ffffff;
  --p-primary-contrast-color: #ffffff;
}
body {
  margin: 0;
  font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  background: #f5f5f5;
  transition: background-color 0.2s ease;
}
html.theme-dark body {
  background: #1c1c1c;
}
html.theme-dark .layout .main {
  background: transparent;
}
/* Toast en modo oscuro */
html.theme-dark .p-toast .p-toast-message {
  background: #2d2d2d !important;
  border: 1px solid #404040 !important;
  color: #e8e8e8 !important;
}
html.theme-dark .p-toast .p-toast-message .p-toast-message-content,
html.theme-dark .p-toast .p-toast-message-content {
  background: transparent !important;
  border: none !important;
  color: #e8e8e8 !important;
}
html.theme-dark .p-toast .p-toast-message-text,
html.theme-dark .p-toast .p-toast-summary,
html.theme-dark .p-toast .p-toast-detail,
html.theme-dark .p-toast [class*="summary"],
html.theme-dark .p-toast [class*="detail"] {
  color: #e8e8e8 !important;
}
html.theme-dark .p-toast .p-toast-message-success { border-left-color: #22c55e !important; }
html.theme-dark .p-toast .p-toast-message-info { border-left-color: #3b82f6 !important; }
html.theme-dark .p-toast .p-toast-message-warn { border-left-color: #f59e0b !important; }
html.theme-dark .p-toast .p-toast-message-error { border-left-color: #ef4444 !important; }
html.theme-dark .p-toast .p-toast-icon-close,
html.theme-dark .p-toast button[aria-label] {
  color: #a0aec0 !important;
}
html.theme-dark .p-toast .p-toast-icon-close:hover,
html.theme-dark .p-toast button[aria-label]:hover {
  color: #e2e8f0 !important;
}
/* Message (advertencias/errores) en modo oscuro */
html.theme-dark .p-message {
  background: #2d2d2d !important;
  border: 1px solid #404040 !important;
  color: #e8e8e8 !important;
}
html.theme-dark .p-message .p-message-content,
html.theme-dark .p-message-content {
  background: transparent !important;
  color: #e8e8e8 !important;
}
html.theme-dark .p-message.p-message-error { border-left-color: #ef4444 !important; }
html.theme-dark .p-message.p-message-success { border-left-color: #22c55e !important; }
html.theme-dark .p-message.p-message-info { border-left-color: #3b82f6 !important; }
html.theme-dark .p-message.p-message-warn { border-left-color: #f59e0b !important; }
html.theme-dark .p-message .p-message-icon,
html.theme-dark .p-message .p-icon {
  color: #e8e8e8 !important;
}
html.theme-dark .p-message .p-message-close-button,
html.theme-dark .p-message button[aria-label] {
  color: #a0aec0 !important;
}
html.theme-dark .p-message .p-message-close-button:hover,
html.theme-dark .p-message button[aria-label]:hover {
  color: #e2e8f0 !important;
}
/* Botón Cancelar (text) siempre en gris neutro, nunca verde. Excluir .theme-toggle del header */
.p-button.p-button-text:not(.theme-toggle) {
  color: #64748b !important;
}
.p-button.p-button-text:not(.theme-toggle) .p-button-icon,
.p-button.p-button-text:not(.theme-toggle) .p-icon {
  color: #64748b !important;
}
.p-button.p-button-text:not(.theme-toggle):hover {
  color: #475569 !important;
  background: rgba(0, 0, 0, 0.04) !important;
}
.p-button.p-button-text:not(.theme-toggle):hover .p-button-icon,
.p-button.p-button-text:not(.theme-toggle):hover .p-icon {
  color: #475569 !important;
}
html.theme-dark .p-button.p-button-text:not(.theme-toggle) {
  color: #a0aec0 !important;
}
html.theme-dark .p-button.p-button-text:not(.theme-toggle) .p-button-icon,
html.theme-dark .p-button.p-button-text:not(.theme-toggle) .p-icon {
  color: #a0aec0 !important;
}
html.theme-dark .p-button.p-button-text:not(.theme-toggle):hover {
  color: #e2e8f0 !important;
  background: rgba(255, 255, 255, 0.08) !important;
}
html.theme-dark .p-button.p-button-text:not(.theme-toggle):hover .p-button-icon,
html.theme-dark .p-button.p-button-text:not(.theme-toggle):hover .p-icon {
  color: #e2e8f0 !important;
}
/* Botón principal (default/primary) = color dominante #ff6200, texto blanco */
.p-button.p-button-primary,
.p-button:not(.p-button-secondary):not(.p-button-success):not(.p-button-info):not(.p-button-warn):not(.p-button-danger):not(.p-button-help):not(.p-button-outlined):not(.p-button-text) {
  background: #ff6200 !important;
  border-color: #ff6200 !important;
  color: #fff !important;
}
.p-button.p-button-primary .p-button-icon,
.p-button:not(.p-button-secondary):not(.p-button-success):not(.p-button-info):not(.p-button-warn):not(.p-button-danger):not(.p-button-help):not(.p-button-outlined):not(.p-button-text) .p-button-icon,
.p-button:not(.p-button-secondary):not(.p-button-success):not(.p-button-info):not(.p-button-warn):not(.p-button-danger):not(.p-button-help):not(.p-button-outlined):not(.p-button-text) .p-icon {
  color: #fff !important;
}
.p-button.p-button-primary:hover,
.p-button:not(.p-button-secondary):not(.p-button-success):not(.p-button-info):not(.p-button-warn):not(.p-button-danger):not(.p-button-help):not(.p-button-outlined):not(.p-button-text):hover {
  background: #cc4e00 !important;
  border-color: #cc4e00 !important;
  color: #fff !important;
}
.p-button.p-button-primary:hover .p-button-icon,
.p-button:not(.p-button-secondary):not(.p-button-success):not(.p-button-info):not(.p-button-warn):not(.p-button-danger):not(.p-button-help):not(.p-button-outlined):not(.p-button-text):hover .p-button-icon,
.p-button:not(.p-button-secondary):not(.p-button-success):not(.p-button-info):not(.p-button-warn):not(.p-button-danger):not(.p-button-help):not(.p-button-outlined):not(.p-button-text):hover .p-icon {
  color: #fff !important;
}
.p-button.p-button-primary:focus-visible,
.p-button:not(.p-button-secondary):not(.p-button-success):not(.p-button-info):not(.p-button-warn):not(.p-button-danger):not(.p-button-help):not(.p-button-outlined):not(.p-button-text):focus-visible {
  box-shadow: 0 0 0 0.2rem rgba(255, 98, 0, 0.4) !important;
}
</style>
