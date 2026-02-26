import { apiClient } from './client'

export interface Assistant {
  id: string
  workspace_id: string
  name: string
  description: string
  system_prompt: string
  graph_type: string
  icon: string
  is_default: boolean
  created_at: string
}

export interface CreateAssistantPayload {
  name: string
  description?: string
  system_prompt?: string
  graph_type?: string
  icon?: string
}

export const assistantsApi = {
  list: () => apiClient.get<Assistant[]>('/assistants').then((r) => r.data),
  create: (payload: CreateAssistantPayload) =>
    apiClient.post<Assistant>('/assistants', payload).then((r) => r.data),
  delete: (id: string) => apiClient.delete(`/assistants/${id}`),
}
