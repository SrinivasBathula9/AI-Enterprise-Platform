import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { Bot, ChevronRight, Sun, Moon } from 'lucide-react'
import { useUIStore } from '@/store/uiStore'

export function PublicHeader() {
    const { theme, toggleTheme } = useUIStore()
    return (
        <motion.header
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="fixed top-0 left-0 right-0 h-16 border-b border-black/5 dark:border-white/10 glass-panel z-50 px-6 flex items-center justify-between"
        >
            <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
                <div className="w-8 h-8 rounded-lg bg-brand-500/10 dark:bg-brand-500/20 flex items-center justify-center glow-purple">
                    <Bot size={18} className="text-brand-600 dark:text-brand-400" />
                </div>
                <span className="font-bold text-lg tracking-tight text-gray-900 dark:text-white">AEP</span>
            </Link>

            <div className="flex items-center gap-4 sm:gap-6">
                <a href="#" className="hidden md:block text-sm font-medium text-gray-500 hover:text-gray-900 dark:text-white/50 dark:hover:text-white transition-colors">Documentation</a>
                <a href="#" className="hidden md:block text-sm font-medium text-gray-500 hover:text-gray-900 dark:text-white/50 dark:hover:text-white transition-colors">Agents</a>
                <a href="#" className="hidden md:block text-sm font-medium text-gray-500 hover:text-gray-900 dark:text-white/50 dark:hover:text-white transition-colors">Pricing</a>

                <button
                    onClick={toggleTheme}
                    className="p-2 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors"
                >
                    {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
                </button>

                <Link
                    to="/login"
                    className="flex items-center gap-2 text-sm font-semibold bg-gray-900 hover:bg-gray-800 text-white dark:bg-white/5 dark:hover:bg-white/10 border border-transparent dark:border-white/10 px-4 py-2 rounded-full transition-all"
                >
                    Sign In <ChevronRight size={14} className="opacity-70 dark:text-white/50" />
                </Link>
            </div>
        </motion.header>
    )
}
