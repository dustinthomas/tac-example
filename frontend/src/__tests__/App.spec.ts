import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import App from '../App.js'
import LoginView from '../views/LoginView.js'
import DashboardView from '../views/DashboardView.js'

function makeRouter(initialRoute = '/login') {
  const router = createRouter({
    history: createWebHistory(),
    routes: [
      { path: '/', redirect: '/login' },
      { path: '/login', component: LoginView, meta: { public: true } },
      { path: '/dashboard', component: DashboardView },
    ],
  })
  router.push(initialRoute)
  return router
}

beforeEach(() => {
  localStorage.clear()
  // Mock fetch for EquipmentView's onMounted
  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: () => Promise.resolve([]),
  })
})

describe('App', () => {
  it('has LogoutButton registered', () => {
    const components = (App as any).components
    expect(components).toHaveProperty('LogoutButton')
  })

  it('renders LogoutButton when authenticated', async () => {
    localStorage.setItem('token', 'test-token')
    localStorage.setItem('user', JSON.stringify({ id: 1, username: 'admin', role: 'admin' }))
    const router = makeRouter('/dashboard')
    await router.isReady()
    const wrapper = mount(App, {
      global: { plugins: [router, createPinia()] },
    })
    expect(wrapper.find('.logout-btn').exists()).toBe(true)
  })

  it('renders QuantumBackground', async () => {
    const router = makeRouter('/login')
    await router.isReady()
    const wrapper = mount(App, {
      global: { plugins: [router, createPinia()] },
    })
    expect(wrapper.find('.quantum-bg').exists()).toBe(true)
  })

  it('hides DockNav on login route', async () => {
    const router = makeRouter('/login')
    await router.isReady()
    const wrapper = mount(App, {
      global: { plugins: [router, createPinia()] },
    })
    expect(wrapper.find('.dock-wrapper').exists()).toBe(false)
  })

  it('shows DockNav on dashboard route', async () => {
    localStorage.setItem('token', 'test-token')
    const router = makeRouter('/dashboard')
    await router.isReady()
    const wrapper = mount(App, {
      global: { plugins: [router, createPinia()] },
    })
    expect(wrapper.find('.dock-wrapper').exists()).toBe(true)
  })
})
