import { useRef, useState, type KeyboardEvent } from 'react'
import { ArrowUp, Paperclip, Square } from 'lucide-react'
import { motion } from 'framer-motion'
import { useChatStore } from '@/store/chatStore'

interface Props {
  onSend: (content: string) => void
  onCancel: () => void
  onFileUpload?: (file: File) => void
}

export function ChatInput({ onSend, onCancel, onFileUpload }: Props) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const { streaming } = useChatStore()
  const isStreaming = streaming?.isStreaming ?? false

  const handleSend = () => {
    const trimmed = value.trim()
    if (!trimmed || isStreaming) return
    onSend(trimmed)
    setValue('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleInput = () => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel border border-white/10 rounded-2xl p-3 mx-auto max-w-3xl"
    >
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        onInput={handleInput}
        placeholder="Message AEP…"
        rows={1}
        className="w-full resize-none bg-transparent text-sm text-white placeholder-white/30 focus:outline-none min-h-[36px] max-h-[200px]"
        disabled={isStreaming}
      />
      <div className="flex items-center justify-between mt-2">
        <div className="flex items-center gap-1">
          {onFileUpload && (
            <label className="cursor-pointer p-1.5 rounded-lg text-white/30 hover:text-white hover:bg-white/10 transition-colors">
              <Paperclip size={16} />
              <input
                type="file"
                className="hidden"
                accept=".pdf,.docx,.txt,.md,.csv"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) onFileUpload(file)
                  e.target.value = ''
                }}
              />
            </label>
          )}
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-white/20">⏎ send, ⇧⏎ newline</span>
          {isStreaming ? (
            <button
              onClick={onCancel}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-white/10 text-white/70 hover:bg-white/20 text-sm transition-colors"
            >
              <Square size={13} fill="currentColor" /> Stop
            </button>
          ) : (
            <button
              onClick={handleSend}
              disabled={!value.trim()}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-brand-600 text-white hover:bg-brand-500 disabled:opacity-30 disabled:pointer-events-none text-sm transition-colors"
            >
              <ArrowUp size={15} /> Send
            </button>
          )}
        </div>
      </div>
    </motion.div>
  )
}
