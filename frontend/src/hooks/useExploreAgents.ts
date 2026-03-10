import { useQuery } from '@tanstack/react-query'
import { exploreAgentsApi } from '@/api/exploreAgentsApi'

export function useExploreAgents() {
    const { data: agents, isLoading, error } = useQuery({
        queryKey: ['explore-agents'],
        queryFn: exploreAgentsApi.list,
        staleTime: 1000 * 60 * 5, // 5 minutes
    })

    return { agents, isLoading, error }
}
