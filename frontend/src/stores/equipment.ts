import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchEquipment as apiFetchEquipment, updateEquipment as apiUpdateEquipment } from '../api.js'
import type { Equipment } from '../types/index.js'

export const useEquipmentStore = defineStore('equipment', () => {
  const equipment = ref<Equipment[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchEquipment(filters?: {
    status?: string
    area?: string
    search?: string
  }) {
    loading.value = true
    error.value = null
    try {
      equipment.value = await apiFetchEquipment(filters)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch equipment'
    } finally {
      loading.value = false
    }
  }

  async function updateEquipmentStatus(id: number, status: string, comment: string) {
    error.value = null
    try {
      const updated = await apiUpdateEquipment(id, status, comment)
      const idx = equipment.value.findIndex(e => e.id === id)
      if (idx !== -1) {
        equipment.value[idx] = updated
      }
      return updated
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update equipment'
      throw e
    }
  }

  return { equipment, loading, error, fetchEquipment, updateEquipmentStatus }
})
