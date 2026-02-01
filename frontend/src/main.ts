import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import ToastService from 'primevue/toastservice'
import Tooltip from 'primevue/tooltip'

import App from './App.vue'
import router from './router'

import 'primeicons/primeicons.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ToastService)
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      prefix: 'p',
      darkModeSelector: '.theme-dark',
      cssLayer: false,
    },
    semantic: {
      primary: {
        50: '{orange.50}',
        100: '{orange.100}',
        200: '{orange.200}',
        300: '{orange.300}',
        400: '{orange.400}',
        500: '#ff6200',
        600: '#e55800',
        700: '#cc4e00',
        800: '#b34500',
        900: '#993b00',
      },
    },
  },
})
app.directive('tooltip', Tooltip)

app.mount('#app')
