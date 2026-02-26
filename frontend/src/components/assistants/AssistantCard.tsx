import { motion } from 'framer-motion'
import { Bot, Code, FileText, PenLine, ArrowRight } from 'lucide-react'
import type { Assistant } from '@/api/assistants'

const ICONS: Record<string, React.ReactNode> = {
  bot: <Bot size={24} />,
  code: <Code size={24} />,
  'file-text': <FileText size={24} />,
  'pen-line': <PenLine size={24} />,
}

const COLORS: Record<string, string> = {
  chat: 'from-brand-600/30 to-brand-800/20',
  rag: 'from-emerald-600/30 to-emerald-800/20',
  code_reviewer: 'from-violet-600/30 to-violet-800/20',
  copywriter: 'from-amber-600/30 to-amber-800/20',
}

interface Props {
  assistant: Assistant
  onSelect: (assistant: Assistant) => void
}

export function AssistantCard({ assistant, onSelect }: Props) {
  const icon = ICONS[assistant.icon] ?? <Bot size={20} />

  return (
    <motion.button
      whileHover={{ y: -4, scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={() => onSelect(assistant)}
      className="group relative flex items-start gap-4 w-full text-left p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-brand-500/50 hover:bg-white/[0.07] transition-all shadow-xl shadow-black/20"
    >
      <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-brand-400 group-hover:scale-110 transition-transform">
        {icon}
      </div>

      <div className="flex-1 min-w-0 pr-4">
        <h3 className="font-semibold text-white text-base mb-1 tracking-tight group-hover:text-brand-300 transition-colors">
          {assistant.name}
        </h3>
        <p className="text-xs text-white/40 leading-relaxed line-clamp-2 font-medium">
          {assistant.description}
        </p>
      </div>

      <div className="absolute bottom-6 right-6 opacity-0 group-hover:opacity-100 transform translate-x-2 group-hover:translate-x-0 transition-all">
        <ArrowRight size={16} className="text-brand-400" />
      </div>

      {assistant.is_default && (
        <span className="absolute top-4 right-4 text-[9px] font-bold px-2 py-0.5 rounded-full bg-brand-500/20 text-brand-400 border border-brand-500/30 uppercase tracking-tighter">
          Agency Top
        </span>
      )}
    </motion.button>
  )
}
