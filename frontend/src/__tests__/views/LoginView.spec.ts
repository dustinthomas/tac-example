import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import LoginView from '../../views/LoginView.js'

function makeRouter() {
  const router = createRouter({
    history: createWebHistory(),
    routes: [
      { path: '/login', component: LoginView },
      { path: '/dashboard', component: { template: '<div>dashboard</div>' } },
    ],
  })
  router.push('/login')
  return router
}

function mountLogin() {
  const pinia = createPinia()
  setActivePinia(pinia)
  const router = makeRouter()
  return { pinia, router }
}

beforeEach(() => {
  localStorage.clear()
})

describe('LoginView', () => {
  it('renders username and password fields', async () => {
    const { pinia, router } = mountLogin()
    await router.isReady()
    const wrapper = mount(LoginView, { global: { plugins: [router, pinia] } })

    expect(wrapper.find('#username').exists()).toBe(true)
    expect(wrapper.find('#password').exists()).toBe(true)
  })

  it('renders the login button', async () => {
    const { pinia, router } = mountLogin()
    await router.isReady()
    const wrapper = mount(LoginView, { global: { plugins: [router, pinia] } })

    expect(wrapper.find('.login-btn').exists()).toBe(true)
    expect(wrapper.find('.login-btn').text()).toBe('Login')
  })

  it('renders QCI logo and badge', async () => {
    const { pinia, router } = mountLogin()
    await router.isReady()
    const wrapper = mount(LoginView, { global: { plugins: [router, pinia] } })

    expect(wrapper.find('.qci-logo').exists()).toBe(true)
    expect(wrapper.find('.badge').text()).toBe('Quantum Ready')
  })

  it('shows error on failed login', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      json: () => Promise.resolve({ error: 'Invalid credentials' }),
    })

    const { pinia, router } = mountLogin()
    await router.isReady()
    const wrapper = mount(LoginView, { global: { plugins: [router, pinia] } })

    await wrapper.find('#username').setValue('admin')
    await wrapper.find('#password').setValue('wrong')
    await wrapper.find('.login-form').trigger('submit')
    await new Promise(r => setTimeout(r, 10))

    expect(wrapper.find('.login-error').text()).toBe('Invalid credentials')
  })

  it('navigates to /dashboard on successful login', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        token: 'test-token',
        user: { id: 1, username: 'admin', role: 'admin' },
      }),
    })

    const { pinia, router } = mountLogin()
    await router.isReady()
    const wrapper = mount(LoginView, { global: { plugins: [router, pinia] } })

    await wrapper.find('#username').setValue('admin')
    await wrapper.find('#password').setValue('admin123')
    await wrapper.find('.login-form').trigger('submit')
    await new Promise(r => setTimeout(r, 10))
    await router.isReady()

    expect(router.currentRoute.value.path).toBe('/dashboard')
    expect(localStorage.getItem('token')).toBe('test-token')
  })
})
