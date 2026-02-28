import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { assistantsApi, type Assistant } from '@/api/assistants'
import { AssistantListCard } from '@/components/assistants/AssistantListCard'
import { Pagination } from '@/components/ui/Pagination'
import { useChat } from '@/hooks/useChat'
import { Spinner } from '@/components/ui/Spinner'
import { Search, ChevronDown, List, MapPin } from 'lucide-react'
import { Button } from '@/components/ui/Button'

export function DiscoverPage() {
  const [search, setSearch] = useState('')
  const navigate = useNavigate()
  const { newSession } = useChat()

  const { data: assistants = [], isLoading } = useQuery({
    queryKey: ['assistants'],
    queryFn: assistantsApi.list,
  })

  // Duplicate data to force scroll/pagination testing
  const allAssistants = [...assistants, ...assistants, ...assistants].map((a, i) => ({ ...a, id: a.id + i }))
  const filtered = allAssistants.filter(
    (a) =>
      a.name.toLowerCase().includes(search.toLowerCase()) ||
      a.description.toLowerCase().includes(search.toLowerCase())
  )

  const handleSelect = async (assistant: Assistant) => {
    // Navigate to chat
    await newSession(assistant.id)
    navigate('/')
  }

  return (
    // Override global dark theme for this page to match Light Theme screenshot
    <div className="min-h-screen bg-[#f8f9fa] text-gray-900 absolute inset-0 pt-20 px-4 md:px-8 z-50 overflow-y-auto">
      <div className="max-w-6xl mx-auto pb-12">
        {/* Top Metrics Cards */}
        <div className="grid grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 flex flex-col justify-center">
            <h2 className="text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-br from-gray-900 to-gray-700 tracking-tight">2.78M</h2>
            <p className="text-gray-500 font-medium mt-1 uppercase tracking-wide text-sm">Total Agents</p>
          </div>
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 flex flex-col justify-center">
            <h2 className="text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-br from-gray-900 to-gray-700 tracking-tight">162M</h2>
            <p className="text-gray-500 font-medium mt-1 uppercase tracking-wide text-sm">Messages Exchanged</p>
          </div>
        </div>

        {/* Promo Banner */}
        <div className="bg-[#f0ebfa] border border-[#e2d5f3] rounded-2xl p-6 flex items-center justify-between mb-12 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 border-[3.5px] border-black rounded-lg relative overflow-hidden flex items-center justify-center">
              <div className="w-2 h-2 bg-black rounded-full absolute top-1 left-1"></div>
              <div className="w-2 h-2 bg-black rounded-full absolute bottom-1 right-1"></div>
            </div>
            <h2 className="text-2xl font-semibold tracking-tight">Enterprise Platform</h2>
          </div>
          <Button className="bg-[#5d3fd3] hover:bg-[#4a32a8] text-white rounded-xl shadow-md py-2.5 px-6 font-semibold flex items-center gap-2">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            Chat with Agents
          </Button>
        </div>

        {/* Header & Search */}
        <div className="text-center mb-10 max-w-4xl mx-auto space-y-8">
          <h1 className="text-[32px] font-bold text-gray-900 tracking-tight">Agent Marketplace</h1>

          <div className="relative group">
            <Search size={20} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-[#5d3fd3] transition-colors" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search in marketplace..."
              className="w-full bg-white border border-gray-200 shadow-sm rounded-xl pl-12 pr-4 py-4 text-[15px] text-gray-900 placeholder-gray-400 focus:outline-none focus:border-[#5d3fd3]/50 focus:ring-4 focus:ring-[#5d3fd3]/10 transition-all"
            />
          </div>

          {/* Filters Row */}
          <div className="flex items-center justify-center gap-4">
            <label className="flex items-center gap-2 cursor-pointer text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">
              <input type="checkbox" className="w-4 h-4 rounded border-gray-300 text-[#5d3fd3] focus:ring-[#5d3fd3] accent-[#5d3fd3]" />
              Verified
            </label>

            <button className="flex items-center gap-12 bg-white border border-gray-200 rounded-lg px-4 py-2 shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
              Relevance <ChevronDown size={16} className="text-gray-400" />
            </button>

            <div className="flex bg-gray-100 rounded-lg p-1 border border-gray-200 shadow-inner">
              <button className="p-1.5 bg-white shadow-sm rounded-md text-gray-800">
                <List size={18} />
              </button>
              <button className="p-1.5 rounded-md text-gray-400 hover:text-gray-600 transition-colors">
                <MapPin size={18} />
              </button>
            </div>
          </div>
        </div>

        {/* List Content */}
        {isLoading ? (
          <div className="flex justify-center py-24">
            <Spinner size="lg" />
          </div>
        ) : (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
            {filtered.map((assistant) => (
              <AssistantListCard key={assistant.id} assistant={assistant} onSelect={handleSelect} />
            ))}

            {filtered.length === 0 && (
              <p className="text-center text-gray-500 py-12">No agents found matching "{search}"</p>
            )}

            {filtered.length > 0 && <Pagination />}
          </motion.div>
        )}
      </div>
    </div>
  )
}

