import { useEffect, useState, useRef } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { LogEntry } from '../types/api'
import { OPPORTUNITIES_QUERY_KEY } from './useOpportunities'

export function useAgentLogs(maxEntries: number = 200) {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [isConnected, setIsConnected] = useState<boolean>(false)
  const queryClient = useQueryClient()
  const eventSourceRef = useRef<EventSource | null>(null)

  useEffect(() => {
    const es = new EventSource('/api/v1/agent/logs/stream')
    eventSourceRef.current = es

    es.onopen = () => {
      setIsConnected(true)
    }

    es.addEventListener('log', (event) => {
      try {
        const entry: LogEntry = JSON.parse(event.data)
        setLogs((prev) => {
          const next = [...prev, entry]
          return next.slice(-maxEntries)
        })

        // Jika log mengindikasikan siklus selesai, otomatis invalidate data peluang & statistik
        if (entry.message.includes('selesai') || entry.message.includes('Siklus')) {
          queryClient.invalidateQueries({ queryKey: OPPORTUNITIES_QUERY_KEY })
          queryClient.invalidateQueries({ queryKey: ['stats'] })
          queryClient.invalidateQueries({ queryKey: ['agent-status'] })
        }
      } catch (err) {
        console.error('Failed to parse SSE log message:', err)
      }
    })

    es.onerror = () => {
      setIsConnected(false)
    }

    return () => {
      es.close()
      setIsConnected(false)
    }
  }, [maxEntries, queryClient])

  const clearLogs = () => setLogs([])

  return { logs, isConnected, clearLogs }
}
