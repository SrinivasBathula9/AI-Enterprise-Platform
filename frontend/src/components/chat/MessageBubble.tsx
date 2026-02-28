import { motion } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { Bot, User } from 'lucide-react'
import type { ChatMessage } from '@/api/chat'

interface Props {
  message: ChatMessage
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === 'user'

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      <div
        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm ${isUser ? 'bg-brand-100 text-brand-700 dark:bg-brand-600/30 dark:text-brand-300' : 'bg-gray-100 text-gray-700 dark:bg-white/10 dark:text-white/70'
          }`}
      >
        {isUser ? <User size={15} /> : <Bot size={15} />}
      </div>

      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${isUser
            ? 'bg-brand-50 text-gray-900 dark:bg-brand-600/25 dark:text-white rounded-tr-sm'
            : 'glass-message text-gray-900 dark:text-white/90 rounded-tl-sm'
          }`}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code({ node, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '')
                const isBlock = match !== null
                return isBlock ? (
                  <SyntaxHighlighter
                    style={oneDark}
                    language={match[1]}
                    PreTag="div"
                    className="rounded-lg !my-3 !text-xs"
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                ) : (
                  <code className="bg-gray-200 dark:bg-white/10 text-gray-900 dark:text-white rounded px-1 py-0.5 text-xs font-mono" {...props}>
                    {children}
                  </code>
                )
              },
              p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
              ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
              ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
              strong: ({ children }) => <strong className="text-gray-900 dark:text-white font-semibold">{children}</strong>,
            }}
          >
            {message.content}
          </ReactMarkdown>
        )}
      </div>
    </motion.div>
  )
}
