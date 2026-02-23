import { defineComponent, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

export default defineComponent({
  name: 'LogoutButton',

  setup() {
    const authStore = useAuthStore()
    const router = useRouter()

    const isAuthenticated = computed(() => authStore.isAuthenticated)

    function handleLogout() {
      authStore.logout()
      router.push('/login')
    }

    return { isAuthenticated, handleLogout }
  },

  template: `
    <template v-if="isAuthenticated">
      <button class="logout-btn logout-btn--fixed" @click="handleLogout">LOGOUT</button>
    </template>
  `,
})
