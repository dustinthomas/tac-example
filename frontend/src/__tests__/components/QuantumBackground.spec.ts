import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import QuantumBackground from '../../components/QuantumBackground.js'

describe('QuantumBackground', () => {
  it('renders the quantum background div', () => {
    const wrapper = mount(QuantumBackground)
    expect(wrapper.find('.quantum-bg').exists()).toBe(true)
  })

  it('renders 10 particle divs', () => {
    const wrapper = mount(QuantumBackground)
    const particles = wrapper.find('.quantum-particles')
    expect(particles.exists()).toBe(true)
    expect(particles.findAll('div').length).toBe(10)
  })
})
