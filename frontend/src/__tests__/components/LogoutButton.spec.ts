import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import LogoutButton from '../../components/LogoutButton.js'
import { useAuthStore } from '../../stores/auth.js'

function makeRouter(initialRoute = '/dashboard') {
  const router = createRouter({
    history: createWebHistory(),
    routes: [
      { path: '/login', component: { template: '<div>login</div>' } },
      { path: '/dashboard', component: { template: '<div>dashboard</div>' } },
    ],
  })
  router.push(initialRoute)
  return router
}

describe('LogoutButton', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('does not render when not authenticated', async () => {
    const pinia = createPinia()
    setActivePinia(pinia)
    const router = makeRouter()
    await router.isReady()
    const wrapper = mount(LogoutButton, { global: { plugins: [pinia, router] } })
    expect(wrapper.find('.logout-btn').exists()).toBe(false)
  })

  it('renders button with class logout-btn when authenticated', async () => {
    localStorage.setItem('token', 'test-token')
    localStorage.setItem('user', JSON.stringify({ id: 1, username: 'admin', role: 'admin' }))
    const pinia = createPinia()
    setActivePinia(pinia)
    const router = makeRouter()
    await router.isReady()
    const wrapper = mount(LogoutButton, { global: { plugins: [pinia, router] } })
    expect(wrapper.find('.logout-btn').exists()).toBe(true)
  })

  it('button text is LOGOUT', async () => {
    localStorage.setItem('token', 'test-token')
    localStorage.setItem('user', JSON.stringify({ id: 1, username: 'admin', role: 'admin' }))
    const pinia = createPinia()
    setActivePinia(pinia)
    const router = makeRouter()
    await router.isReady()
    const wrapper = mount(LogoutButton, { global: { plugins: [pinia, router] } })
    expect(wrapper.find('.logout-btn').text()).toBe('LOGOUT')
  })

  it('clicking calls authStore.logout()', async () => {
    localStorage.setItem('token', 'test-token')
    localStorage.setItem('user', JSON.stringify({ id: 1, username: 'admin', role: 'admin' }))
    const pinia = createPinia()
    setActivePinia(pinia)
    const router = makeRouter()
    await router.isReady()
    const wrapper = mount(LogoutButton, { global: { plugins: [pinia, router] } })
    const authStore = useAuthStore()
    const logoutSpy = vi.spyOn(authStore, 'logout')
    await wrapper.find('.logout-btn').trigger('click')
    expect(logoutSpy).toHaveBeenCalledOnce()
  })

  it('after click, authStore.isAuthenticated is false', async () => {
    localStorage.setItem('token', 'test-token')
    localStorage.setItem('user', JSON.stringify({ id: 1, username: 'admin', role: 'admin' }))
    const pinia = createPinia()
    setActivePinia(pinia)
    const router = makeRouter()
    await router.isReady()
    const wrapper = mount(LogoutButton, { global: { plugins: [pinia, router] } })
    const authStore = useAuthStore()
    await wrapper.find('.logout-btn').trigger('click')
    expect(authStore.isAuthenticated).toBe(false)
  })

  it('after click, localStorage token is null', async () => {
    localStorage.setItem('token', 'test-token')
    localStorage.setItem('user', JSON.stringify({ id: 1, username: 'admin', role: 'admin' }))
    const pinia = createPinia()
    setActivePinia(pinia)
    const router = makeRouter()
    await router.isReady()
    const wrapper = mount(LogoutButton, { global: { plugins: [pinia, router] } })
    await wrapper.find('.logout-btn').trigger('click')
    expect(localStorage.getItem('token')).toBeNull()
  })

  it('after click, router navigates to /login', async () => {
    localStorage.setItem('token', 'test-token')
    localStorage.setItem('user', JSON.stringify({ id: 1, username: 'admin', role: 'admin' }))
    const pinia = createPinia()
    setActivePinia(pinia)
    const router = makeRouter('/dashboard')
    await router.isReady()
    const wrapper = mount(LogoutButton, { global: { plugins: [pinia, router] } })
    await wrapper.find('.logout-btn').trigger('click')
    await new Promise(resolve => setTimeout(resolve, 50))
    expect(router.currentRoute.value.path).toBe('/login')
  })
})
