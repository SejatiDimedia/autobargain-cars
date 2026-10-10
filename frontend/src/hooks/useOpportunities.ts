import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getOpportunities, clearOpportunities } from '../api/client'
import { OpportunityFilterParams } from '../types/api'

export const OPPORTUNITIES_QUERY_KEY = ['opportunities']

export function useOpportunities(filters?: OpportunityFilterParams) {
  return useQuery({
    queryKey: [...OPPORTUNITIES_QUERY_KEY, filters],
    queryFn: () => getOpportunities(filters),
    staleTime: 1000 * 30, // 30 detik
  })
}

export function useClearOpportunities() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: clearOpportunities,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: OPPORTUNITIES_QUERY_KEY })
      queryClient.invalidateQueries({ queryKey: ['stats'] })
    },
  })
}
