import { useEffect } from 'react'
import { create } from 'zustand'
import { authService, type AuthUser } from '@/services/authService'

// ── Store ─────────────────────────────────────────────────────────────────────

interface AuthState {
  user: AuthUser | null
  accessToken: string | null
  loading: boolean
  setAuth: (user: AuthUser, accessToken: string) => void
  clearAuth: () => void
  setLoading: (v: boolean) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: null,
  loading: true,
  setAuth: (user, accessToken) => set({ user, accessToken, loading: false }),
  clearAuth: () => set({ user: null, accessToken: null, loading: false }),
  setLoading: (loading) => set({ loading }),
}))

// Synchronous getter used by axios interceptor (outside React)
export function getAuthToken(): string | null {
  return useAuthStore.getState().accessToken
}

// ── Hook ──────────────────────────────────────────────────────────────────────

let initialized = false

export function useAuth() {
  const { user, accessToken, loading, setAuth, clearAuth, setLoading } =
    useAuthStore()

  useEffect(() => {
    if (initialized) return
    initialized = true

    // On mount: attempt a silent token refresh using the httpOnly cookie.
    // If the cookie is present and valid, we get a new access token and load
    // the user profile. If not, we stay logged-out.
    authService
      .refresh()
      .then(({ access_token }) => authService.me(access_token).then((u) => setAuth(u, access_token)))
      .catch(() => clearAuth())
  }, [setAuth, clearAuth])

  const signOut = async () => {
    await authService.logout().catch(() => {})
    clearAuth()
    initialized = false
  }

  return { user, accessToken, loading, setAuth, clearAuth, signOut }
}
