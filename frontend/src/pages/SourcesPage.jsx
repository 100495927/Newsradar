import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import TopNavBar from '../components/TopNavBar'
import SideNavBar from '../components/SideNavBar'
import MobileNav from '../components/MobileNav'
import { apiFetch, getCategories } from '../api/apiClient'

function SourcesPage() {
  const { t } = useTranslation()
  const [groupedSources, setGroupedSources] = useState([])
  const [categories, setCategories] = useState([])
  const [expandedSources, setExpandedSources] = useState(new Set())
  const [newUrl, setNewUrl] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitError, setSubmitError] = useState(null)

  const [showCategoryModal, setShowCategoryModal] = useState(false)
  const [pendingUrl, setPendingUrl] = useState(null)
  const [selectedCategoryId, setSelectedCategoryId] = useState('')
  const [selectedSourceId, setSelectedSourceId] = useState('')
  const [newSourceName, setNewSourceName] = useState('')
  const [modalError, setModalError] = useState(null)

  useEffect(() => {
    fetchCategories()
    fetchSources()
  }, [])

  const fetchCategories = async () => {
    try {
      setCategories(await getCategories())
    } catch (err) {
      console.warn('Error cargando categorias:', err.message)
      setCategories([])
    }
  }

  const categoryLabel = (category) => t(`categories.${category.code}`, category.name)

  const fetchSources = async () => {
    try {
      setLoading(true)
      const response = await apiFetch('/api/v1/information-sources')
      if (!response.ok) throw new Error('API no disponible')
      const data = await response.json()

      const withChannels = await Promise.all(
        data.map(async (src) => {
          const chRes = await apiFetch(`/api/v1/information-sources/${src.id}/rss-channels`)
          const channels = chRes.ok ? await chRes.json() : []
          return { id: src.id, name: src.name, url: src.url, channels }
        }),
      )
      setGroupedSources(withChannels)
    } catch (err) {
      console.warn('Error cargando fuentes:', err.message)
      setGroupedSources([])
    } finally {
      setLoading(false)
    }
  }

  const toggleExpand = (sourceId) => {
    setExpandedSources((prev) => {
      const next = new Set(prev)
      next.has(sourceId) ? next.delete(sourceId) : next.add(sourceId)
      return next
    })
  }

  const handleDeleteSource = async (sourceId) => {
    try {
      await apiFetch(`/api/v1/information-sources/${sourceId}`, { method: 'DELETE' })
    } catch (err) {
      console.warn('Error eliminando fuente:', err.message)
    }
    setGroupedSources((prev) => prev.filter((s) => s.id !== sourceId))
    setExpandedSources((prev) => { const next = new Set(prev); next.delete(sourceId); return next })
  }

  const handleDeleteChannel = async (sourceId, channelId) => {
    try {
      await apiFetch(`/api/v1/information-sources/${sourceId}/rss-channels/${channelId}`, {
        method: 'DELETE',
      })
    } catch (err) {
      console.warn('Error eliminando canal:', err.message)
    }
    setGroupedSources((prev) =>
      prev.map((s) =>
        s.id === sourceId
          ? { ...s, channels: s.channels.filter((ch) => ch.id !== channelId) }
          : s,
      ),
    )
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

  const createSourceAndChannel = async (url, categoryId, sourceId, sourceName) => {
    let finalSourceId = sourceId

    if (sourceId === 'new') {
      const srcRes = await apiFetch('/api/v1/information-sources', {
        method: 'POST',
        body: JSON.stringify({ name: sourceName, url: new URL(url).origin }),
      })
      if (!srcRes.ok) {
        const err = await srcRes.json().catch(() => ({}))
        throw new Error(err.detail || 'Error creando fuente')
      }
      const src = await srcRes.json()
      finalSourceId = src.id
    }

    const chRes = await apiFetch(`/api/v1/information-sources/${finalSourceId}/rss-channels`, {
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
    setSelectedSourceId('')
    setNewSourceName('')
    setModalError(null)
    fetchSources()
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!newUrl.trim()) return
    setSubmitError(null)
    setPendingUrl(newUrl)
    setNewSourceName(extractDomainName(newUrl))
    setShowCategoryModal(true)
  }

  const handleModalConfirm = async () => {
    if (!selectedCategoryId || !selectedSourceId) return
    if (selectedSourceId === 'new' && !newSourceName.trim()) return
    setModalError(null)
    try {
      await createSourceAndChannel(
        pendingUrl,
        Number(selectedCategoryId),
        selectedSourceId,
        newSourceName.trim(),
      )
    } catch (err) {
      setModalError(err.message || 'Error al añadir la fuente')
    }
  }

  const closeModal = () => {
    setShowCategoryModal(false)
    setPendingUrl(null)
    setSelectedCategoryId('')
    setSelectedSourceId('')
    setNewSourceName('')
    setModalError(null)
  }

  const isConfirmDisabled =
    !selectedCategoryId ||
    !selectedSourceId ||
    categories.length === 0 ||
    (selectedSourceId === 'new' && !newSourceName.trim())

  const totalChannels = groupedSources.reduce((acc, s) => acc + s.channels.length, 0)

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
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-bold">{t('sources.activeSources')}</h3>
                  {!loading && totalChannels > 0 && (
                    <span className="text-sm text-slate-500">
                      {groupedSources.length} {t('sources.sourcesCount')} · {totalChannels} {t('sources.channelsCount')}
                    </span>
                  )}
                </div>

                {loading ? (
                  <div className="flex items-center justify-center py-8">
                    <span className="material-symbols-outlined animate-spin text-slate-400">
                      progress_activity
                    </span>
                    <span className="ml-2 text-slate-500">{t('sources.loading')}</span>
                  </div>
                ) : groupedSources.length === 0 ? (
                  <div className="text-center py-8 text-slate-500">
                    <span className="material-symbols-outlined text-4xl mb-2">rss_feed</span>
                    <p>{t('sources.empty')}</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {groupedSources.map((source) => {
                      const isOpen = expandedSources.has(source.id)
                      return (
                        <div key={source.id} className="bg-white rounded-lg shadow-sm overflow-hidden border border-transparent hover:border-outline-variant transition-all">
                          {/* Source header row */}
                          <div className="flex items-center justify-between px-4 py-3">
                            <button
                              onClick={() => toggleExpand(source.id)}
                              className="flex items-center gap-3 flex-1 min-w-0 text-left"
                            >
                              <span className="material-symbols-outlined text-slate-400 text-base">
                                {isOpen ? 'expand_less' : 'expand_more'}
                              </span>
                              <span className="material-symbols-outlined text-primary-container">
                                public
                              </span>
                              <span className="font-bold truncate">{source.name}</span>
                              <span className="ml-1 text-xs font-semibold bg-primary-container text-white rounded-full px-2 py-0.5 shrink-0">
                                {source.channels.length}
                              </span>
                            </button>
                            <button
                              onClick={() => handleDeleteSource(source.id)}
                              className="material-symbols-outlined text-slate-400 hover:text-red-500 transition-colors ml-3 shrink-0"
                            >
                              delete
                            </button>
                          </div>

                          {/* Channel list */}
                          {isOpen && (
                            <div className="border-t border-slate-100 divide-y divide-slate-50">
                              {source.channels.length === 0 ? (
                                <p className="text-xs text-slate-400 px-12 py-3">{t('sources.noChannels')}</p>
                              ) : (
                                source.channels.map((ch) => (
                                  <div
                                    key={ch.id}
                                    className="flex items-center justify-between px-12 py-2 bg-slate-50/60 hover:bg-slate-100/60 transition-colors"
                                  >
                                    <div className="flex items-center gap-2 min-w-0">
                                      <span className="material-symbols-outlined text-slate-300 text-sm">rss_feed</span>
                                      <span className="text-xs text-slate-500 truncate">{ch.url}</span>
                                    </div>
                                    <button
                                      onClick={() => handleDeleteChannel(source.id, ch.id)}
                                      className="material-symbols-outlined text-slate-300 hover:text-red-500 transition-colors text-sm ml-3 shrink-0"
                                    >
                                      delete
                                    </button>
                                  </div>
                                ))
                              )}
                            </div>
                          )}
                        </div>
                      )
                    })}
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
                    className="w-full bg-white text-primary-container font-black py-4 rounded-lg hover:bg-slate-100 transition-colors"
                  >
                    {t('sources.connectButton')}
                  </button>
                </form>
              </section>
            </div>
          </div>
        </div>
      </main>
      <MobileNav />

      {showCategoryModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full p-8">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-slate-800">{t('sources.categoryModalTitle')}</h2>
              <button
                onClick={closeModal}
                className="material-symbols-outlined text-slate-400 hover:text-slate-600"
              >
                close
              </button>
            </div>
            <p className="text-slate-500 mb-6">{t('sources.categoryModalDesc')}</p>

            <div className="space-y-4">
              <div>
                <label className="block text-xs uppercase font-bold text-slate-500 mb-1">
                  {t('sources.sourceLabel')}
                </label>
                <select
                  value={selectedSourceId}
                  onChange={(e) => setSelectedSourceId(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-slate-800"
                >
                  <option value="">{t('sources.sourcePlaceholder')}</option>
                  {groupedSources.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name}
                    </option>
                  ))}
                  <option value="new">{t('sources.newSource')}</option>
                </select>
              </div>

              {selectedSourceId === 'new' && (
                <div>
                  <label className="block text-xs uppercase font-bold text-slate-500 mb-1">
                    {t('sources.sourceNameLabel')}
                  </label>
                  <input
                    type="text"
                    value={newSourceName}
                    onChange={(e) => setNewSourceName(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-slate-800"
                    placeholder={t('sources.sourceNamePlaceholder')}
                  />
                </div>
              )}

              <div>
                <label className="block text-xs uppercase font-bold text-slate-500 mb-1">
                  {t('sources.categoryLabel')}
                </label>
                <select
                  value={selectedCategoryId}
                  onChange={(e) => setSelectedCategoryId(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-slate-800"
                >
                  <option value="">{t('sources.categoryPlaceholder')}</option>
                  {categories.length === 0 && (
                    <option value="" disabled>
                      Categorias no disponibles
                    </option>
                  )}
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>
                      {categoryLabel(c)}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {modalError && <p className="text-red-500 text-sm mt-4">{modalError}</p>}

            <button
              disabled={isConfirmDisabled}
              onClick={handleModalConfirm}
              className="w-full mt-6 bg-primary-container text-white font-bold py-3 rounded-lg hover:opacity-90 transition-opacity disabled:opacity-40"
            >
              {t('sources.addButton')}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default SourcesPage
