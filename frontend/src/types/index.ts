export type StatusType = 'UP' | 'UP WITH ISSUES' | 'MAINTENANCE' | 'DOWN'

export type CriticalityLevel = 'Critical' | 'High' | 'Medium' | 'Low'

export type FabArea = 'Lithography' | 'Etching' | 'Deposition' | 'Metrology'

export interface Equipment {
  id: number
  name: string
  description: string
  area: FabArea
  bay: string
  status: StatusType
  criticality: CriticalityLevel
  updated_by: string
  last_comment: string
  created_at: string
  updated_at: string
}

export interface StatusSummary {
  up: number
  issues: number
  maintenance: number
  down: number
}

export interface User {
  id: number
  username: string
  role: string
}

export interface LoginResponse {
  token: string
  user: User
}
