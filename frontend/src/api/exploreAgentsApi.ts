import { apiClient } from './client'

export interface AgentCapability {
    label: string
    description: string
}

export interface ExploreAgent {
    id: string
    name: string
    description: string
    graph_type: string
    icon: string
    category: string
    category_label: string
    capabilities: string[]
    status: 'available' | 'coming_soon' | string
    badge: string | null
}

export const exploreAgentsApi = {
    list: () => apiClient.get<ExploreAgent[]>('/explore-agents').then((r) => r.data),
}
