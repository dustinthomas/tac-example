import { defineComponent, computed } from 'vue'
import type { PropType } from 'vue'
import type { StatusType } from '../types/index.js'

const statusClassMap: Record<StatusType, string> = {
  'UP': 'up',
  'UP WITH ISSUES': 'up-with-issues',
  'MAINTENANCE': 'maintenance',
  'DOWN': 'down',
}

export default defineComponent({
  name: 'StatusBadge',

  props: {
    status: {
      type: String as PropType<StatusType>,
      required: true,
    },
  },

  setup(props) {
    const statusClass = computed(() => statusClassMap[props.status])

    return { statusClass }
  },

  template: `
    <span class="status-badge" :class="statusClass">
      <span class="status-dot"></span>
      {{ status }}
    </span>
  `,
})
