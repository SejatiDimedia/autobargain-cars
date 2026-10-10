export interface StatsResponse {
  total_opportunities: number
  max_discount_million: number
  avg_discount_million: number
  avg_car_price_million: number
  total_potential_profit_million: number
  vector_db_car_count: number
  is_agent_running: boolean
  last_run: string | null
  total_cycles: number
  last_error: string | null
  brand_distribution: Record<string, number>
  grade_distribution: Record<string, number>
}

export interface TsnePoint {
  x: number
  y: number
  z: number
  brand: string
  description: string
  color: string
}

export interface TsnePlotResponse {
  points: TsnePoint[]
  brands: string[]
  brand_colors: string[]
  total: number
  error?: string
}

export interface AgentStatus {
  is_running: boolean
  total_cycles: number
  last_run: string | null
  last_error: string | null
}

export interface LogEntry {
  timestamp: string
  level: string
  message: string
  raw: string
}

export interface OpportunityFilterParams {
  brand?: string
  min_discount?: number
  max_price?: number
  sort_by?: 'discount_desc' | 'discount_asc' | 'price_asc' | 'price_desc' | 'year_desc'
}
