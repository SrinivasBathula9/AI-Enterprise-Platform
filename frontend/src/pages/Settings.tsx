import { motion } from 'framer-motion'
import { useUIStore } from '@/store/uiStore'
import { useAuth } from '@/hooks/useAuth'
import { Button } from '@/components/ui/Button'

export function SettingsPage() {
  const { theme, toggleTheme, selectedProvider, selectedModel } = useUIStore()
  const { user, signOut } = useAuth()

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold text-white mb-6">Settings</h1>

        <div className="space-y-4">
          {/* Account */}
          <section className="glass-panel border border-white/10 rounded-2xl p-5">
            <h2 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-4">Account</h2>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-white">{user?.email}</p>
                <p className="text-xs text-white/40">Local Auth</p>
              </div>
              <Button variant="danger" size="sm" onClick={signOut}>
                Sign Out
              </Button>
            </div>
          </section>

          {/* Appearance */}
          <section className="glass-panel border border-white/10 rounded-2xl p-5">
            <h2 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-4">Appearance</h2>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-white">Theme</p>
                <p className="text-xs text-white/40">Currently: {theme}</p>
              </div>
              <Button variant="ghost" size="sm" onClick={toggleTheme}>
                Toggle {theme === 'dark' ? 'Light' : 'Dark'} Mode
              </Button>
            </div>
          </section>

          {/* Model */}
          <section className="glass-panel border border-white/10 rounded-2xl p-5">
            <h2 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-4">Default AI Model</h2>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <p className="text-xs text-white/40 mb-1">Provider</p>
                <p className="text-sm text-white capitalize">{selectedProvider}</p>
              </div>
              <div>
                <p className="text-xs text-white/40 mb-1">Model</p>
                <p className="text-sm text-white">{selectedModel}</p>
              </div>
            </div>
            <p className="text-xs text-white/30 mt-3">Change the active model in the header.</p>
          </section>

          {/* About */}
          <section className="glass-panel border border-white/10 rounded-2xl p-5">
            <h2 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-2">About</h2>
            <p className="text-sm text-white/60">AI Enterprise Platform v1.0.0</p>
            <p className="text-xs text-white/30 mt-1">
              Powered by LangGraph agents, Qdrant vector search, and multi-provider LLM support.
            </p>
          </section>
        </div>
      </motion.div>
    </div>
  )
}
