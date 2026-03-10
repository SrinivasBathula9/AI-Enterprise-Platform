import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Search, Sparkles } from 'lucide-react'
import { useExploreAgents } from '@/hooks/useExploreAgents'
import { AgentCard } from '@/components/assistants/AgentCard'
import { Spinner } from '@/components/ui/Spinner'
import type { ExploreAgent } from '@/api/exploreAgentsApi'

const CATEGORIES = [
  { id: 'all', label: 'All Agents' },
  { id: 'logistics', label: 'Logistics' },
  { id: 'finance', label: 'Finance' },
  { id: 'email', label: 'Email Mgt' },
  { id: 'customer', label: 'Customer Exp' },
  { id: 'operations', label: 'Operations' },
  { id: 'general', label: 'General AI' },
]

export function DiscoverPage() {
  const navigate = useNavigate()
  const { agents, isLoading } = useExploreAgents()
  const [activeTab, setActiveTab] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')

  const handleLaunch = (agent: ExploreAgent) => {
    navigate(`/chat?assistant_id=${agent.id}`)
  }

  const filteredAgents = agents?.filter((agent) => {
    const matchesCategory = activeTab === 'all' || agent.category === activeTab
    const matchesSearch = agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.description.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesCategory && matchesSearch
  })

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#0a0a0a] text-gray-900 dark:text-gray-100 absolute inset-0 pt-20 px-4 md:px-8 z-50 overflow-y-auto">
      <div className="max-w-7xl mx-auto pb-24">
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
          <div>
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-100 dark:bg-brand-500/20 text-brand-700 dark:text-brand-400 text-sm font-semibold mb-4 border border-brand-200 dark:border-brand-500/30"
            >
              <Sparkles size={14} />
              <span>AI Automation Hub</span>
            </motion.div>
            <motion.h1
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="text-4xl md:text-5xl font-extrabold text-gray-900 dark:text-white mb-4 tracking-tight"
            >
              Explore <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-600 to-violet-600 dark:from-brand-400 dark:to-violet-400">Agents</span>
            </motion.h1>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
              className="text-gray-500 dark:text-gray-400 text-lg max-w-2xl"
            >
              Discover and deploy intelligent AI systems engineered to automate your e-commerce operations.
            </motion.p>
          </div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="relative relative w-full md:w-80 group mt-4 md:mt-0"
          >
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search size={18} className="text-gray-400 group-focus-within:text-brand-500 transition-colors" />
            </div>
            <input
              type="text"
              placeholder="Search capabilities..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-11 pr-4 py-3 bg-white dark:bg-gray-900/50 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-sm focus:ring-2 focus:ring-brand-500 focus:border-brand-500 text-gray-900 dark:text-white placeholder-gray-400 transition-all"
            />
          </motion.div>
        </div>

        {/* Category Tabs */}
        <div className="flex overflow-x-auto pb-4 mb-8 -mx-4 px-4 md:mx-0 md:px-0 hide-scrollbar gap-2">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setActiveTab(cat.id)}
              className={`whitespace-nowrap px-5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 ${activeTab === cat.id
                ? 'bg-gray-900 text-white shadow-md dark:bg-brand-600 dark:shadow-brand-500/20'
                : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50 dark:bg-gray-900/50 dark:text-gray-400 dark:border-gray-800 dark:hover:bg-gray-800'
                }`}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {/* Loading State */}
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-32">
            <div className="text-brand-500 mb-4 flex justify-center">
              <Spinner size="lg" />
            </div>
            <p className="text-gray-500 dark:text-gray-400 font-medium">Loading operational agents...</p>
          </div>
        ) : (
          /* Grid */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAgents?.map((agent) => (
              <AgentCard
                key={agent.id}
                agent={agent}
                onLaunch={handleLaunch}
              />
            ))}

            {filteredAgents?.length === 0 && (
              <div className="col-span-full py-24 text-center bg-white dark:bg-gray-900/30 rounded-3xl border border-dashed border-gray-300 dark:border-gray-800">
                <Search size={32} className="mx-auto text-gray-400 mb-4 opacity-50" />
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">No agents found</h3>
                <p className="text-gray-500 dark:text-gray-400">Could not find any agents matching your filters.</p>
                <button
                  onClick={() => { setSearchQuery(''); setActiveTab('all'); }}
                  className="mt-6 px-4 py-2 text-sm font-medium text-brand-600 dark:text-brand-400 hover:underline"
                >
                  Clear all filters
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

