import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import LoginView from './views/LoginView.js'
import DashboardView from './views/DashboardView.js'
import EquipmentView from './views/EquipmentView.js'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'login', component: LoginView, meta: { public: true } },
  { path: '/dashboard', name: 'dashboard', component: DashboardView },
  { path: '/equipment', name: 'equipment', component: EquipmentView },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const isPublic = to.meta?.public === true
  const token = localStorage.getItem('token')

  if (!isPublic && !token) {
    next({ name: 'login' })
  } else if (to.name === 'login' && token) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
})
