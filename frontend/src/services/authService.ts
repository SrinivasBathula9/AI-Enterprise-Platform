/**
 * Auth service — thin wrappers around the local FastAPI auth endpoints.
 * All state management stays in useAuth.ts (Zustand).
 */

const BASE = '/api/v1/auth'

export interface AuthUser {
  id: string
  email: string
  full_name?: string | null
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    credentials: 'include', // send/receive httpOnly refresh_token cookie
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail ?? `Request failed: ${res.status}`)
  }
  // 204 No Content has no body
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

export const authService = {
  register(email: string, password: string, full_name?: string): Promise<AuthUser> {
    return request<AuthUser>('/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name }),
    })
  },

  login(email: string, password: string): Promise<TokenResponse> {
    return request<TokenResponse>('/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
  },

  /** Exchange the httpOnly refresh cookie for a fresh access token. */
  refresh(): Promise<TokenResponse> {
    return request<TokenResponse>('/refresh', { method: 'POST' })
  },

  /** Revoke the refresh cookie server-side and clear it. */
  logout(): Promise<void> {
    return request<void>('/logout', { method: 'POST' })
  },

  me(accessToken: string): Promise<AuthUser> {
    return request<AuthUser>('/me', {
      headers: { Authorization: `Bearer ${accessToken}` },
    })
  },

  forgotPassword(email: string): Promise<{ message: string }> {
    return request<{ message: string }>('/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    })
  },

  resetPassword(token: string, new_password: string): Promise<{ message: string }> {
    return request<{ message: string }>('/reset-password', {
      method: 'POST',
      body: JSON.stringify({ token, new_password }),
    })
  },
}
