import { motion } from 'framer-motion'
import { Bot, Wrench } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface Props {
  content: string
  toolActivity: string | null
}

function TypingDots() {
  return (
    <div className="flex items-center gap-1 py-1">
      {[0, 1, 2].map((i) => (
        <motion.span
          key={i}
          className="w-1.5 h-1.5 rounded-full bg-brand-400"
          animate={{ scale: [0, 1, 0], opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 1.4, repeat: Infinity, delay: i * 0.2 }}
        />
      ))}
    </div>
  )
}

export function StreamingMessage({ content, toolActivity }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex gap-3"
    >
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-white/10 text-white/70">
        <Bot size={15} />
      </div>

      <div className="max-w-[80%] rounded-2xl rounded-tl-sm glass-message px-4 py-3 text-sm text-white/90 leading-relaxed">
        {toolActivity && (
          <div className="flex items-center gap-2 text-xs text-brand-400 mb-2 animate-pulse">
            <Wrench size={12} />
            {toolActivity}
          </div>
        )}
        {content ? (
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
        ) : (
          <TypingDots />
        )}
        <motion.span
          className="inline-block w-0.5 h-4 bg-brand-400 ml-0.5 align-middle"
          animate={{ opacity: [1, 0] }}
          transition={{ duration: 0.6, repeat: Infinity }}
        />
      </div>
    </motion.div>
  )
}
