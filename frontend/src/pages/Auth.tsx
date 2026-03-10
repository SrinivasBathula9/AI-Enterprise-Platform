import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { Bot, Home } from 'lucide-react'
import { authService } from '@/services/authService'
import { Button } from '@/components/ui/Button'
import { useAuth } from '@/hooks/useAuth'

export function AuthPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [mode, setMode] = useState<'login' | 'register' | 'forgot'>('login')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const navigate = useNavigate()
  const { user, setAuth } = useAuth()

  useEffect(() => {
    if (user && mode === 'login') {
      navigate('/chat', { replace: true })
    }
  }, [user, mode, navigate])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setMessage('')

    try {
      if (mode === 'login') {
        const { access_token } = await authService.login(email, password)
        const userInfo = await authService.me(access_token)
        setAuth(userInfo, access_token)
        // navigation handled by the useEffect above
      } else if (mode === 'register') {
        await authService.register(email, password)
        setMessage('Account created! You can now sign in.')
        setMode('login')
      } else if (mode === 'forgot') {
        await authService.forgotPassword(email)
        setMessage('If that email exists, a reset link has been sent.')
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Authentication failed')
    } finally {
      setLoading(false)
    }
  }

  const getTitle = () => {
    if (mode === 'login') return 'Sign in to your account'
    if (mode === 'register') return 'Create a new account'
    return 'Reset your password'
  }

  const getSubmitLabel = () => {
    if (mode === 'login') return 'Sign In'
    if (mode === 'register') return 'Create Account'
    return 'Send Reset Link'
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-white via-gray-50 to-gray-100 dark:from-brand-900/20 dark:via-gray-950 dark:to-black bg-dot-grid transition-colors duration-300">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md glass-panel border border-black/5 dark:border-white/10 rounded-3xl p-8 glow-purple relative"
      >
        <button
          onClick={() => navigate('/')}
          className="absolute top-6 left-6 text-gray-400 hover:text-gray-900 dark:text-white/40 dark:hover:text-white transition-colors"
        >
          <Home size={20} />
        </button>

        <div className="flex flex-col items-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-brand-500/10 dark:bg-brand-500/20 flex items-center justify-center mb-4 glow-purple">
            <Bot size={28} className="text-brand-600 dark:text-brand-400" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">AI Enterprise Platform</h1>
          <p className="text-sm text-gray-500 dark:text-white/40 mt-1">{getTitle()}</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-700 dark:text-white/60 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-xl px-4 py-3 text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-white/30 focus:outline-none focus:border-brand-500 transition-colors shadow-sm dark:shadow-none"
              placeholder="you@company.com"
            />
          </div>

          {mode !== 'forgot' && (
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="block text-sm text-gray-700 dark:text-white/60">Password</label>
                {mode === 'login' && (
                  <button
                    type="button"
                    onClick={() => {
                      setMode('forgot')
                      setError('')
                      setMessage('')
                    }}
                    className="text-xs text-brand-600 dark:text-brand-400 hover:text-brand-700 dark:hover:text-brand-300 transition-colors"
                  >
                    Forgot Password?
                  </button>
                )}
              </div>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
                className="w-full bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-xl px-4 py-3 text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-white/30 focus:outline-none focus:border-brand-500 transition-colors shadow-sm dark:shadow-none"
                placeholder="••••••••"
              />
            </div>
          )}

          {error && <p className="text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-500/10 rounded-lg px-3 py-2 border border-red-100 dark:border-transparent">{error}</p>}
          {message && <p className="text-sm text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-500/10 rounded-lg px-3 py-2 border border-emerald-100 dark:border-transparent">{message}</p>}

          <Button type="submit" className="w-full" loading={loading}>
            {getSubmitLabel()}
          </Button>
        </form>

        <p className="text-center text-sm text-gray-500 dark:text-white/30 mt-6">
          {mode === 'login' ? "Don't have an account? " : ''}
          {mode === 'register' ? 'Already have an account? ' : ''}
          {mode === 'forgot' ? 'Remember your password? ' : ''}
          <button
            onClick={() => {
              setMode(mode === 'login' ? 'register' : 'login')
              setError('')
              setMessage('')
            }}
            className="text-brand-600 dark:text-brand-400 hover:text-brand-700 dark:hover:text-brand-300 font-medium transition-colors"
          >
            {mode === 'login' ? 'Sign Up' : 'Sign In'}
          </button>
        </p>
      </motion.div>
    </div>
  )
}
