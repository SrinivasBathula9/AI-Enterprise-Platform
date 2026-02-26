import { useEffect } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useAuth } from '@/hooks/useAuth'
import { useUIStore } from '@/store/uiStore'
import { Sidebar } from '@/components/layout/Sidebar'
import { Header } from '@/components/layout/Header'
import { ChatPage } from '@/pages/Chat'
import { DiscoverPage } from '@/pages/Discover'
import { SettingsPage } from '@/pages/Settings'
import { AuthPage } from '@/pages/Auth'
import { Spinner } from '@/components/ui/Spinner'

const queryClient = new QueryClient()

function AppLayout() {
  const { user, loading } = useAuth()
  const { sidebarOpen, theme } = useUIStore()

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
  }, [theme])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-950">
        <Spinner size="lg" />
      </div>
    )
  }

  if (!user) {
    return <AuthPage />
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(ellipse_at_top_left,_var(--tw-gradient-stops))] from-brand-950/50 via-gray-950 to-black">
      <Header />
      <Sidebar />
      <main
        className={`pt-14 min-h-screen transition-all duration-300 ${sidebarOpen ? 'pl-64' : 'pl-0'}`}
      >
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/discover" element={<DiscoverPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppLayout />
      </BrowserRouter>
    </QueryClientProvider>
  )
}
