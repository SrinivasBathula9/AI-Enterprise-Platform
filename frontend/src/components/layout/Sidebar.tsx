import { motion, AnimatePresence } from 'framer-motion'
import {
  Bot, LayoutGrid, MessageSquarePlus, PenLine, Settings, Trash2, X,
} from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { useChatStore } from '@/store/chatStore'
import { useUIStore } from '@/store/uiStore'
import { useChat } from '@/hooks/useChat'
import { useAuth } from '@/hooks/useAuth'


export function Sidebar() {
  const { sessions, activeSessionId } = useChatStore()
  const { sidebarOpen, toggleSidebar } = useUIStore()
  const { newSession, selectSession, deleteSession } = useChat()
  const { user, signOut } = useAuth()
  const navigate = useNavigate()

  const handleNewChat = async () => {
    await newSession()
    navigate('/')
  }

  return (
    <AnimatePresence>
      {sidebarOpen && (
        <motion.aside
          key="sidebar"
          initial={{ x: -280, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: -280, opacity: 0 }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className="fixed inset-y-0 left-0 z-40 flex w-64 flex-col glass-panel border-r border-black/5 dark:border-white/10 transition-colors"
        >
          {/* Header */}
          <div className="flex h-14 items-center justify-between px-4 border-b border-black/5 dark:border-white/10 transition-colors">
            <span className="text-sm font-semibold text-gray-900 dark:text-white tracking-wide">AEP</span>
            <button onClick={toggleSidebar} className="p-1 rounded hover:bg-gray-100 dark:hover:bg-white/10 text-gray-500 dark:text-white/50 hover:text-gray-900 dark:hover:text-white transition-colors">
              <X size={16} />
            </button>
          </div>

          {/* New Chat */}
          <div className="p-3">
            <button
              onClick={handleNewChat}
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 text-sm font-medium text-gray-900 dark:text-white hover:bg-gray-50 dark:hover:bg-white/10 hover:border-gray-300 dark:hover:border-white/20 shadow-sm dark:shadow-none transition-all"
            >
              <MessageSquarePlus size={18} className="text-brand-600 dark:text-brand-400" />
              New Chat
            </button>
          </div>
          {/* Main Navigation */}
          <div className="px-3 py-2 space-y-1">
            <Link
              to="/templates"
              className="flex items-center justify-between group px-3 py-2 rounded-lg text-sm text-gray-600 dark:text-white/60 hover:bg-gray-100 dark:hover:bg-white/10 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              <div className="flex items-center gap-2">
                <PenLine size={16} /> <span>Agent workflows</span>
              </div>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-cyan-500/10 dark:bg-cyan-500/20 text-cyan-700 dark:text-cyan-400 border border-cyan-500/20 dark:border-cyan-500/30">NEW</span>
            </Link>
            <Link
              to="/batch"
              className="flex items-center justify-between group px-3 py-2 rounded-lg text-sm text-gray-600 dark:text-white/60 hover:bg-gray-100 dark:hover:bg-white/10 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              <div className="flex items-center gap-2">
                <LayoutGrid size={16} /> <span>Process automation</span>
              </div>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-cyan-500/10 dark:bg-cyan-500/20 text-cyan-700 dark:text-cyan-400 border border-cyan-500/20 dark:border-cyan-500/30">NEW</span>
            </Link>
          </div>

          {/* Agent Ecosystem */}
          <div className="px-2 pt-4">
            <p className="px-3 py-1 text-[10px] font-bold text-gray-400 dark:text-white/30 uppercase tracking-widest">
              Agent Ecosystem
            </p>
            <Link
              to="/discover"
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm mt-1 transition-colors ${window.location.pathname === '/discover'
                ? 'bg-gray-100 text-gray-900 dark:bg-white/10 dark:text-white'
                : 'text-gray-600 dark:text-white/60 hover:bg-gray-100 dark:hover:bg-white/10 hover:text-gray-900 dark:hover:text-white'
                }`}
            >
              <Bot size={16} /> Explore Agents
            </Link>
          </div>

          {/* Chat History */}
          <div className="flex-1 overflow-y-auto px-2 py-1 space-y-0.5 mt-2">
            <p className="px-3 py-1 text-[10px] font-bold text-gray-400 dark:text-white/30 uppercase tracking-widest">
              Recent Chats
            </p>
            {sessions.map((session) => (
              <div key={session.id} className="group flex items-center rounded-lg">
                <button
                  onClick={() => { selectSession(session.id); navigate('/') }}
                  className={`flex-1 truncate px-3 py-2 text-left text-sm rounded-lg transition-colors ${session.id === activeSessionId
                    ? 'bg-brand-50 text-brand-700 dark:bg-brand-600/30 dark:text-white'
                    : 'text-gray-600 dark:text-white/60 hover:bg-gray-100 dark:hover:bg-white/10 hover:text-gray-900 dark:hover:text-white'
                    }`}
                >
                  {session.title}
                </button>
                <button
                  onClick={() => deleteSession(session.id)}
                  className="hidden group-hover:flex p-1 mr-1 rounded text-gray-400 dark:text-white/30 hover:text-red-500 dark:hover:text-red-400"
                >
                  <Trash2 size={13} />
                </button>
              </div>
            ))}
            {sessions.length === 0 && (
              <p className="px-3 py-4 text-xs text-gray-400 dark:text-white/30 text-center">No conversations yet</p>
            )}
          </div>

          {/* Bottom nav */}
          <div className="border-t border-black/5 dark:border-white/10 p-3 space-y-1 transition-colors">
            <Link
              to="/settings"
              className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-600 dark:text-white/60 hover:bg-gray-100 dark:hover:bg-white/10 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              <Settings size={16} /> Settings
            </Link>
            {user && (
              <button
                onClick={signOut}
                className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-600 dark:text-white/40 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
              >
                <span className="w-6 h-6 rounded-full bg-brand-100 dark:bg-brand-600/40 flex items-center justify-center text-xs font-bold text-brand-700 dark:text-white">
                  {user.email?.[0].toUpperCase()}
                </span>
                <span className="truncate flex-1 text-left">{user.email}</span>
              </button>
            )}
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  )
}
