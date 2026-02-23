import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StatusBadge from '../../components/StatusBadge.js'

describe('StatusBadge', () => {
  it('renders UP status with correct class', () => {
    const wrapper = mount(StatusBadge, { props: { status: 'UP' } })
    expect(wrapper.find('.status-badge.up').exists()).toBe(true)
    expect(wrapper.text()).toContain('UP')
  })

  it('renders UP WITH ISSUES status with correct class', () => {
    const wrapper = mount(StatusBadge, { props: { status: 'UP WITH ISSUES' } })
    expect(wrapper.find('.status-badge.up-with-issues').exists()).toBe(true)
  })

  it('renders MAINTENANCE status with correct class', () => {
    const wrapper = mount(StatusBadge, { props: { status: 'MAINTENANCE' } })
    expect(wrapper.find('.status-badge.maintenance').exists()).toBe(true)
  })

  it('renders DOWN status with correct class', () => {
    const wrapper = mount(StatusBadge, { props: { status: 'DOWN' } })
    expect(wrapper.find('.status-badge.down').exists()).toBe(true)
  })

  it('renders the pulsing status dot', () => {
    const wrapper = mount(StatusBadge, { props: { status: 'UP' } })
    expect(wrapper.find('.status-dot').exists()).toBe(true)
  })
})
