import axios from 'axios'
import { getAuthToken } from '@/lib/supabase'

export const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

apiClient.interceptors.request.use(async (config) => {
  const token = await getAuthToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (r) => r,
  (error) => {
    // We let the UI (useAuth/App.tsx) handle unauthorized states
    // to avoid infinite redirect loops on mount.
    return Promise.reject(error)
  }
)
