import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import EquipmentView from '../../views/EquipmentView.js'
import type { Equipment } from '../../types/index.js'

const mockEquipment: Equipment[] = [
  { id: 1, name: 'E-Beam Lithography System', description: 'Electron Beam Writer', area: 'Lithography', bay: 'Bay 1A', status: 'UP', criticality: 'Critical', updated_by: 'admin', last_comment: 'Calibration complete', created_at: '2026-02-16T00:00:00Z', updated_at: '2026-02-16T00:00:00Z' },
  { id: 2, name: 'RIE Plasma Etcher', description: 'Reactive Ion Etcher', area: 'Etching', bay: 'Bay 2B', status: 'UP WITH ISSUES', criticality: 'High', updated_by: 'operator', last_comment: 'RF power fluctuating', created_at: '2026-02-16T00:00:00Z', updated_at: '2026-02-16T00:00:00Z' },
  { id: 3, name: 'PECVD Chamber A', description: 'Plasma CVD System', area: 'Deposition', bay: 'Bay 3A', status: 'MAINTENANCE', criticality: 'Medium', updated_by: 'admin', last_comment: 'Scheduled PM in progress', created_at: '2026-02-16T00:00:00Z', updated_at: '2026-02-16T00:00:00Z' },
  { id: 4, name: 'Wafer Prober Station', description: 'Electrical Test System', area: 'Metrology', bay: 'Bay 4C', status: 'DOWN', criticality: 'Critical', updated_by: 'operator', last_comment: 'Stage motor failure', created_at: '2026-02-16T00:00:00Z', updated_at: '2026-02-16T00:00:00Z' },
  { id: 5, name: 'Sputter Deposition Tool', description: 'PVD Magnetron Sputter', area: 'Deposition', bay: 'Bay 3B', status: 'UP', criticality: 'Low', updated_by: 'admin', last_comment: 'Running batch 47', created_at: '2026-02-16T00:00:00Z', updated_at: '2026-02-16T00:00:00Z' },
  { id: 6, name: 'Optical Profilometer', description: 'Surface Metrology', area: 'Metrology', bay: 'Bay 4A', status: 'UP', criticality: 'Medium', updated_by: 'operator', last_comment: 'Ready for use', created_at: '2026-02-16T00:00:00Z', updated_at: '2026-02-16T00:00:00Z' },
]

function mockFetch() {
  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: () => Promise.resolve(mockEquipment),
  })
}

function makeRouter() {
  const router = createRouter({
    history: createWebHistory(),
    routes: [
      { path: '/login', component: { template: '<div>login</div>' } },
      { path: '/equipment', component: { template: '<div>equipment</div>' } },
    ],
  })
  router.push('/equipment')
  return router
}

function mountEquipment() {
  const pinia = createPinia()
  setActivePinia(pinia)
  const router = makeRouter()
  return mount(EquipmentView, { global: { plugins: [pinia, router] } })
}

beforeEach(() => {
  localStorage.setItem('token', 'test-token')
  mockFetch()
})

describe('EquipmentView', () => {
  it('renders the equipment table with all 6 rows', async () => {
    const wrapper = mountEquipment()
    await flushPromises()

    const rows = wrapper.findAll('.equipment-table tbody tr')
    expect(rows.length).toBe(6)
  })

  it('renders status summary chips', async () => {
    const wrapper = mountEquipment()
    await flushPromises()

    const chips = wrapper.findAll('.status-chip')
    expect(chips.length).toBe(4)
  })

  it('shows correct status summary counts', async () => {
    const wrapper = mountEquipment()
    await flushPromises()

    const counts = wrapper.findAll('.status-chip .chip-count').map(el => el.text())
    // 3 UP, 1 UP WITH ISSUES, 1 MAINTENANCE, 1 DOWN
    expect(counts).toEqual(['3', '1', '1', '1'])
  })

  it('filters by status', async () => {
    const wrapper = mountEquipment()
    await flushPromises()

    const select = wrapper.find('.filter-bar select')
    await select.setValue('DOWN')

    const rows = wrapper.findAll('.equipment-table tbody tr')
    expect(rows.length).toBe(1)
    expect(rows[0].text()).toContain('Wafer Prober Station')
  })

  it('filters by area', async () => {
    const wrapper = mountEquipment()
    await flushPromises()

    const selects = wrapper.findAll('.filter-bar select')
    await selects[1].setValue('Deposition')

    const rows = wrapper.findAll('.equipment-table tbody tr')
    expect(rows.length).toBe(2)
  })

  it('filters by search query', async () => {
    const wrapper = mountEquipment()
    await flushPromises()

    const input = wrapper.find('.filter-bar input[type="text"]')
    await input.setValue('Prober')

    const rows = wrapper.findAll('.equipment-table tbody tr')
    expect(rows.length).toBe(1)
    expect(rows[0].text()).toContain('Wafer Prober Station')
  })

  it('displays correct equipment count', async () => {
    const wrapper = mountEquipment()
    await flushPromises()

    expect(wrapper.find('.equipment-count span').text()).toBe('6')

    const input = wrapper.find('.filter-bar input[type="text"]')
    await input.setValue('Prober')
    expect(wrapper.find('.equipment-count span').text()).toBe('1')
  })

  it('renders chip labels with correct text for each status type', async () => {
    const wrapper = mountEquipment()
    await flushPromises()

    const labels = wrapper.findAll('.status-chip .chip-label').map(el => el.text())
    expect(labels).toEqual(['Operational', 'With Issues', 'Maintenance', 'Down'])
  })

  it('applies correct status variant classes to chips', async () => {
    const wrapper = mountEquipment()
    await flushPromises()

    const chips = wrapper.findAll('.status-chip')
    expect(chips[0].classes()).toContain('up')
    expect(chips[1].classes()).toContain('issues')
    expect(chips[2].classes()).toContain('maintenance')
    expect(chips[3].classes()).toContain('down')
  })

  it('fetches equipment from API on mount', async () => {
    mountEquipment()
    await flushPromises()

    expect(globalThis.fetch).toHaveBeenCalledWith(
      '/api/equipment',
      expect.objectContaining({
        headers: expect.any(Headers),
      })
    )
  })
})
