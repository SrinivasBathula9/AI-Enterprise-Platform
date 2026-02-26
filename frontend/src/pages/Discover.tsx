import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { assistantsApi, type Assistant } from '@/api/assistants'
import { AssistantCard } from '@/components/assistants/AssistantCard'
import { useChat } from '@/hooks/useChat'
import { Spinner } from '@/components/ui/Spinner'
import { Plus, Search } from 'lucide-react'
import { Button } from '@/components/ui/Button'

export function DiscoverPage() {
  const [search, setSearch] = useState('')
  const [activeTab, setActiveTab] = useState('PUBLIC')
  const navigate = useNavigate()
  const { newSession } = useChat()

  const { data: assistants = [], isLoading } = useQuery({
    queryKey: ['assistants'],
    queryFn: assistantsApi.list,
  })

  // Mocking categories for the reference-matched UI
  const trending = assistants.slice(0, 3)
  const agencyTop = assistants.slice(3, 6)

  const filtered = assistants.filter(
    (a) =>
      a.name.toLowerCase().includes(search.toLowerCase()) ||
      a.description.toLowerCase().includes(search.toLowerCase())
  )

  const handleSelect = async (assistant: Assistant) => {
    await newSession(assistant.id)
    navigate('/')
  }

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-12">
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        {/* Header Section */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-semibold text-white tracking-tight mb-2">
              Deploy Intelligent Agents to scale your business
            </h1>
          </div>
          <Button variant="primary" className="gap-2 rounded-xl px-6 py-5">
            <Plus size={18} /> Deploy new agent
          </Button>
        </div>

        {/* Search & Suggestions */}
        <div className="max-w-4xl mx-auto mb-12">
          <div className="relative group">
            <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-white/20 group-focus-within:text-brand-400 transition-colors" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by assistant's title or description or creator's email"
              className="w-full bg-white/5 border border-white/10 rounded-2xl pl-11 pr-4 py-4 text-sm text-white placeholder-white/20 focus:outline-none focus:border-brand-500/50 focus:ring-4 focus:ring-brand-500/10 transition-all"
            />
          </div>
          <div className="mt-3 flex items-center gap-2 text-xs">
            <span className="text-white/30">Try:</span>
            {['Policy guidelines', 'Data analysis', 'Tech support', 'Staff training', 'Report writing', 'HR'].map((tag) => (
              <button
                key={tag}
                onClick={() => setSearch(tag)}
                className="text-white/40 hover:text-brand-400 underline decoration-white/10 underline-offset-2 transition-colors"
              >
                {tag},
              </button>
            ))}
          </div>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-24">
            <Spinner size="lg" />
          </div>
        ) : search ? (
          /* Search Results */
          <div className="space-y-6">
            <h2 className="text-lg font-medium text-white/80">Search Results</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filtered.map((assistant) => (
                <AssistantCard key={assistant.id} assistant={assistant} onSelect={handleSelect} />
              ))}
            </div>
            {filtered.length === 0 && (
              <p className="text-center text-sm text-white/30 py-12">
                No assistants found matching "{search}"
              </p>
            )}
          </div>
        ) : (
          /* Landing Dashboard View */
          <div className="space-y-16">
            {/* Ecosystem Section */}
            <section className="space-y-6">
              <div className="flex items-center justify-between border-b border-white/5 pb-2">
                <h2 className="text-xl font-medium text-white/90">Global Ecosystem Highlights</h2>
                <button className="text-xs text-brand-400 hover:text-brand-300 font-medium transition-colors">Expand all</button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {trending.map((assistant) => (
                  <AssistantCard key={assistant.id} assistant={assistant} onSelect={handleSelect} />
                ))}
              </div>
            </section>

            {/* Enterprise Standards Section */}
            <section className="space-y-6">
              <div className="flex items-center justify-between border-b border-white/5 pb-2">
                <h2 className="text-xl font-medium text-white/90">Enterprise Standard Agents</h2>
                <button className="text-xs text-brand-400 hover:text-brand-300 font-medium transition-colors">Expand all</button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {agencyTop.map((assistant) => (
                  <AssistantCard key={assistant.id} assistant={assistant} onSelect={handleSelect} />
                ))}
              </div>
            </section>

            {/* Tabs Header */}
            <div className="flex items-center gap-8 border-b border-white/5 pb-0">
              {['RECENT', 'MY AGENTS', 'SHARED', 'GLOBAL'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`text-xs font-bold py-3 transition-all relative ${activeTab === tab
                    ? 'text-brand-400'
                    : 'text-white/30 hover:text-white/50'
                    }`}
                >
                  {tab}
                  {activeTab === tab && (
                    <motion.div layoutId="tab-underline" className="absolute bottom-0 left-0 right-0 h-0.5 bg-brand-500 rounded-full" />
                  )}
                </button>
              ))}
            </div>
          </div>
        )}
      </motion.div>
    </div>
  )
}
