import { useQuery } from '@tanstack/react-query'
import { getDashboardStats, getTsnePlot } from '../api/client'

export function useStats() {
  return useQuery({
    queryKey: ['stats'],
    queryFn: getDashboardStats,
    staleTime: 1000 * 30,
  })
}

export function useTsnePlot(maxDatapoints: number = 300) {
  return useQuery({
    queryKey: ['tsne-plot', maxDatapoints],
    queryFn: () => getTsnePlot(maxDatapoints),
    staleTime: 1000 * 60 * 5, // 5 menit
  })
}
