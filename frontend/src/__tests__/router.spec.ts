import { describe, it, expect, beforeEach } from 'vitest'
import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.js'
import DashboardView from '../views/DashboardView.js'
import EquipmentView from '../views/EquipmentView.js'

function makeRouter() {
  const r = createRouter({
    history: createWebHistory(),
    routes: [
      { path: '/', redirect: '/login' },
      { path: '/login', name: 'login', component: LoginView, meta: { public: true } },
      { path: '/dashboard', name: 'dashboard', component: DashboardView },
      { path: '/equipment', name: 'equipment', component: EquipmentView },
    ],
  })

  r.beforeEach((to, _from, next) => {
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

  return r
}

beforeEach(() => {
  localStorage.clear()
})

describe('router guards', () => {
  it('redirects unauthenticated users to /login', async () => {
    const router = makeRouter()
    router.push('/dashboard')
    await router.isReady()
    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('allows unauthenticated access to /login', async () => {
    const router = makeRouter()
    router.push('/login')
    await router.isReady()
    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('allows authenticated access to /dashboard', async () => {
    localStorage.setItem('token', 'test-token')
    const router = makeRouter()
    router.push('/dashboard')
    await router.isReady()
    expect(router.currentRoute.value.path).toBe('/dashboard')
  })

  it('redirects authenticated users from /login to /dashboard', async () => {
    localStorage.setItem('token', 'test-token')
    const router = makeRouter()
    router.push('/login')
    await router.isReady()
    expect(router.currentRoute.value.path).toBe('/dashboard')
  })

  it('redirects unauthenticated users from /equipment to /login', async () => {
    const router = makeRouter()
    router.push('/equipment')
    await router.isReady()
    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('allows authenticated access to /equipment', async () => {
    localStorage.setItem('token', 'test-token')
    const router = makeRouter()
    router.push('/equipment')
    await router.isReady()
    expect(router.currentRoute.value.path).toBe('/equipment')
  })
})
