import { useState, useEffect } from 'react'
import TopNavBar from '../components/TopNavBar'
import SideNavBar from '../components/SideNavBar'
import MobileNav from '../components/MobileNav'

const mockSources = [
  { id: 1, name: 'TechCrunch Principal', url: 'https://techcrunch.com/feed/' },
  { id: 2, name: 'FT Mercados', url: 'https://ft.com/markets/feed' },
  { id: 3, name: 'Reuters Intel', url: 'https://reuters.com/intel/feed' },
]

function SourcesPage() {
  const [sources, setSources] = useState([])
  const [newUrl, setNewUrl] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSources()
  }, [])

  const fetchSources = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/rss')
      if (!response.ok) throw new Error('API no disponible')
      const data = await response.json()
      setSources(data)
    } catch (err) {
      console.warn('Usando datos de fallback:', err.message)
      setSources(mockSources)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    try {
      await fetch(`/api/rss/${id}`, { method: 'DELETE' })
    } catch (err) {
      console.warn('API no disponible, eliminando localmente')
    }
    setSources(sources.filter((s) => s.id !== id))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!newUrl.trim()) return

    const newSource = {
      id: Date.now(),
      name: extractDomainName(newUrl),
      url: newUrl,
    }

    try {
      const response = await fetch('/api/rss', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSource),
      })
      if (response.ok) {
        const savedSource = await response.json()
        setSources([...sources, savedSource])
      } else {
        throw new Error('API error')
      }
    } catch (err) {
      console.warn('API no disponible, agregando localmente')
      setSources([...sources, newSource])
    }

    setNewUrl('')
  }

  const extractDomainName = (url) => {
    try {
      const domain = new URL(url).hostname.replace('www.', '')
      const name = domain.split('.')[0]
      return name.charAt(0).toUpperCase() + name.slice(1)
    } catch {
      return 'Nueva Fuente'
    }
  }

  return (
    <div className="bg-surface min-h-screen">
      <TopNavBar />
      <SideNavBar />
      <main className="lg:ml-64 pt-20 pb-12 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-10">
            <div>
              <h1 className="text-4xl font-extrabold tracking-tight text-primary-container mb-2">
                Fuentes y RSS
              </h1>
            </div>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-8 space-y-6">
              <section className="bg-surface-container-low rounded-xl p-6">
                <h3 className="text-xl font-bold mb-6">Canales RSS Activos</h3>
                {loading ? (
                  <div className="flex items-center justify-center py-8">
                    <span className="material-symbols-outlined animate-spin text-slate-400">
                      progress_activity
                    </span>
                    <span className="ml-2 text-slate-500">Cargando fuentes...</span>
                  </div>
                ) : sources.length === 0 ? (
                  <div className="text-center py-8 text-slate-500">
                    <span className="material-symbols-outlined text-4xl mb-2">
                      rss_feed
                    </span>
                    <p>No hay fuentes RSS configuradas</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {sources.map((source) => (
                      <div
                        key={source.id}
                        className="p-4 bg-white rounded-lg border border-transparent hover:border-outline-variant flex justify-between items-center shadow-sm transition-all"
                      >
                        <div className="flex items-center gap-4">
                          <span className="material-symbols-outlined text-slate-400">
                            rss_feed
                          </span>
                          <div>
                            <span className="font-bold block">{source.name}</span>
                            <span className="text-xs text-slate-400 truncate max-w-xs block">
                              {source.url}
                            </span>
                          </div>
                        </div>
                        <button
                          onClick={() => handleDelete(source.id)}
                          className="material-symbols-outlined text-slate-400 hover:text-red-500 transition-colors"
                        >
                          delete
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </section>
            </div>
            <div className="lg:col-span-4">
              <section className="bg-primary-container text-white rounded-xl p-8 sticky top-24">
                <h3 className="text-2xl font-extrabold mb-4">Añadir Fuente</h3>
                <form className="space-y-6" onSubmit={handleSubmit}>
                  <div>
                    <label className="block text-[10px] uppercase font-bold mb-2">
                      URL RSS
                    </label>
                    <input
                      className="w-full bg-slate-800/50 border-0 rounded-lg py-3 px-4 text-sm text-white placeholder-slate-400"
                      placeholder="https://dominio.com/feed.xml"
                      type="url"
                      value={newUrl}
                      onChange={(e) => setNewUrl(e.target.value)}
                      required
                    />
                  </div>
                  <button
                    type="submit"
                    className="w-full bg-white text-primary-container font-black py-4 rounded-lg hover:bg-slate-100 transition-colors"
                  >
                    Conectar Stream
                  </button>
                </form>
              </section>
            </div>
          </div>
        </div>
      </main>
      <MobileNav />
    </div>
  )
}

export default SourcesPage
