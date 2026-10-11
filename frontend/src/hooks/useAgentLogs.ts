import { useEffect, useState, useRef } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { LogEntry } from '../types/api'
import { getRecentLogs } from '../api/client'
import { OPPORTUNITIES_QUERY_KEY } from './useOpportunities'

export function useAgentLogs(maxEntries: number = 300) {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [isConnected, setIsConnected] = useState<boolean>(false)
  const queryClient = useQueryClient()
  const eventSourceRef = useRef<EventSource | null>(null)

  // 1. Ambil riwayat log awal via REST API agar tampilan terminal langsung terisi saat dibuka
  useEffect(() => {
    let isMounted = true
    getRecentLogs(60)
      .then((initialLogs) => {
        if (isMounted && initialLogs && initialLogs.length > 0) {
          setLogs((prev) => {
            if (prev.length === 0) return initialLogs
            return prev
          })
        }
      })
      .catch((err) => {
        console.warn('Gagal memuat riwayat log awal:', err)
      })

    return () => {
      isMounted = false
    }
  }, [])

  // 2. Hubungkan ke SSE stream untuk log real-time
  useEffect(() => {
    const es = new EventSource('/api/v1/agent/logs/stream')
    eventSourceRef.current = es

    es.onopen = () => {
      setIsConnected(true)
    }

    const handleLogMessage = (event: MessageEvent) => {
      try {
        if (!event.data || event.data === 'keep-alive') return
        const entry: LogEntry = JSON.parse(event.data)

        setLogs((prev) => {
          // Cegah duplikasi jika entry dengan timestamp dan pesan yang sama sudah ada di ujung list
          const isDuplicate = prev.some(
            (p) => p.raw === entry.raw && p.timestamp === entry.timestamp
          )
          if (isDuplicate) return prev

          const next = [...prev, entry]
          return next.slice(-maxEntries)
        })

        // Jika log menandakan siklus selesai, otomatis segarkan tabel peluang & statistik dashboard
        if (entry.message.includes('selesai') || entry.message.includes('Siklus')) {
          queryClient.invalidateQueries({ queryKey: OPPORTUNITIES_QUERY_KEY })
          queryClient.invalidateQueries({ queryKey: ['stats'] })
          queryClient.invalidateQueries({ queryKey: ['agent-status'] })
        }
      } catch (err) {
        console.error('Failed to parse SSE log message:', err)
      }
    }

    es.addEventListener('log', handleLogMessage)
    es.onmessage = handleLogMessage

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
