import { ChevronLeft, ChevronRight } from 'lucide-react'

export function Pagination() {
    return (
        <div className="flex items-center justify-between w-full py-6 mt-8">
            <div className="flex items-center gap-1">
                <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors pointer-events-none opacity-50">
                    <ChevronLeft size={16} />
                </button>
                <button className="w-8 h-8 rounded-lg bg-[#5d3fd3] text-white text-sm font-semibold flex items-center justify-center shadow-sm shadow-[#5d3fd3]/30">
                    1
                </button>
                <button className="w-8 h-8 rounded-lg text-gray-600 text-sm font-medium hover:bg-gray-100 flex items-center justify-center transition-colors">
                    2
                </button>
                <button className="w-8 h-8 rounded-lg text-gray-600 text-sm font-medium hover:bg-gray-100 flex items-center justify-center transition-colors">
                    3
                </button>
                <button className="w-8 h-8 rounded-lg text-gray-600 text-sm font-medium hover:bg-gray-100 flex items-center justify-center transition-colors">
                    4
                </button>
                <button className="w-8 h-8 rounded-lg text-gray-600 text-sm font-medium hover:bg-gray-100 flex items-center justify-center transition-colors">
                    5
                </button>
                <span className="w-8 h-8 text-gray-400 text-sm font-medium flex items-center justify-center">
                    ...
                </span>
                <button className="w-8 h-8 rounded-lg text-gray-600 text-sm font-medium hover:bg-gray-100 flex items-center justify-center transition-colors">
                    334
                </button>
                <button className="p-2 text-gray-600 hover:text-gray-900 transition-colors">
                    <ChevronRight size={16} />
                </button>
            </div>

            <div className="flex items-center gap-4">
                <span className="text-sm text-[#5d3fd3] font-medium">1 of 334 selected</span>
                <div className="flex items-center gap-2">
                    <button className="px-4 py-1.5 text-sm font-medium text-gray-400 pointer-events-none opacity-50 bg-white border border-gray-200 rounded-lg">
                        Previous
                    </button>
                    <button className="px-5 py-1.5 text-sm font-semibold text-gray-900 bg-white border border-gray-200 shadow-sm rounded-lg hover:bg-gray-50 transition-colors">
                        Next
                    </button>
                </div>
            </div>
        </div>
    )
}
