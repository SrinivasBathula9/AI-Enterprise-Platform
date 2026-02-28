import { motion } from 'framer-motion'
import { Bot, Code, FileText, PenLine, CheckCircle2, GripHorizontal } from 'lucide-react'
import type { Assistant } from '@/api/assistants'

const ICONS: Record<string, React.ReactNode> = {
    bot: <Bot size={28} strokeWidth={1.5} />,
    code: <Code size={28} strokeWidth={1.5} />,
    'file-text': <FileText size={28} strokeWidth={1.5} />,
    'pen-line': <PenLine size={28} strokeWidth={1.5} />,
}

interface Props {
    assistant: Assistant
    onSelect: (assistant: Assistant) => void
}

export function AssistantListCard({ assistant, onSelect }: Props) {
    const icon = ICONS[assistant.icon] ?? <Bot size={28} strokeWidth={1.5} />

    // Mocking interactions and rating to match screenshot
    const interactions = assistant.is_default ? '59.5K' : '37.3K'
    const rating = 4.5

    return (
        <motion.div
            whileHover={{ y: -2 }}
            className="group bg-white rounded-2xl border border-gray-100 p-6 flex items-center justify-between shadow-sm hover:shadow-md transition-all w-full cursor-pointer"
            onClick={() => onSelect(assistant)}
        >
            <div className="flex items-center gap-6">
                {/* Icon Container with subtle background framing */}
                <div className="w-16 h-16 rounded-2xl bg-[#E6DECF] border border-[#d6ccb5] flex items-center justify-center text-gray-800 flex-shrink-0 relative overflow-hidden">
                    {/* Decorative lines matching screenshot */}
                    <div className="absolute inset-x-0 top-1/2 h-px bg-black/10 -translate-y-1/2"></div>
                    <div className="absolute inset-y-0 left-1/2 w-px bg-black/10 -translate-x-1/2"></div>
                    <div className="relative z-10 bg-[#E6DECF] p-2 rounded-lg">
                        {icon}
                    </div>
                </div>

                {/* Info Content */}
                <div>
                    <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-gray-900 text-[17px] tracking-tight hover:text-blue-600 transition-colors">
                            {assistant.name}
                        </h3>
                        {/* Verified Badges */}
                        <CheckCircle2 size={14} className="text-emerald-500 fill-emerald-50" />
                        <CheckCircle2 size={14} className="text-blue-500 fill-blue-50" />
                    </div>

                    <p className="text-[13px] text-gray-500 font-medium mb-2">
                        {assistant.name.toLowerCase().replace(/\s+/g, '-')}
                    </p>

                    <div className="flex items-center gap-2">
                        <span className="text-[11px] font-bold px-2 py-0.5 rounded border border-emerald-200 text-emerald-600 tracking-wide uppercase">
                            Active
                        </span>
                        <span className="text-[11px] font-semibold px-2 py-0.5 rounded border border-gray-200 text-gray-500 tracking-wide uppercase">
                            Hosted
                        </span>
                        <GripHorizontal size={14} className="text-gray-300 ml-1" />
                    </div>
                </div>
            </div>

            {/* Right Stats Container */}
            <div className="flex items-center gap-8 pl-8 border-l border-gray-50 mr-4">
                <div className="text-center">
                    <div className="font-bold text-gray-900 text-lg">{interactions}</div>
                    <div className="text-[11px] text-gray-400 font-medium uppercase tracking-wider">Interactions</div>
                </div>
                <div className="text-center">
                    <div className="font-bold text-gray-900 text-lg">{rating}</div>
                    <div className="text-[11px] text-gray-400 font-medium uppercase tracking-wider">Rating</div>
                </div>
            </div>
        </motion.div>
    )
}
