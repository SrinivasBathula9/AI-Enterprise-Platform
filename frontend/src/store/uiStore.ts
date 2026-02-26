import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface UIStore {
  theme: 'dark' | 'light'
  sidebarOpen: boolean
  selectedProvider: string
  selectedModel: string
  toggleTheme: () => void
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void
  setProvider: (provider: string) => void
  setModel: (model: string) => void
}

export const useUIStore = create<UIStore>()(
  persist(
    (set, get) => ({
      theme: 'dark',
      sidebarOpen: true,
      selectedProvider: 'openai',
      selectedModel: 'gpt-4o-mini',

      toggleTheme: () => {
        const next = get().theme === 'dark' ? 'light' : 'dark'
        document.documentElement.classList.toggle('dark', next === 'dark')
        set({ theme: next })
      },
      toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      setProvider: (provider) => set({ selectedProvider: provider }),
      setModel: (model) => set({ selectedModel: model }),
    }),
    { name: 'aep-ui-v2' }
  )
)
