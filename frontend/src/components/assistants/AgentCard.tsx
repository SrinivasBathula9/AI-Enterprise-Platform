import { motion } from 'framer-motion'
import {
    Bot,
    Code,
    FileText,
    PenLine,
    Truck,
    BarChart2,
    Mail,
    Headphones,
    LayoutDashboard,
    ArrowRight,
    CheckCircle2
} from 'lucide-react'
import type { ExploreAgent } from '@/api/exploreAgentsApi'

const ICONS: Record<string, React.ReactNode> = {
    bot: <Bot size={24} />,
    code: <Code size={24} />,
    'file-text': <FileText size={24} />,
    'pen-line': <PenLine size={24} />,
    truck: <Truck size={24} />,
    'bar-chart-2': <BarChart2 size={24} />,
    mail: <Mail size={24} />,
    headphones: <Headphones size={24} />,
    'layout-dashboard': <LayoutDashboard size={24} />,
}

interface Props {
    agent: ExploreAgent
    onLaunch: (agent: ExploreAgent) => void
}

export function AgentCard({ agent, onLaunch }: Props) {
    const icon = ICONS[agent.icon] ?? <Bot size={24} />

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ y: -6, scale: 1.02 }}
            className="group relative flex flex-col w-full text-left p-6 rounded-3xl bg-white border border-gray-100 hover:border-brand-200 hover:shadow-2xl hover:shadow-brand-500/10 transition-all duration-300 overflow-hidden dark:bg-gray-900/50 dark:border-gray-800 dark:hover:border-brand-500/50"
        >
            {/* Background Glow */}
            <div className="absolute inset-0 bg-gradient-to-br from-brand-500/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

            {/* Header */}
            <div className="flex justify-between items-start mb-4 relative z-10">
                <div className="flex-shrink-0 w-14 h-14 rounded-2xl bg-gradient-to-br from-brand-50 to-brand-100 dark:from-brand-500/20 dark:to-brand-800/20 border border-brand-100 dark:border-brand-500/30 flex items-center justify-center text-brand-600 dark:text-brand-400 group-hover:scale-110 group-hover:rotate-3 transition-transform duration-300 shadow-sm">
                    {icon}
                </div>
                <div className="flex gap-2">
                    {agent.badge && (
                        <span className="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider rounded-full bg-brand-100 text-brand-700 dark:bg-brand-500/20 dark:text-brand-400">
                            {agent.badge}
                        </span>
                    )}
                    <span className="px-2.5 py-1 text-[10px] font-medium tracking-wide rounded-full bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400">
                        {agent.category_label}
                    </span>
                </div>
            </div>

            {/* Content */}
            <div className="flex-1 relative z-10 mb-6">
                <h3 className="font-bold text-gray-900 dark:text-white text-xl mb-2 tracking-tight group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">
                    {agent.name}
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 leading-relaxed">
                    {agent.description}
                </p>

                {/* Capabilities Snippet */}
                <div className="mt-4 space-y-2">
                    {agent.capabilities.slice(0, 2).map((cap, i) => (
                        <div key={i} className="flex items-start gap-2 text-xs text-gray-600 dark:text-gray-400">
                            <CheckCircle2 size={14} className="text-emerald-500 shrink-0 mt-0.5" />
                            <span className="line-clamp-1">{cap}</span>
                        </div>
                    ))}
                    {agent.capabilities.length > 2 && (
                        <div className="text-xs text-brand-500 font-medium pl-6">
                            + {agent.capabilities.length - 2} more capabilities
                        </div>
                    )}
                </div>
            </div>

            {/* Action Footer */}
            <div className="pt-4 border-t border-gray-100 dark:border-gray-800 relative z-10 mt-auto">
                <button
                    onClick={() => onLaunch(agent)}
                    className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl font-semibold text-sm bg-gray-50 hover:bg-brand-50 text-gray-700 hover:text-brand-700 dark:bg-gray-800 dark:hover:bg-brand-500/20 dark:text-gray-300 dark:hover:text-brand-400 transition-colors group/btn"
                >
                    <span>Launch Agent</span>
                    <ArrowRight size={16} className="transform group-hover/btn:translate-x-1 transition-transform" />
                </button>
            </div>
        </motion.div>
    )
}
