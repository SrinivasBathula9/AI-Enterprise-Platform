import { create } from 'zustand'
import type { ChatMessage, Session } from '@/api/chat'

interface StreamingMessage {
  content: string
  isStreaming: boolean
  toolActivity: string | null
}

interface ChatStore {
  sessions: Session[]
  activeSessionId: string | null
  messages: ChatMessage[]
  streaming: StreamingMessage | null
  isLoadingMessages: boolean

  setSessions: (sessions: Session[]) => void
  addSession: (session: Session) => void
  removeSession: (id: string) => void
  updateSessionTitle: (id: string, title: string) => void
  setActiveSession: (id: string | null) => void
  setMessages: (messages: ChatMessage[]) => void
  addMessage: (message: ChatMessage) => void
  startStreaming: () => void
  appendToken: (token: string) => void
  setToolActivity: (activity: string | null) => void
  stopStreaming: (finalContent: string) => void
  setLoadingMessages: (loading: boolean) => void
  reset: () => void
}

export const useChatStore = create<ChatStore>((set, get) => ({
  sessions: [],
  activeSessionId: null,
  messages: [],
  streaming: null,
  isLoadingMessages: false,

  setSessions: (sessions) => set({ sessions }),
  addSession: (session) => set((s) => ({ sessions: [session, ...s.sessions] })),
  removeSession: (id) =>
    set((s) => ({
      sessions: s.sessions.filter((s) => s.id !== id),
      activeSessionId: s.activeSessionId === id ? null : s.activeSessionId,
    })),
  updateSessionTitle: (id, title) =>
    set((s) => ({
      sessions: s.sessions.map((sess) => (sess.id === id ? { ...sess, title } : sess)),
    })),
  setActiveSession: (id) => set({ activeSessionId: id, messages: [], streaming: null }),
  setMessages: (messages) => set({ messages }),
  addMessage: (message) => set((s) => ({ messages: [...s.messages, message] })),
  startStreaming: () => set({ streaming: { content: '', isStreaming: true, toolActivity: null } }),
  appendToken: (token) =>
    set((s) => ({
      streaming: s.streaming
        ? { ...s.streaming, content: s.streaming.content + token }
        : { content: token, isStreaming: true, toolActivity: null },
    })),
  setToolActivity: (activity) =>
    set((s) => ({ streaming: s.streaming ? { ...s.streaming, toolActivity: activity } : null })),
  stopStreaming: (finalContent) =>
    set((s) => {
      const assistantMsg: ChatMessage = {
        id: crypto.randomUUID(),
        session_id: s.activeSessionId ?? '',
        role: 'assistant',
        content: finalContent,
        tokens: null,
        created_at: new Date().toISOString(),
      }
      return { streaming: null, messages: [...s.messages, assistantMsg] }
    }),
  setLoadingMessages: (loading) => set({ isLoadingMessages: loading }),
  reset: () => set({ sessions: [], activeSessionId: null, messages: [], streaming: null }),
}))
