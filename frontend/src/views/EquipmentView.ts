import { defineComponent, ref, computed, onMounted } from 'vue'
import StatusBadge from '../components/StatusBadge.js'
import AppHeader from '../components/AppHeader.js'
import { useEquipmentStore } from '../stores/equipment.js'
import type { StatusType, FabArea, StatusSummary } from '../types/index.js'

const criticalityClassMap: Record<string, string> = {
  'Critical': 'critical',
  'High': 'high',
  'Medium': 'medium',
  'Low': 'low',
}

export default defineComponent({
  name: 'EquipmentView',

  components: { StatusBadge, AppHeader },

  setup() {
    const equipmentStore = useEquipmentStore()
    const statusFilter = ref<string>('all')
    const areaFilter = ref<string>('all')
    const searchQuery = ref('')

    const areas: FabArea[] = ['Lithography', 'Etching', 'Deposition', 'Metrology']
    const statuses: StatusType[] = ['UP', 'UP WITH ISSUES', 'MAINTENANCE', 'DOWN']

    onMounted(() => {
      equipmentStore.fetchEquipment()
    })

    const filteredEquipment = computed(() => {
      return equipmentStore.equipment.filter(eq => {
        if (statusFilter.value !== 'all' && eq.status !== statusFilter.value) return false
        if (areaFilter.value !== 'all' && eq.area !== areaFilter.value) return false
        if (searchQuery.value) {
          const query = searchQuery.value.toLowerCase()
          return eq.name.toLowerCase().includes(query) ||
                 eq.description.toLowerCase().includes(query)
        }
        return true
      })
    })

    const statusSummary = computed<StatusSummary>(() => ({
      up: equipmentStore.equipment.filter(e => e.status === 'UP').length,
      issues: equipmentStore.equipment.filter(e => e.status === 'UP WITH ISSUES').length,
      maintenance: equipmentStore.equipment.filter(e => e.status === 'MAINTENANCE').length,
      down: equipmentStore.equipment.filter(e => e.status === 'DOWN').length,
    }))

    function criticalityClass(level: string): string {
      return criticalityClassMap[level] || ''
    }

    function formatDate(dateStr: string): string {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      const now = new Date()
      const diffMs = now.getTime() - date.getTime()
      const diffMins = Math.floor(diffMs / 60000)
      if (diffMins < 1) return 'Just now'
      if (diffMins < 60) return `${diffMins} min ago`
      const diffHours = Math.floor(diffMins / 60)
      if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
      const diffDays = Math.floor(diffHours / 24)
      return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
    }

    return {
      equipmentStore,
      statusFilter,
      areaFilter,
      searchQuery,
      areas,
      statuses,
      filteredEquipment,
      statusSummary,
      criticalityClass,
      formatDate,
    }
  },

  template: `
    <div class="main-content" style="justify-content: flex-start; padding-top: 40px;">
      <div class="equipment-dashboard">
        <AppHeader />
        <div class="equipment-header">
          <div style="display:flex;align-items:center;gap:14px;">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 14v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6m18 0v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4m18 0h-2m-2 0h-2m-2 0H7m2 0H5M3 6h.01M21 6h.01"/>
            </svg>
            <div>
              <h1>Equipment Status</h1>
              <p>Real-time monitoring of fab equipment across all areas</p>
            </div>
          </div>
          <div class="status-chips">
            <div class="status-chip up">
              <span class="chip-count">{{ statusSummary.up }}</span>
              <span class="chip-label">Operational</span>
            </div>
            <div class="status-chip issues">
              <span class="chip-count">{{ statusSummary.issues }}</span>
              <span class="chip-label">With Issues</span>
            </div>
            <div class="status-chip maintenance">
              <span class="chip-count">{{ statusSummary.maintenance }}</span>
              <span class="chip-label">Maintenance</span>
            </div>
            <div class="status-chip down">
              <span class="chip-count">{{ statusSummary.down }}</span>
              <span class="chip-label">Down</span>
            </div>
          </div>
        </div>

        <div v-if="equipmentStore.error" class="equipment-error">
          {{ equipmentStore.error }}
        </div>

        <div class="filter-bar">
          <div class="filter-group">
            <label>Status</label>
            <select v-model="statusFilter">
              <option value="all">All Statuses</option>
              <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>
          <div class="filter-group">
            <label>Area</label>
            <select v-model="areaFilter">
              <option value="all">All Areas</option>
              <option v-for="a in areas" :key="a" :value="a">{{ a }}</option>
            </select>
          </div>
          <div class="filter-group">
            <label>Search</label>
            <input v-model="searchQuery" type="text" placeholder="Search equipment...">
          </div>
          <div class="equipment-count">
            Showing <span>{{ filteredEquipment.length }}</span> equipment
          </div>
        </div>

        <div v-if="equipmentStore.loading" class="equipment-loading">
          Loading equipment...
        </div>

        <div v-else class="equipment-table-wrapper">
          <table class="equipment-table">
            <thead>
              <tr>
                <th>Equipment</th>
                <th>Area</th>
                <th>Bay</th>
                <th>Status</th>
                <th>Criticality</th>
                <th>Updated By</th>
                <th>Last Updated</th>
                <th>Last Comment</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="eq in filteredEquipment" :key="eq.id">
                <td>
                  <strong>{{ eq.name }}</strong><br>
                  <span style="color: rgba(255,255,255,0.4); font-size: 0.8rem;">{{ eq.description }}</span>
                </td>
                <td><span class="area-badge">{{ eq.area }}</span></td>
                <td>{{ eq.bay }}</td>
                <td><StatusBadge :status="eq.status" /></td>
                <td><span class="criticality-badge" :class="criticalityClass(eq.criticality)">{{ eq.criticality }}</span></td>
                <td>{{ eq.updated_by }}</td>
                <td style="color: rgba(255,255,255,0.5);">{{ formatDate(eq.updated_at) }}</td>
                <td style="color: rgba(255,255,255,0.5);">{{ eq.last_comment }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `,
})
