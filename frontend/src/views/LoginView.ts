import { defineComponent, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

export default defineComponent({
  name: 'LoginView',

  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const username = ref('')
    const password = ref('')
    const error = ref('')
    const loading = ref(false)

    async function handleLogin() {
      error.value = ''
      loading.value = true
      try {
        await authStore.login(username.value, password.value)
        router.push('/dashboard')
      } catch (e) {
        error.value = e instanceof Error ? e.message : 'Login failed'
      } finally {
        loading.value = false
      }
    }

    return { username, password, error, loading, handleLogin }
  },

  template: `
    <div class="main-content">
      <div class="login-container">
        <div class="glass-panel">
          <div class="logo-section">
            <svg class="qci-logo" viewBox="0 0 464 142" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M1.61887 58.5544C3.98887 46.9444 7.05887 39.1344 13.0089 30.7444C24.6089 14.3744 41.8389 3.92443 61.5489 2.62443C91.3389 0.644434 121.779 -0.995559 151.199 2.83444C195.869 8.65444 220.539 46.4644 209.679 86.0944C208.309 91.0944 205.929 95.8344 203.399 102.254C191.949 92.9044 181.539 84.5544 171.379 75.9444C170.019 74.7944 169.479 72.3344 169.159 70.3844C165.579 48.4544 153.899 37.1344 131.549 35.9944C114.789 35.1444 97.9089 35.1144 81.1489 35.9944C59.2989 37.1344 44.5989 50.5544 43.9289 68.3544C43.2189 87.2544 56.2489 101.214 77.9989 103.204C89.9789 104.304 102.149 103.404 116.249 103.404C110.319 98.1644 105.599 94.0044 100.889 89.8444C101.319 89.0544 101.759 88.2744 102.189 87.4844C121.009 87.4844 139.829 87.4544 158.659 87.5444C159.999 87.5444 161.599 88.0644 162.619 88.8944C182.329 104.974 201.969 121.144 221.629 137.294C221.349 138.344 221.909 140.084 221.629 141.134H164.279C160.889 140.964 161.059 137.234 157.669 137.064C154.179 136.894 150.659 137.664 147.149 137.704C121.099 138.004 94.7689 140.744 69.0789 137.864C33.9389 133.924 6.26887 115.624 0.988865 78.7144C0.518865 75.4344 -0.241134 69.3544 1.61887 58.5544Z" fill="#00BCD4"/>
              <path d="M406.559 103.744V139.404C389.659 139.404 373.309 139.684 356.979 139.334C333.059 138.824 308.769 140.264 285.329 136.554C243.989 130.004 219.379 96.1744 225.089 57.5044C229.019 30.8744 246.679 15.2544 270.869 6.21442C279.449 3.00442 288.879 0.544422 297.969 0.384422C333.719 -0.275578 369.489 0.114433 406.199 0.114433V35.6944C399.289 35.6944 392.589 35.6944 385.899 35.6944C360.139 35.6944 334.369 35.4844 308.619 35.7744C286.649 36.0244 270.179 47.9244 267.749 64.5544C264.579 86.2544 280.849 103.174 306.389 103.594C335.719 104.084 365.069 103.734 394.409 103.744C398.249 103.744 402.089 103.744 406.579 103.744H406.559Z" fill="#00BCD4"/>
              <path d="M463.829 49.3844V138.604H421.829V49.3844H463.829Z" fill="#00BCD4"/>
              <path d="M463.859 35.1744H421.799V0.644409H463.859V35.1744Z" fill="#00BCD4"/>
            </svg>
            <span class="logo-subtitle">Fab Interface</span>
          </div>

          <div class="badge">Quantum Ready</div>

          <h1>Login to Fab UI</h1>
          <div class="quantum-line"></div>

          <div v-if="error" class="login-error">{{ error }}</div>

          <form class="login-form" @submit.prevent="handleLogin">
            <div class="form-group">
              <label for="username">Username</label>
              <input id="username" v-model="username" type="text" placeholder="Enter username" :disabled="loading">
            </div>
            <div class="form-group">
              <label for="password">Password</label>
              <input id="password" v-model="password" type="password" placeholder="Enter password" :disabled="loading">
            </div>
            <button type="submit" class="login-btn" :disabled="loading">
              {{ loading ? 'Logging in...' : 'Login' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  `,
})
