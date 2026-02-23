import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import AppHeader from '../../components/AppHeader.js'

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

describe('AppHeader', () => {
  let pinia: ReturnType<typeof createPinia>

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    localStorage.clear()
  })

  it('renders .app-header element', async () => {
    const router = makeRouter()
    await router.isReady()
    const wrapper = mount(AppHeader, { global: { plugins: [pinia, router] } })
    expect(wrapper.find('.app-header').exists()).toBe(true)
  })
})
