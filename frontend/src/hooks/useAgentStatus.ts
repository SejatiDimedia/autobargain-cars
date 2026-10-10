import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getAgentStatus, triggerAgentRun } from '../api/client'
import { OPPORTUNITIES_QUERY_KEY } from './useOpportunities'

export function useAgentStatus() {
  return useQuery({
    queryKey: ['agent-status'],
    queryFn: getAgentStatus,
    // Polling setiap 2 detik jika agent running, atau 10 detik jika idle
    refetchInterval: (query) => {
      const isRunning = query.state.data?.is_running
      return isRunning ? 2000 : 10000
    },
  })
}

export function useRunAgent() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: triggerAgentRun,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent-status'] })
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: OPPORTUNITIES_QUERY_KEY })
      queryClient.invalidateQueries({ queryKey: ['stats'] })
    },
  })
}
