import { CarOpportunity } from '../types/car'
import { StatsResponse, TsnePlotResponse, AgentStatus, LogEntry, OpportunityFilterParams } from '../types/api'

const API_BASE = '/api/v1'

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(errorData.detail || `Request gagal dengan status ${response.status}`)
  }

  return response.json()
}

// 1. Opportunities API
export async function getOpportunities(params?: OpportunityFilterParams): Promise<CarOpportunity[]> {
  const searchParams = new URLSearchParams()
  if (params?.brand && params.brand !== 'all') searchParams.append('brand', params.brand)
  if (params?.min_discount !== undefined) searchParams.append('min_discount', params.min_discount.toString())
  if (params?.max_price !== undefined) searchParams.append('max_price', params.max_price.toString())
  if (params?.sort_by) searchParams.append('sort_by', params.sort_by)

  const query = searchParams.toString() ? `?${searchParams.toString()}` : ''
  return request<CarOpportunity[]>(`/opportunities${query}`)
}

export async function clearOpportunities(): Promise<{ message: string; deleted_count: number }> {
  return request('/opportunities', { method: 'DELETE' })
}

// 2. Agent Execution & Status API
export async function triggerAgentRun(): Promise<{ status: string; message: string }> {
  return request('/agent/run', { method: 'POST' })
}

export async function getAgentStatus(): Promise<AgentStatus> {
  return request<AgentStatus>('/agent/status')
}

export async function getRecentLogs(limit: number = 50): Promise<LogEntry[]> {
  return request<LogEntry[]>(`/agent/logs?limit=${limit}`)
}

// 3. Stats & 3D t-SNE Plot API
export async function getDashboardStats(): Promise<StatsResponse> {
  return request<StatsResponse>('/stats')
}

export async function getTsnePlot(maxDatapoints: number = 350): Promise<TsnePlotResponse> {
  return request<TsnePlotResponse>(`/stats/tsne-plot?max_datapoints=${maxDatapoints}`)
}

// 4. AI Consultant Chat API
export async function sendChatMessage(
  message: string,
  sessionId: string = 'default'
): Promise<{ response: string; session_id: string; timestamp: string }> {
  return request('/chat', {
    method: 'POST',
    body: JSON.stringify({ message, session_id: sessionId }),
  })
}

export async function getChatHistory(
  sessionId: string = 'default',
  limit: number = 50
): Promise<{ session_id: string; messages: Array<{ id?: number; role: 'user' | 'assistant'; content: string; timestamp: string }>; total: number }> {
  return request(`/chat/history?session_id=${sessionId}&limit=${limit}`)
}

export async function clearChatHistory(
  sessionId: string = 'default'
): Promise<{ status: string; message: string; deleted_count: number }> {
  return request(`/chat/history?session_id=${sessionId}`, {
    method: 'DELETE',
  })
}
