import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import DockNav from '../../components/DockNav.js'

function makeRouter(initialRoute = '/dashboard') {
  const router = createRouter({
    history: createWebHistory(),
    routes: [
      { path: '/login', component: { template: '<div>login</div>' } },
      { path: '/dashboard', component: { template: '<div>dashboard</div>' } },
      { path: '/equipment', component: { template: '<div>equipment</div>' } },
    ],
  })
  router.push(initialRoute)
  return router
}

describe('DockNav', () => {
  it('renders dock items on non-login routes', async () => {
    const router = makeRouter('/dashboard')
    await router.isReady()
    const wrapper = mount(DockNav, { global: { plugins: [router] } })
    expect(wrapper.findAll('.dock-item').length).toBe(8)
  })

  it('hides dock on login route', async () => {
    const router = makeRouter('/login')
    await router.isReady()
    const wrapper = mount(DockNav, { global: { plugins: [router] } })
    expect(wrapper.find('.dock-wrapper').exists()).toBe(false)
  })

  it('marks Foundry as active on /dashboard', async () => {
    const router = makeRouter('/dashboard')
    await router.isReady()
    const wrapper = mount(DockNav, { global: { plugins: [router] } })
    const items = wrapper.findAll('.dock-item')
    expect(items[0].classes()).toContain('active')
  })

  it('marks Equipment as active on /equipment', async () => {
    const router = makeRouter('/equipment')
    await router.isReady()
    const wrapper = mount(DockNav, { global: { plugins: [router] } })
    const items = wrapper.findAll('.dock-item')
    // Equipment is index 4 in the dock items array
    expect(items[4].classes()).toContain('active')
  })

  it('toggles dock hidden state when toggle button is clicked', async () => {
    const router = makeRouter('/dashboard')
    await router.isReady()
    const wrapper = mount(DockNav, { global: { plugins: [router] } })
    const toggle = wrapper.find('.dock-toggle-tab')

    expect(wrapper.find('.dock-wrapper').classes()).not.toContain('dock-hidden')
    await toggle.trigger('click')
    expect(wrapper.find('.dock-wrapper').classes()).toContain('dock-hidden')
    await toggle.trigger('click')
    expect(wrapper.find('.dock-wrapper').classes()).not.toContain('dock-hidden')
  })
})
