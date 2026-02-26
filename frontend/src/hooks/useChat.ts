import { useCallback, useEffect, useRef } from 'react'
import { chatApi, createChatStream } from '@/api/chat'
import { getAuthToken } from '@/lib/supabase'
import { useChatStore } from '@/store/chatStore'
import { useUIStore } from '@/store/uiStore'

export function useChat() {
  const store = useChatStore()
  const { selectedProvider, selectedModel } = useUIStore()
  const cancelStreamRef = useRef<(() => void) | null>(null)

  useEffect(() => {
    chatApi.listSessions().then(store.setSessions).catch(console.error)
  }, [])

  const selectSession = useCallback(
    async (sessionId: string) => {
      store.setActiveSession(sessionId)
      store.setLoadingMessages(true)
      try {
        const { messages } = await chatApi.getMessages(sessionId)
        store.setMessages(messages)
      } finally {
        store.setLoadingMessages(false)
      }
    },
    []
  )

  const newSession = useCallback(
    async (assistantId?: string) => {
      const session = await chatApi.createSession({
        assistant_id: assistantId,
        provider: selectedProvider,
        model: selectedModel,
      })
      store.addSession(session)
      await selectSession(session.id)
      return session
    },
    [selectedProvider, selectedModel, selectSession]
  )

  const deleteSession = useCallback(async (id: string) => {
    await chatApi.deleteSession(id)
    store.removeSession(id)
  }, [])

  const sendMessage = useCallback(
    async (content: string) => {
      let sessionId = store.activeSessionId
      if (!sessionId) {
        const session = await newSession()
        sessionId = session.id
      }

      // Add optimistic user message
      store.addMessage({
        id: crypto.randomUUID(),
        session_id: sessionId,
        role: 'user',
        content,
        tokens: null,
        created_at: new Date().toISOString(),
      })

      store.startStreaming()

      const token = await getAuthToken()
      if (!token) return

      let accumulated = ''

      cancelStreamRef.current = createChatStream(
        sessionId,
        content,
        token,
        selectedProvider,
        selectedModel,
        (chunk) => {
          accumulated += chunk
          store.appendToken(chunk)
        },
        (event) => {
          if (event.type === 'tool_start') store.setToolActivity(`Using ${event.tool}…`)
          if (event.type === 'tool_end') store.setToolActivity(null)
        },
        () => {
          store.stopStreaming(accumulated)
          store.updateSessionTitle(sessionId!, content.slice(0, 80))
        },
        (err) => {
          console.error('Stream error:', err)
          store.stopStreaming('⚠ Error: ' + err)
        }
      )
    },
    [store.activeSessionId, newSession]
  )

  const cancelStream = useCallback(() => {
    cancelStreamRef.current?.()
    cancelStreamRef.current = null
  }, [])

  return { selectSession, newSession, deleteSession, sendMessage, cancelStream }
}
