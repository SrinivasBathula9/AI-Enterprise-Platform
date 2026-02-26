import { getAuthToken } from '@/lib/supabase'
import { apiClient } from './client'

export interface UploadResponse {
  task_id: string
  filename: string
  status: string
}

export interface TaskStatus {
  task_id: string
  status: 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE'
  result: { chunks?: number; doc_id?: string } | null
}

export const documentsApi = {
  upload: async (file: File, workspaceId: string): Promise<UploadResponse> => {
    const form = new FormData()
    form.append('file', file)
    const response = await apiClient.post<UploadResponse>(
      `/documents/upload?workspace_id=${workspaceId}`,
      form,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )
    return response.data
  },

  getTaskStatus: (taskId: string) =>
    apiClient.get<TaskStatus>(`/documents/tasks/${taskId}`).then((r) => r.data),
}
