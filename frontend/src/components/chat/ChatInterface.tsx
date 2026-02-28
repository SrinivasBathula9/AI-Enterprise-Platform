import { useEffect, useRef } from 'react'
import { useChatStore } from '@/store/chatStore'
import { useChat } from '@/hooks/useChat'
import { MessageBubble } from './MessageBubble'
import { StreamingMessage } from './StreamingMessage'
import { ChatInput } from './ChatInput'
import { Spinner } from '@/components/ui/Spinner'
import { Bot } from 'lucide-react'
import { motion } from 'framer-motion'

export function ChatInterface() {
  const { messages, streaming, isLoadingMessages } = useChatStore()
  const { sendMessage, cancelStream } = useChat()
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streaming?.content])

  const isEmpty = messages.length === 0 && !streaming

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto py-6 px-4 space-y-6">
        {isLoadingMessages && (
          <div className="flex justify-center py-8">
            <Spinner />
          </div>
        )}

        {isEmpty && !isLoadingMessages && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center justify-center h-full gap-4 text-center py-20"
          >
            <div className="w-16 h-16 rounded-2xl bg-brand-100 dark:bg-brand-600/20 flex items-center justify-center">
              <Bot size={32} className="text-brand-600 dark:text-brand-400" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-1">How can I help you?</h2>
              <p className="text-sm text-gray-500 dark:text-white/40">Start a conversation or pick an assistant from Discover.</p>
            </div>
          </motion.div>
        )}

        <div className="max-w-3xl mx-auto space-y-6">
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}

          {streaming && (
            <StreamingMessage
              content={streaming.content}
              toolActivity={streaming.toolActivity}
            />
          )}
          <div ref={bottomRef} />
        </div>
      </div>

      {/* Input */}
      <div className="px-4 py-4">
        <ChatInput onSend={sendMessage} onCancel={cancelStream} />
      </div>
    </div>
  )
}
