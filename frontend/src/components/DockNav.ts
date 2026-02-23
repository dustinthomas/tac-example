import { defineComponent, ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

interface DockItem {
  name: string
  icon: string
  route: string | null
}

const dockItems: DockItem[] = [
  {
    name: 'Foundry',
    route: '/dashboard',
    icon: '<svg class="dock-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>',
  },
  {
    name: 'Quantum',
    route: null,
    icon: '<svg class="dock-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>',
  },
  {
    name: 'Applications',
    route: null,
    icon: '<svg class="dock-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M4 8h4V4H4v4zm6 12h4v-4h-4v4zm-6 0h4v-4H4v4zm0-6h4v-4H4v4zm6 0h4v-4h-4v4zm6-10v4h4V4h-4zm-6 4h4V4h-4v4zm6 6h4v-4h-4v4zm0 6h4v-4h-4v4z"/></svg>',
  },
  {
    name: 'Analytics',
    route: null,
    icon: '<svg class="dock-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/></svg>',
  },
  {
    name: 'Equipment',
    route: '/equipment',
    icon: '<svg class="dock-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 14v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6m18 0v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4m18 0h-2m-2 0h-2m-2 0H7m2 0H5M3 6h.01M21 6h.01"/></svg>',
  },
  {
    name: 'Research',
    route: null,
    icon: '<svg class="dock-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M12 3L1 9l4 2.18v6L12 21l7-3.82v-6l2-1.09V17h2V9L12 3zm6.82 6L12 12.72 5.18 9 12 5.28 18.82 9zM17 15.99l-5 2.73-5-2.73v-3.72L12 15l5-2.73v3.72z"/></svg>',
  },
  {
    name: 'Settings',
    route: null,
    icon: '<svg class="dock-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M19.14 12.94c.04-.31.06-.63.06-.94 0-.31-.02-.63-.06-.94l2.03-1.58a.49.49 0 00.12-.61l-1.92-3.32a.488.488 0 00-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 00-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96a.488.488 0 00-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.04.31-.06.63-.06.94s.02.63.06.94l-2.03 1.58a.49.49 0 00-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/></svg>',
  },
  {
    name: 'Users',
    route: null,
    icon: '<svg class="dock-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>',
  },
]

export default defineComponent({
  name: 'DockNav',

  setup() {
    const router = useRouter()
    const route = useRoute()
    const dockHidden = ref(false)

    const isLoginRoute = computed(() => route.path === '/login')

    function isActive(item: DockItem): boolean {
      if (!item.route) return false
      return route.path === item.route
    }

    function navigate(item: DockItem) {
      if (item.route) {
        router.push(item.route)
      }
    }

    function toggleDock() {
      dockHidden.value = !dockHidden.value
    }

    return { dockItems, dockHidden, isLoginRoute, isActive, navigate, toggleDock }
  },

  template: `
    <div v-if="!isLoginRoute" class="dock-wrapper" :class="{ 'dock-hidden': dockHidden }">
      <button class="dock-toggle-tab" @click="toggleDock">
        <svg class="dock-toggle-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="7 10 12 15 17 10" />
        </svg>
      </button>

      <div class="dock-container">
        <nav class="dock" role="navigation" aria-label="Application dock">
          <div
            v-for="item in dockItems"
            :key="item.name"
            class="dock-item"
            :class="{ active: isActive(item) }"
            @click="navigate(item)"
          >
            <span v-html="item.icon"></span>
            <div class="active-dot"></div>
            <div class="tooltip">{{ item.name }}</div>
          </div>
        </nav>
      </div>
    </div>
  `,
})
