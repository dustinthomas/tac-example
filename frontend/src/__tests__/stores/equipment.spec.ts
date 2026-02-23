import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useEquipmentStore } from '../../stores/equipment.js'
import type { Equipment } from '../../types/index.js'

const mockEquipment: Equipment[] = [
  { id: 1, name: 'E-Beam Lithography System', description: 'Electron Beam Writer', area: 'Lithography', bay: 'Bay 1A', status: 'UP', criticality: 'Critical', updated_by: 'admin', last_comment: 'Calibration complete', created_at: '2026-02-16T00:00:00Z', updated_at: '2026-02-16T00:00:00Z' },
  { id: 2, name: 'RIE Plasma Etcher', description: 'Reactive Ion Etcher', area: 'Etching', bay: 'Bay 2B', status: 'DOWN', criticality: 'High', updated_by: 'operator', last_comment: 'RF power issue', created_at: '2026-02-16T00:00:00Z', updated_at: '2026-02-16T00:00:00Z' },
]

beforeEach(() => {
  setActivePinia(createPinia())
  localStorage.setItem('token', 'test-token')
})

describe('equipment store', () => {
  it('starts with empty equipment list', () => {
    const store = useEquipmentStore()
    expect(store.equipment).toEqual([])
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('fetchEquipment loads data', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockEquipment),
    })

    const store = useEquipmentStore()
    await store.fetchEquipment()

    expect(store.equipment.length).toBe(2)
    expect(store.equipment[0].name).toBe('E-Beam Lithography System')
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('fetchEquipment sets error on failure', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      json: () => Promise.resolve({ error: 'Unauthorized' }),
    })

    const store = useEquipmentStore()
    await store.fetchEquipment()

    expect(store.equipment).toEqual([])
    expect(store.error).toBe('Unauthorized')
    expect(store.loading).toBe(false)
  })

  it('fetchEquipment sets loading during fetch', async () => {
    let resolvePromise: (value: unknown) => void
    const pending = new Promise(r => { resolvePromise = r })

    globalThis.fetch = vi.fn().mockReturnValue(pending)

    const store = useEquipmentStore()
    const fetchPromise = store.fetchEquipment()

    expect(store.loading).toBe(true)

    resolvePromise!({
      ok: true,
      json: () => Promise.resolve([]),
    })
    await fetchPromise

    expect(store.loading).toBe(false)
  })

  it('updateEquipmentStatus updates item in list', async () => {
    const updatedItem: Equipment = { ...mockEquipment[1], status: 'UP', last_comment: 'Fixed' }

    // First mock for fetchEquipment
    globalThis.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockEquipment),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(updatedItem),
      })

    const store = useEquipmentStore()
    await store.fetchEquipment()
    expect(store.equipment[1].status).toBe('DOWN')

    await store.updateEquipmentStatus(2, 'UP', 'Fixed')
    expect(store.equipment[1].status).toBe('UP')
    expect(store.equipment[1].last_comment).toBe('Fixed')
  })
})
