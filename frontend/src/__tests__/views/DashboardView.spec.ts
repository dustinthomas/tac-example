import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../../views/DashboardView.js'

function makeRouter() {
  const router = createRouter({
    history: createWebHistory(),
    routes: [
      { path: '/login', component: { template: '<div>login</div>' } },
      { path: '/dashboard', component: { template: '<div>dashboard</div>' } },
    ],
  })
  router.push('/dashboard')
  return router
}

describe('DashboardView', () => {
  let pinia: ReturnType<typeof createPinia>

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    localStorage.clear()
  })

  it('renders the page title', async () => {
    const router = makeRouter()
    await router.isReady()
    const wrapper = mount(DashboardView, { global: { plugins: [pinia, router] } })
    expect(wrapper.find('h1').text()).toBe('QCI Foundry Services')
  })

  it('renders 4 feature cards', async () => {
    const router = makeRouter()
    await router.isReady()
    const wrapper = mount(DashboardView, { global: { plugins: [pinia, router] } })
    const cards = wrapper.findAll('.feature-card')
    expect(cards.length).toBe(4)
  })

  it('renders correct feature card titles', async () => {
    const router = makeRouter()
    await router.isReady()
    const wrapper = mount(DashboardView, { global: { plugins: [pinia, router] } })
    const titles = wrapper.findAll('.feature-card h3').map(el => el.text())
    expect(titles).toEqual([
      'TFLN Fabrication',
      'Photonic Engines',
      'Room Temperature',
      'Scalable Production',
    ])
  })
})
