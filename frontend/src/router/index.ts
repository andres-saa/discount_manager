import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/descuentos' },
    { path: '/carpetas', name: 'Carpetas', component: () => import('../views/CarpetasView.vue'), meta: { title: 'Carpetas' } },
    { path: '/descuentos', name: 'Descuentos', component: () => import('../views/DescuentosView.vue'), meta: { title: 'Descuentos' } },
    { path: '/cuponeras', name: 'Cuponeras', component: () => import('../views/CuponerasView.vue'), meta: { title: 'Cuponeras' } },
    { path: '/cuponeras/:id/usuarios', name: 'CuponeraUsuarios', component: () => import('../views/CuponeraUsuariosView.vue'), meta: { title: 'Usuarios cuponera' } },
    { path: '/consultar', name: 'Consultar', component: () => import('../views/ConsultarView.vue'), meta: { title: 'Consultar cupón' } },
    { path: '/pagar', name: 'Pagar', component: () => import('../views/PagarView.vue'), meta: { title: 'Pagar' } },
    { path: '/manual', name: 'Documentación', component: () => import('../views/ManualView.vue'), meta: { title: 'Documentación' } },
  ],
})

router.afterEach((to) => {
  const title = (to.meta?.title as string) || 'Cuponera'
  document.title = `${title} | Salchimonster`
})

export default router
