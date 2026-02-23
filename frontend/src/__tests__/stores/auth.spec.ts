import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAuthStore } from '../../stores/auth.js'

beforeEach(() => {
  setActivePinia(createPinia())
  localStorage.clear()
})

describe('auth store', () => {
  it('starts unauthenticated when no token in localStorage', () => {
    const store = useAuthStore()
    expect(store.isAuthenticated).toBe(false)
    expect(store.token).toBeNull()
    expect(store.user).toBeNull()
  })

  it('restores auth state from localStorage', () => {
    localStorage.setItem('token', 'stored-token')
    localStorage.setItem('user', JSON.stringify({ id: 1, username: 'admin', role: 'admin' }))

    // Need fresh pinia to re-read localStorage
    setActivePinia(createPinia())
    const store = useAuthStore()

    expect(store.isAuthenticated).toBe(true)
    expect(store.token).toBe('stored-token')
    expect(store.user?.username).toBe('admin')
  })

  it('login sets token and user', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        token: 'jwt-token',
        user: { id: 1, username: 'admin', role: 'admin' },
      }),
    })

    const store = useAuthStore()
    await store.login('admin', 'admin123')

    expect(store.isAuthenticated).toBe(true)
    expect(store.token).toBe('jwt-token')
    expect(store.user?.username).toBe('admin')
    expect(localStorage.getItem('token')).toBe('jwt-token')
  })

  it('login throws on invalid credentials', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      json: () => Promise.resolve({ error: 'Invalid credentials' }),
    })

    const store = useAuthStore()
    await expect(store.login('admin', 'wrong')).rejects.toThrow('Invalid credentials')
    expect(store.isAuthenticated).toBe(false)
  })

  it('logout clears state and localStorage', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        token: 'jwt-token',
        user: { id: 1, username: 'admin', role: 'admin' },
      }),
    })

    const store = useAuthStore()
    await store.login('admin', 'admin123')
    expect(store.isAuthenticated).toBe(true)

    store.logout()
    expect(store.isAuthenticated).toBe(false)
    expect(store.token).toBeNull()
    expect(store.user).toBeNull()
    expect(localStorage.getItem('token')).toBeNull()
    expect(localStorage.getItem('user')).toBeNull()
  })

  it('checkAuth returns correct state', () => {
    const store = useAuthStore()
    expect(store.checkAuth()).toBe(false)

    localStorage.setItem('token', 'test')
    setActivePinia(createPinia())
    const store2 = useAuthStore()
    expect(store2.checkAuth()).toBe(true)
  })
})
