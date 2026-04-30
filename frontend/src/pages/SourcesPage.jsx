import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import TopNavBar from '../components/TopNavBar'
import SideNavBar from '../components/SideNavBar'
import MobileNav from '../components/MobileNav'
import { apiFetch } from '../api/apiClient'

function SourcesPage() {
  const { t } = useTranslation()
  const [sources, setSources] = useState([])
  const [newUrl, setNewUrl] = useState('')
  const [loading, setLoading] = useState(true)
  const [validating, setValidating] = useState(false)
  const [submitError, setSubmitError] = useState(null)

  // Category modal state (shown when feed has no detectable category)
  const [showCategoryModal, setShowCategoryModal] = useState(false)
  const [pendingUrl, setPendingUrl] = useState(null)
  const [categories, setCategories] = useState([])
  const [selectedCategoryId, setSelectedCategoryId] = useState('')
  const [modalError, setModalError] = useState(null)

  useEffect(() => {
    fetchSources()
    apiFetch('/api/v1/categories')
      .then((r) => r.json())
      .then(setCategories)
      .catch(() => {})
  }, [])

  const fetchSources = async () => {
    try {
      setLoading(true)
      const response = await apiFetch('/api/v1/information-sources')
      if (!response.ok) throw new Error('API no disponible')
      const data = await response.json()
      const allChannels = await Promise.all(
        data.map(async (src) => {
          const chRes = await apiFetch(`/api/v1/information-sources/${src.id}/rss-channels`)
          if (!chRes.ok) return []
          const channels = await chRes.json()
          return channels.map((ch) => ({
            id: ch.id,
            sourceId: src.id,
            name: src.name,
            url: ch.url,
          }))
        }),
      )
      setSources(allChannels.flat())
    } catch (err) {
      console.warn('Error cargando fuentes:', err.message)
      setSources([])
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (sourceId, channelId) => {
    try {
      await apiFetch(`/api/v1/information-sources/${sourceId}/rss-channels/${channelId}`, {
        method: 'DELETE',
      })
    } catch (err) {
      console.warn('Error eliminando canal:', err.message)
    }
    setSources((prev) => prev.filter((s) => !(s.sourceId === sourceId && s.id === channelId)))
  }

  const extractDomainName = (url) => {
    try {
      const domain = new URL(url).hostname.replace('www.', '')
      const name = domain.split('.')[0]
      return name.charAt(0).toUpperCase() + name.slice(1)
    } catch {
      return t('sources.defaultSourceName')
    }
  }

  const createSourceAndChannel = async (url, categoryId) => {
    const srcRes = await apiFetch('/api/v1/information-sources', {
      method: 'POST',
      body: JSON.stringify({ name: extractDomainName(url), url }),
    })
    if (!srcRes.ok) {
      const err = await srcRes.json().catch(() => ({}))
      throw new Error(err.detail || 'Error creando fuente')
    }
    const src = await srcRes.json()

    const chRes = await apiFetch(`/api/v1/information-sources/${src.id}/rss-channels`, {
      method: 'POST',
      body: JSON.stringify({ url, category_id: categoryId }),
    })
    if (!chRes.ok) {
      const err = await chRes.json().catch(() => ({}))
      throw new Error(err.detail || 'Error creando canal RSS')
    }

    setNewUrl('')
    setShowCategoryModal(false)
    setPendingUrl(null)
    setSelectedCategoryId('')
    setModalError(null)
    fetchSources()
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!newUrl.trim()) return
    setSubmitError(null)
    setValidating(true)

    try {
      const res = await apiFetch('/api/v1/rss/preview', {
        method: 'POST',
        body: JSON.stringify({ url: newUrl }),
      })
      const data = await res.json()

      if (data.status === 'parse_error') {
        setSubmitError(data.error || 'No se pudo analizar el feed RSS')
      } else if (data.status === 'ok') {
        const match = categories.find((c) => c.name === data.detected_categories[0])
        if (!match) {
          setPendingUrl(newUrl)
          setShowCategoryModal(true)
        } else {
          await createSourceAndChannel(newUrl, match.id)
        }
      } else {
        setPendingUrl(newUrl)
        setShowCategoryModal(true)
      }
    } catch (err) {
      setSubmitError(err.message || 'Error al verificar la URL')
    } finally {
      setValidating(false)
    }
  }

  const handleModalConfirm = async () => {
    if (!selectedCategoryId) return
    setModalError(null)
    try {
      await createSourceAndChannel(pendingUrl, Number(selectedCategoryId))
    } catch (err) {
      setModalError(err.message || 'Error al añadir la fuente')
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
                {t('sources.pageTitle')}
              </h1>
            </div>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-8 space-y-6">
              <section className="bg-surface-container-low rounded-xl p-6">
                <h3 className="text-xl font-bold mb-6">{t('sources.activeSources')}</h3>
                {loading ? (
                  <div className="flex items-center justify-center py-8">
                    <span className="material-symbols-outlined animate-spin text-slate-400">
                      progress_activity
                    </span>
                    <span className="ml-2 text-slate-500">{t('sources.loading')}</span>
                  </div>
                ) : sources.length === 0 ? (
                  <div className="text-center py-8 text-slate-500">
                    <span className="material-symbols-outlined text-4xl mb-2">rss_feed</span>
                    <p>{t('sources.empty')}</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {sources.map((source) => (
                      <div
                        key={`${source.sourceId}-${source.id}`}
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
                          onClick={() => handleDelete(source.sourceId, source.id)}
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
                <h3 className="text-2xl font-extrabold mb-4">{t('sources.addTitle')}</h3>
                <form className="space-y-6" onSubmit={handleSubmit}>
                  <div>
                    <label className="block text-[10px] uppercase font-bold mb-2">{t('sources.urlLabel')}</label>
                    <input
                      className="w-full bg-slate-800/50 border-0 rounded-lg py-3 px-4 text-sm text-white placeholder-slate-400"
                      placeholder={t('sources.urlPlaceholder')}
                      type="url"
                      value={newUrl}
                      onChange={(e) => {
                        setNewUrl(e.target.value)
                        setSubmitError(null)
                      }}
                      required
                    />
                    {submitError && (
                      <p className="text-red-300 text-xs mt-2">{submitError}</p>
                    )}
                  </div>
                  <button
                    type="submit"
                    disabled={validating}
                    className="w-full bg-white text-primary-container font-black py-4 rounded-lg hover:bg-slate-100 transition-colors disabled:opacity-50"
                  >
                    {validating ? '...' : t('sources.connectButton')}
                  </button>
                </form>
              </section>
            </div>
          </div>
        </div>
      </main>
      <MobileNav />

      {/* Category selection modal */}
      {showCategoryModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full p-8">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-slate-800">Seleccionar categoría</h2>
              <button
                onClick={() => {
                  setShowCategoryModal(false)
                  setPendingUrl(null)
                  setSelectedCategoryId('')
                  setModalError(null)
                }}
                className="material-symbols-outlined text-slate-400 hover:text-slate-600"
              >
                close
              </button>
            </div>
            <p className="text-slate-500 mb-6">
              No se detectó categoría automáticamente para este feed. Selecciona una para
              clasificar sus artículos.
            </p>
            <select
              value={selectedCategoryId}
              onChange={(e) => setSelectedCategoryId(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 mb-2 text-slate-800"
            >
              <option value="">-- Elige una categoría --</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
            {modalError && <p className="text-red-500 text-sm mb-4">{modalError}</p>}
            <button
              disabled={!selectedCategoryId}
              onClick={handleModalConfirm}
              className="w-full mt-4 bg-primary-container text-white font-bold py-3 rounded-lg hover:opacity-90 transition-opacity disabled:opacity-40"
            >
              Añadir fuente
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default SourcesPage
