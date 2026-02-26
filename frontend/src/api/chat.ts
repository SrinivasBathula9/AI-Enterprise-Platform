import { apiClient } from './client'

export interface Session {
  id: string
  workspace_id: string
  user_id: string
  assistant_id: string | null
  title: string
  provider: string
  model: string
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  id: string
  session_id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  tokens: number | null
  created_at: string
}

export interface CreateSessionPayload {
  title?: string
  assistant_id?: string
  provider?: string
  model?: string
}

export const chatApi = {
  listSessions: () => apiClient.get<Session[]>('/sessions').then((r) => r.data),

  createSession: (payload: CreateSessionPayload = {}) =>
    apiClient.post<Session>('/sessions', payload).then((r) => r.data),

  deleteSession: (id: string) => apiClient.delete(`/sessions/${id}`),

  getMessages: (sessionId: string, limit = 50, offset = 0) =>
    apiClient
      .get<{ messages: ChatMessage[]; total: number }>(
        `/sessions/${sessionId}/messages`,
        { params: { limit, offset } }
      )
      .then((r) => r.data),
}

export function createChatStream(
  sessionId: string,
  content: string,
  token: string,
  provider: string | undefined,
  model: string | undefined,
  onToken: (chunk: string) => void,
  onToolEvent: (event: { type: string; tool?: string }) => void,
  onDone: () => void,
  onError: (msg: string) => void
): () => void {
  // Use fetch + ReadableStream for SSE with POST body
  let cancelled = false
  const controller = new AbortController()

  fetch(`/api/v1/sessions/${sessionId}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ content, provider, model }),
    signal: controller.signal,
  })
    .then(async (response) => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const reader = response.body!.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (!cancelled) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event = JSON.parse(line.slice(6))
              if (event.type === 'token') onToken(event.content)
              else if (event.type === 'tool_start' || event.type === 'tool_end') onToolEvent(event)
              else if (event.type === 'done') onDone()
              else if (event.type === 'error') onError(event.content)
            } catch {
              // skip malformed event
            }
          }
        }
      }
    })
    .catch((err) => {
      if (!cancelled) onError(err.message)
    })

  return () => {
    cancelled = true
    controller.abort()
  }
}
