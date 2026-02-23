import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin } from '../api.js'
import type { User } from '../types/index.js'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(
    (() => {
      const stored = localStorage.getItem('user')
      return stored ? JSON.parse(stored) as User : null
    })()
  )

  const isAuthenticated = computed(() => !!token.value)

  async function login(username: string, password: string) {
    const response = await apiLogin(username, password)
    token.value = response.token
    user.value = response.user
    localStorage.setItem('token', response.token)
    localStorage.setItem('user', JSON.stringify(response.user))
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  function checkAuth(): boolean {
    return !!token.value
  }

  return { token, user, isAuthenticated, login, logout, checkAuth }
})
