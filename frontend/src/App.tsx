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

import { Home } from '@/pages/Home'
import { UpdatePasswordPage } from '@/pages/UpdatePassword'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  return <>{children}</>
}

function AppLayout() {
  const { loading } = useAuth()
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

  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<AuthPage />} />
      <Route path="/update-password" element={<UpdatePasswordPage />} />

      {/* Protected Dashboard Routes */}
      <Route
        path="*"
        element={
          <ProtectedRoute>
            <div className="min-h-screen bg-white dark:bg-black bg-[radial-gradient(ellipse_at_top_left,_var(--tw-gradient-stops))] from-white via-gray-50 to-gray-100 dark:from-brand-900/30 dark:via-gray-950 dark:to-black bg-dot-grid transition-colors duration-300">
              <Header />
              <Sidebar />
              <main
                className={`pt-14 min-h-screen transition-all duration-300 ${sidebarOpen ? 'pl-64' : 'pl-0'}`}
              >
                <Routes>
                  <Route path="/chat" element={<ChatPage />} />
                  <Route path="/discover" element={<DiscoverPage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                  <Route path="*" element={<Navigate to="/chat" replace />} />
                </Routes>
              </main>
            </div>
          </ProtectedRoute>
        }
      />
    </Routes>
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
