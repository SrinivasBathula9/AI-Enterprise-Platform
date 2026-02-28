import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { ArrowRight, Zap, Shield, Globe } from 'lucide-react'
import { PublicHeader } from '@/components/layout/PublicHeader'

export function Home() {
    return (
        <div className="min-h-screen bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-white via-gray-50 to-gray-100 dark:from-brand-900/30 dark:via-gray-950 dark:to-black bg-dot-grid text-gray-900 dark:text-white overflow-x-hidden selection:bg-brand-500/30 transition-colors duration-300">
            <PublicHeader />

            <main className="pt-32 pb-24 px-6 md:px-12 max-w-7xl mx-auto flex flex-col items-center justify-center min-h-[90vh]">
                {/* Hero Section */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="text-center max-w-4xl mx-auto mb-16"
                >
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/5 dark:bg-brand-500/10 border border-brand-500/20 mb-8 glow-purple">
                        <span className="w-2 h-2 rounded-full bg-brand-500 dark:bg-brand-400 animate-pulse"></span>
                        <span className="text-xs font-semibold text-brand-700 dark:text-brand-300 tracking-wide uppercase">Introducing AEP 2.0</span>
                    </div>

                    <h1 className="text-5xl md:text-7xl font-bold tracking-tighter mb-6 leading-tight">
                        The Enterprise <br />
                        <span className="text-gradient">Multi-Agent Ecosystem</span>
                    </h1>

                    <p className="text-lg md:text-xl text-gray-600 dark:text-white/50 font-medium mb-10 max-w-2xl mx-auto leading-relaxed">
                        A production-ready platform bridging premium cloud models with intelligent local fallbacks. Build, discover, and scale your AI workforce securely.
                    </p>

                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                        <Link
                            to="/login"
                            className="w-full sm:w-auto px-8 py-4 rounded-xl bg-accent-500 text-gray-950 font-bold hover:bg-accent-400 transition-all glow-green flex items-center justify-center gap-2 group"
                        >
                            Get Started
                            <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                        </Link>
                        <Link
                            to="/discover"
                            className="w-full sm:w-auto px-8 py-4 rounded-xl bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 hover:bg-gray-50 dark:hover:bg-white/10 transition-all font-semibold shadow-sm dark:shadow-none"
                        >
                            Explore Agents
                        </Link>
                    </div>
                </motion.div>

                {/* Feature Grid */}
                <motion.div
                    initial={{ opacity: 0, y: 40 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                    className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-6xl mx-auto mt-12"
                >
                    {/* Card 1 */}
                    <div className="glass-panel rounded-3xl p-8 hover:border-brand-500/30 transition-colors group">
                        <div className="w-12 h-12 rounded-xl bg-brand-500/10 flex items-center justify-center text-brand-600 dark:text-brand-400 mb-6 group-hover:scale-110 transition-transform">
                            <Zap size={24} />
                        </div>
                        <h3 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">Cost Optimization Layer</h3>
                        <p className="text-gray-500 dark:text-white/40 leading-relaxed text-sm font-medium">
                            Intelligently routes simple queries to local models (Llama 3.1) saving API credits while maintaining GPT-4 capabilities for complex reasoning.
                        </p>
                    </div>

                    {/* Card 2 */}
                    <div className="glass-panel rounded-3xl p-8 hover:border-brand-500/30 transition-colors group relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-brand-500/10 blur-[50px] rounded-full pointer-events-none"></div>
                        <div className="w-12 h-12 rounded-xl bg-brand-500/10 flex items-center justify-center text-brand-600 dark:text-brand-400 mb-6 group-hover:scale-110 transition-transform">
                            <Globe size={24} />
                        </div>
                        <h3 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">Global Agent Marketplace</h3>
                        <p className="text-gray-500 dark:text-white/40 leading-relaxed text-sm font-medium">
                            Deploy and discover specialized agents from across the ecosystem. Connect internal workflows with verified external AI capabilities.
                        </p>
                    </div>

                    {/* Card 3 */}
                    <div className="glass-panel rounded-3xl p-8 hover:border-brand-500/30 transition-colors group">
                        <div className="w-12 h-12 rounded-xl bg-brand-500/10 flex items-center justify-center text-brand-600 dark:text-brand-400 mb-6 group-hover:scale-110 transition-transform">
                            <Shield size={24} />
                        </div>
                        <h3 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">Enterprise Security</h3>
                        <p className="text-gray-500 dark:text-white/40 leading-relaxed text-sm font-medium">
                            Production-grade JWT validation via Supabase JWKS. Complete data segregation with isolated RAG vectors and execution environments.
                        </p>
                    </div>
                </motion.div>
            </main>
        </div>
    )
}
