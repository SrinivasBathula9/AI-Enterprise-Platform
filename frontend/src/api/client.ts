import axios, { type InternalAxiosRequestConfig } from 'axios'
import { getAuthToken, useAuthStore } from '@/hooks/useAuth'
import { authService } from '@/services/authService'

export const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true, // send httpOnly refresh cookie on same-origin requests
})

// ── Request: inject access token ──────────────────────────────────────────────
apiClient.interceptors.request.use((config) => {
  const token = getAuthToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── Response: silent token refresh on 401 ────────────────────────────────────
let refreshing: Promise<string> | null = null

apiClient.interceptors.response.use(
  (r) => r,
  async (error) => {
    const original: InternalAxiosRequestConfig & { _retry?: boolean } =
      error.config

    // Only attempt refresh once per request, and not on auth endpoints themselves
    if (
      error.response?.status === 401 &&
      !original._retry &&
      original.url &&
      !original.url.includes('/auth/')
    ) {
      original._retry = true

      try {
        // Deduplicate: if a refresh is already in-flight, await the same promise
        if (!refreshing) {
          refreshing = authService
            .refresh()
            .then(({ access_token }) =>
              authService.me(access_token).then((user) => {
                useAuthStore.getState().setAuth(user, access_token)
                return access_token
              }),
            )
            .finally(() => {
              refreshing = null
            })
        }

        const newToken = await refreshing
        original.headers.Authorization = `Bearer ${newToken}`
        return apiClient(original)
      } catch {
        // Refresh failed — clear auth and let the UI handle the redirect
        useAuthStore.getState().clearAuth()
        return Promise.reject(error)
      }
    }

    return Promise.reject(error)
  },
)
