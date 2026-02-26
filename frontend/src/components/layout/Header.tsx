import { Menu, Moon, Sun } from 'lucide-react'
import { useEffect } from 'react'
import { useUIStore } from '@/store/uiStore'

const PROVIDERS: { value: string; label: string; models: { value: string; label: string }[] }[] = [
  {
    value: 'anthropic',
    label: 'Anthropic',
    models: [
      { value: 'claude-3-5-sonnet-20240620', label: 'Claude 3.5 Sonnet' },
      { value: 'claude-3-opus-20240229', label: 'Claude 3 Opus' },
      { value: 'claude-3-haiku-20240307', label: 'Claude 3 Haiku' },
    ],
  },
  {
    value: 'openai',
    label: 'OpenAI',
    models: [
      { value: 'gpt-4o', label: 'GPT-4o' },
      { value: 'gpt-4o-mini', label: 'GPT-4o Mini' },
    ],
  },
  {
    value: 'ollama',
    label: 'Ollama',
    models: [
      { value: 'llama3.1:8b', label: 'Llama 3.1 8B' },
      { value: 'mistral', label: 'Mistral' },
    ],
  },
]

export function Header() {
  const { theme, toggleTheme, toggleSidebar, sidebarOpen, selectedProvider, selectedModel, setProvider, setModel } =
    useUIStore()

  const currentProvider = PROVIDERS.find((p) => p.value === selectedProvider) ?? PROVIDERS[0]

  // Validation: ensure the selected model exists for the current provider
  useEffect(() => {
    const isValid = currentProvider.models.some((m) => m.value === selectedModel)
    if (!isValid) {
      console.log(`Auto-correcting dead model choice: ${selectedModel} -> ${currentProvider.models[0].value}`)
      setModel(currentProvider.models[0].value)
    }
  }, [selectedProvider, selectedModel, currentProvider])

  const handleProviderChange = (value: string) => {
    const p = PROVIDERS.find((p) => p.value === value)
    setProvider(value)
    setModel(p?.models[0].value ?? '')
  }

  return (
    <header className="fixed top-0 right-0 left-0 z-30 flex h-14 items-center gap-3 glass-panel border-b border-white/10 px-4">
      {!sidebarOpen && (
        <button onClick={toggleSidebar} className="p-1.5 rounded-lg hover:bg-white/10 text-white/50 hover:text-white transition-colors">
          <Menu size={18} />
        </button>
      )}
      {sidebarOpen && <div className="w-64 shrink-0" />}

      <div className="flex-1" />

      {/* Model selector */}
      <div className="flex items-center gap-2">
        <select
          value={selectedProvider}
          onChange={(e) => handleProviderChange(e.target.value)}
          className="bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-sm text-white/80 focus:outline-none focus:border-brand-500"
        >
          {PROVIDERS.map((p) => (
            <option key={p.value} value={p.value}>
              {p.label}
            </option>
          ))}
        </select>
        <select
          value={selectedModel}
          onChange={(e) => setModel(e.target.value)}
          className="bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-sm text-white/80 focus:outline-none focus:border-brand-500"
        >
          {currentProvider.models.map((m) => (
            <option key={m.value} value={m.value}>
              {m.label}
            </option>
          ))}
        </select>
      </div>

      <button
        onClick={toggleTheme}
        className="p-1.5 rounded-lg hover:bg-white/10 text-white/50 hover:text-white transition-colors"
      >
        {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
      </button>
    </header>
  )
}
