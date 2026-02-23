import type { LoginResponse, Equipment } from './types/index.js'

const BASE_URL = '/api'

function getToken(): string | null {
  return localStorage.getItem('token')
}

async function fetchWithAuth(url: string, options: RequestInit = {}): Promise<Response> {
  const token = getToken()
  const headers = new Headers(options.headers)
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }
  headers.set('Content-Type', 'application/json')

  const response = await fetch(url, { ...options, headers })

  if (response.status === 401) {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    window.location.href = '/login'
  }

  return response
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const response = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })

  if (!response.ok) {
    const data = await response.json()
    throw new Error(data.error || 'Login failed')
  }

  return response.json()
}

export async function fetchEquipment(filters?: {
  status?: string
  area?: string
  search?: string
}): Promise<Equipment[]> {
  const params = new URLSearchParams()
  if (filters?.status) params.set('status', filters.status)
  if (filters?.area) params.set('area', filters.area)
  if (filters?.search) params.set('search', filters.search)

  const query = params.toString()
  const url = `${BASE_URL}/equipment${query ? '?' + query : ''}`
  const response = await fetchWithAuth(url)

  if (!response.ok) {
    const data = await response.json()
    throw new Error(data.error || 'Failed to fetch equipment')
  }

  return response.json()
}

export async function getEquipment(id: number): Promise<Equipment> {
  const response = await fetchWithAuth(`${BASE_URL}/equipment/${id}`)

  if (!response.ok) {
    const data = await response.json()
    throw new Error(data.error || 'Failed to fetch equipment')
  }

  return response.json()
}

export async function updateEquipment(
  id: number,
  status: string,
  comment: string
): Promise<Equipment> {
  const response = await fetchWithAuth(`${BASE_URL}/equipment/${id}`, {
    method: 'PUT',
    body: JSON.stringify({ status, comment }),
  })

  if (!response.ok) {
    const data = await response.json()
    throw new Error(data.error || 'Failed to update equipment')
  }

  return response.json()
}
