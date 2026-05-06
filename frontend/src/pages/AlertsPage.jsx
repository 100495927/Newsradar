import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import TopNavBar from '../components/TopNavBar'
import SideNavBar from '../components/SideNavBar'
import MobileNav from '../components/MobileNav'
import MultiSelectSearch from '../components/MultiSelectSearch'
import { useAuth } from '../context/AuthContext'
import { apiFetch, getCategories } from '../api/apiClient'

const MAX_ALERTS = 20

function toLocal(a) {
  return {
    id: a.id,
    name: a.name,
    cat: a.categories?.[0]?.code ?? '',
    cron: a.cron_expression,
    enabled: a.enabled ?? true,
    rssChannelIds: (a.rss_channels_ids ?? []).map(String),
    descriptors: a.descriptors ?? [],
  }
}

function AlertsPage() {
  const { t } = useTranslation()
  const { user } = useAuth()
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [rssChannels, setRssChannels] = useState([])
  const [categories, setCategories] = useState([])

  // Create modal
  const [showModal, setShowModal] = useState(false)
  const [newAlert, setNewAlert] = useState({ name: '', cat: '', cron: '*/15 * * * *', rssChannelIds: [] })
  const [error, setError] = useState('')
  const [synonymSuggestions, setSynonymSuggestions] = useState([])
  const [acceptedSynonyms, setAcceptedSynonyms] = useState([])
  const [loadingSynonyms, setLoadingSynonyms] = useState(false)

  // Edit modal
  const [showEditModal, setShowEditModal] = useState(false)
  const [editData, setEditData] = useState({ id: null, name: '', cat: '', cron: '*/15 * * * *', rssChannelIds: [] })
  const [editExtraDescriptors, setEditExtraDescriptors] = useState([])
  const [editSuggestions, setEditSuggestions] = useState([])
  const [editError, setEditError] = useState('')
  const [loadingEditSynonyms, setLoadingEditSynonyms] = useState(false)

  const frequencies = [
    { value: '* * * * *',     label: t('alerts.freq1min',  'Cada minuto') },
    { value: '*/2 * * * *',   label: t('alerts.freq2min',  'Cada 2 minutos') },
    { value: '*/5 * * * *',   label: t('alerts.freq5min',  'Cada 5 minutos') },
    { value: '*/15 * * * *', label: t('alerts.freq15min', 'Cada 15 minutos') },
    { value: '*/30 * * * *', label: t('alerts.freq30min', 'Cada 30 minutos') },
    { value: '0 * * * *',    label: t('alerts.freq1h',    'Cada hora') },
    { value: '0 */12 * * *', label: t('alerts.freq12h',   'Cada 12 horas') },
    { value: '0 0 * * *',    label: t('alerts.freq24h',   'Cada 24 h') },
  ]

  const cronLabel = (cron) => frequencies.find((f) => f.value === cron)?.label ?? cron

  const catLabel = (code) => categories.find((c) => c.value === code)?.label ?? code
  const categoryPayload = (code) => (code ? [{ code, label: catLabel(code) }] : [])

  const limitReached = alerts.length >= MAX_ALERTS

  useEffect(() => {
    if (user?.id) fetchAlerts()
    fetchCategories()
    fetchRssChannels()
  }, [user?.id])

  const fetchCategories = async () => {
    try {
      const apiCategories = await getCategories()
      const normalized = apiCategories.map((category) => ({
        value: category.code,
        label: t(`categories.${category.code}`, category.name),
      }))
      setCategories(normalized)
      if (normalized.length > 0) {
        setNewAlert((prev) => (prev.cat ? prev : { ...prev, cat: normalized[0].value }))
        setEditData((prev) => (prev.cat ? prev : { ...prev, cat: normalized[0].value }))
      }
    } catch (err) {
      console.warn('Error cargando categorias:', err.message)
      setCategories([])
    }
  }

  const fetchRssChannels = async () => {
    try {
      const res = await apiFetch('/api/v1/information-sources')
      if (!res.ok) return
      const sources = await res.json()
      const channelLists = await Promise.all(
        sources.map(async (src) => {
          const r = await apiFetch(`/api/v1/information-sources/${src.id}/rss-channels`)
          if (!r.ok) return []
          const channels = await r.json()
          return channels.map((ch) => ({ id: String(ch.id), label: `${src.name} — ${ch.url}` }))
        }),
      )
      setRssChannels(channelLists.flat())
    } catch {
      // silencioso
    }
  }

  const fetchAlerts = async () => {
    try {
      setLoading(true)
      const res = await apiFetch(`/api/v1/users/${user.id}/alerts`)
      if (!res.ok) throw new Error(t('alerts.errorLoad'))
      const data = await res.json()
      setAlerts(data.map(toLocal))
    } catch (err) {
      console.error(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    setAlerts(alerts.filter((a) => a.id !== id))
    await apiFetch(`/api/v1/users/${user.id}/alerts/${id}`, { method: 'DELETE' })
  }

  const handleToggle = async (id) => {
    const updated = alerts.map((a) => (a.id === id ? { ...a, enabled: !a.enabled } : a))
    setAlerts(updated)
    const alert = updated.find((a) => a.id === id)
    await apiFetch(`/api/v1/users/${user.id}/alerts/${id}`, {
      method: 'PUT',
      body: JSON.stringify({
        name: alert.name,
        cron_expression: alert.cron,
        enabled: alert.enabled,
        descriptors: alert.descriptors.length > 0 ? alert.descriptors : [alert.name],
        categories: categoryPayload(alert.cat),
        rss_channels_ids: alert.rssChannelIds ?? [],
      }),
    })
  }

  // ── Create modal handlers ──────────────────────────────────────────────────

  const handleFetchSynonyms = async () => {
    if (!newAlert.name.trim()) return
    setLoadingSynonyms(true)
    setSynonymSuggestions([])
    setAcceptedSynonyms([])
    try {
      const res = await apiFetch(`/api/v1/synonyms?word=${encodeURIComponent(newAlert.name.trim())}`)
      if (!res.ok) return
      const data = await res.json()
      setSynonymSuggestions(data)
    } catch {
      // silencioso
    } finally {
      setLoadingSynonyms(false)
    }
  }

  const toggleSynonym = (word) => {
    setAcceptedSynonyms((prev) =>
      prev.includes(word) ? prev.filter((w) => w !== word) : [...prev, word],
    )
  }

  const handleCreateAlert = async (e) => {
    e.preventDefault()
    setError('')
    if (!newAlert.name.trim() || !newAlert.cron.trim()) return
    const selectedCategories = categoryPayload(newAlert.cat)
    if (selectedCategories.length === 0) {
      setError('No se ha podido cargar la lista de categorias')
      return
    }
    const payload = {
      name: newAlert.name,
      cron_expression: newAlert.cron,
      descriptors: [newAlert.name, ...acceptedSynonyms],
      categories: selectedCategories,
      rss_channels_ids: newAlert.rssChannelIds,
    }
    try {
      const res = await apiFetch(`/api/v1/users/${user.id}/alerts`, {
        method: 'POST',
        body: JSON.stringify(payload),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || t('alerts.errorCreate'))
      }
      const saved = await res.json()
      setAlerts([...alerts, toLocal(saved)])
      setNewAlert({ name: '', cat: categories[0]?.value ?? '', cron: '*/15 * * * *', rssChannelIds: [] })
      setSynonymSuggestions([])
      setAcceptedSynonyms([])
      setShowModal(false)
    } catch (err) {
      setError(err.message)
    }
  }

  // ── Edit modal handlers ────────────────────────────────────────────────────

  const handleOpenEdit = (alert) => {
    const extra = (alert.descriptors ?? []).filter((d) => d !== alert.name)
    setEditData({ id: alert.id, name: alert.name, cat: alert.cat, cron: alert.cron, rssChannelIds: alert.rssChannelIds })
    setEditExtraDescriptors(extra)
    setEditSuggestions([])
    setEditError('')
    setShowEditModal(true)
  }

  const removeEditDescriptor = (word) => {
    setEditExtraDescriptors((prev) => prev.filter((d) => d !== word))
  }

  const handleFetchEditSynonyms = async () => {
    if (!editData.name.trim()) return
    setLoadingEditSynonyms(true)
    setEditSuggestions([])
    try {
      const res = await apiFetch(`/api/v1/synonyms?word=${encodeURIComponent(editData.name.trim())}`)
      if (!res.ok) return
      const data = await res.json()
      setEditSuggestions(data.filter((w) => !editExtraDescriptors.includes(w) && w !== editData.name))
    } catch {
      // silencioso
    } finally {
      setLoadingEditSynonyms(false)
    }
  }

  const toggleEditSuggestion = (word) => {
    if (editExtraDescriptors.includes(word)) {
      removeEditDescriptor(word)
    } else {
      setEditExtraDescriptors((prev) => [...prev, word])
    }
  }

  const handleSaveEdit = async (e) => {
    e.preventDefault()
    setEditError('')
    const selectedCategories = categoryPayload(editData.cat)
    if (selectedCategories.length === 0) {
      setEditError('No se ha podido cargar la lista de categorias')
      return
    }
    const currentAlert = alerts.find((a) => a.id === editData.id)
    const payload = {
      name: editData.name,
      cron_expression: editData.cron,
      enabled: currentAlert?.enabled ?? true,
      descriptors: [editData.name, ...editExtraDescriptors],
      categories: selectedCategories,
      rss_channels_ids: editData.rssChannelIds,
    }
    try {
      const res = await apiFetch(`/api/v1/users/${user.id}/alerts/${editData.id}`, {
        method: 'PUT',
        body: JSON.stringify(payload),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || t('alerts.errorSave', 'Error al guardar la alerta'))
      }
      const saved = await res.json()
      setAlerts(alerts.map((a) => (a.id === editData.id ? toLocal(saved) : a)))
      setShowEditModal(false)
    } catch (err) {
      setEditError(err.message)
    }
  }

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <div className="bg-background min-h-screen">
      <TopNavBar />
      <SideNavBar />
      <main className="lg:ml-64 pt-24 pb-12 px-6 lg:px-12">
        <div className="max-w-6xl mx-auto">
          <header className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
            <div>
              <h1 className="text-4xl font-extrabold tracking-tighter text-primary-container mb-2">
                {t('alerts.pageTitle')}
              </h1>
              <p className="text-on-primary-container font-medium max-w-lg">
                {t('alerts.pageSubtitle')}
              </p>
            </div>
            <div className="flex flex-col items-end gap-2">
              <button
                onClick={() => !limitReached && setShowModal(true)}
                disabled={limitReached}
                className="bg-primary-container text-on-primary px-6 py-3 rounded-lg font-bold flex items-center gap-2 hover:opacity-90 active:scale-95 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <span className="material-symbols-outlined">add</span>
                {t('alerts.createButton')}
              </button>
              {limitReached && (
                <p className="text-xs text-slate-500">
                  {t('alerts.limitReached', `Límite de ${MAX_ALERTS} alertas alcanzado`)}
                </p>
              )}
            </div>
          </header>

          <div className="bg-surface-container-low rounded-xl overflow-hidden">
            {/* Table header */}
            <div className="grid grid-cols-12 gap-4 px-6 py-4 bg-surface-container-highest/50 border-b border-outline-variant/10">
              <div className="col-span-3 text-xs font-bold uppercase tracking-widest text-on-surface-variant">
                {t('alerts.colName')}
              </div>
              <div className="col-span-3 text-xs font-bold uppercase tracking-widest text-on-surface-variant">
                {t('alerts.colDescriptors', 'Descriptores')}
              </div>
              <div className="col-span-2 text-xs font-bold uppercase tracking-widest text-on-surface-variant">
                {t('alerts.colCategory')}
              </div>
              <div className="col-span-2 text-xs font-bold uppercase tracking-widest text-on-surface-variant">
                {t('alerts.colFrequency')}
              </div>
              <div className="col-span-2 text-xs font-bold uppercase tracking-widest text-on-surface-variant text-right">
                {t('alerts.colActions', 'Acciones')}
              </div>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-12">
                <span className="material-symbols-outlined animate-spin text-slate-400">
                  progress_activity
                </span>
                <span className="ml-2 text-slate-500">{t('alerts.loading')}</span>
              </div>
            ) : alerts.length === 0 ? (
              <div className="text-center py-12 text-slate-500">
                <span className="material-symbols-outlined text-4xl mb-2">notifications_off</span>
                <p>{t('alerts.empty')}</p>
              </div>
            ) : (
              alerts.map((a) => (
                <div
                  key={a.id}
                  className={`grid grid-cols-12 gap-4 px-6 py-5 items-center hover:bg-white border-b border-outline-variant/10 transition-opacity ${
                    !a.enabled ? 'opacity-50' : ''
                  }`}
                >
                  <div className="col-span-3">
                    <div className="font-bold text-primary-container">{a.name}</div>
                  </div>

                  <div className="col-span-3 flex flex-wrap gap-1">
                    {(a.descriptors ?? []).slice(0, 3).map((d) => (
                      <span
                        key={d}
                        className="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-mono truncate max-w-[90px]"
                      >
                        {d}
                      </span>
                    ))}
                    {(a.descriptors ?? []).length > 3 && (
                      <span className="text-[10px] text-slate-400 self-center">
                        +{a.descriptors.length - 3}
                      </span>
                    )}
                  </div>

                  <div className="col-span-2">
                    <span className="text-xs text-slate-600">{catLabel(a.cat)}</span>
                  </div>

                  <div className="col-span-2 text-xs text-slate-600">{cronLabel(a.cron)}</div>

                  <div className="col-span-2 flex justify-end items-center gap-2">
                    <button
                      onClick={() => handleToggle(a.id)}
                      className={`w-11 h-6 rounded-full relative transition-colors flex-shrink-0 ${
                        a.enabled ? 'bg-primary-container' : 'bg-slate-300'
                      }`}
                    >
                      <div
                        className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${
                          a.enabled ? 'right-1' : 'left-1'
                        }`}
                      />
                    </button>
                    <button
                      onClick={() => handleOpenEdit(a)}
                      className="material-symbols-outlined text-slate-400 hover:text-primary-container transition-colors text-[20px]"
                      title={t('alerts.editTitle', 'Editar alerta')}
                    >
                      edit
                    </button>
                    <button
                      onClick={() => handleDelete(a.id)}
                      className="material-symbols-outlined text-slate-400 hover:text-red-500 transition-colors text-[20px]"
                    >
                      delete
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </main>
      <MobileNav />

      {/* ── Create Alert Modal ─────────────────────────────────────────────── */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full p-8 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-slate-900">{t('alerts.modalTitle')}</h3>
              <button
                onClick={() => {
                  setShowModal(false)
                  setSynonymSuggestions([])
                  setAcceptedSynonyms([])
                }}
                className="material-symbols-outlined text-slate-400 hover:text-slate-600"
              >
                close
              </button>
            </div>

            <form onSubmit={handleCreateAlert} className="space-y-6">
              <div className="space-y-2">
                <label className="block text-xs font-bold uppercase text-slate-500">
                  {t('alerts.colName')}
                </label>
                <div className="flex gap-2">
                  <input
                    className="flex-1 bg-slate-50 border border-slate-200 rounded-lg px-4 py-3"
                    placeholder={t('alerts.namePlaceholder')}
                    value={newAlert.name}
                    onChange={(e) => {
                      setNewAlert({ ...newAlert, name: e.target.value })
                      setSynonymSuggestions([])
                      setAcceptedSynonyms([])
                    }}
                    required
                  />
                  <button
                    type="button"
                    onClick={handleFetchSynonyms}
                    disabled={!newAlert.name.trim() || loadingSynonyms}
                    className="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-lg text-xs font-bold transition-colors disabled:opacity-40 whitespace-nowrap flex items-center gap-1"
                  >
                    <span className="material-symbols-outlined text-[16px]">
                      {loadingSynonyms ? 'progress_activity' : 'auto_awesome'}
                    </span>
                    {t('alerts.suggestSynonyms', 'Sinónimos')}
                  </button>
                </div>
                {synonymSuggestions.length > 0 && (
                  <div className="pt-1">
                    <p className="text-[10px] uppercase font-bold text-slate-400 mb-2">
                      {t('alerts.synonymsHint', 'Selecciona los que quieras incluir como descriptores')}
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {synonymSuggestions.map((word) => {
                        const accepted = acceptedSynonyms.includes(word)
                        return (
                          <button
                            key={word}
                            type="button"
                            onClick={() => toggleSynonym(word)}
                            className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
                              accepted
                                ? 'bg-primary-container text-white border-primary-container'
                                : 'bg-white text-slate-600 border-slate-200 hover:border-primary-container'
                            }`}
                          >
                            {accepted && '✓ '}
                            {word}
                          </button>
                        )
                      })}
                    </div>
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <label className="block text-xs font-bold uppercase text-slate-500">
                  {t('alerts.colCategory')}
                </label>
                <select
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3"
                  value={newAlert.cat}
                  onChange={(e) => setNewAlert({ ...newAlert, cat: e.target.value })}
                >
                  {categories.length === 0 && (
                    <option value="" disabled>
                      Categorias no disponibles
                    </option>
                  )}
                  {categories.map((cat) => (
                    <option key={cat.value} value={cat.value}>
                      {cat.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-2">
                <label className="block text-xs font-bold uppercase text-slate-500">
                  {t('alerts.rssChannelsLabel', 'Canales RSS')}
                </label>
                <MultiSelectSearch
                  options={rssChannels}
                  selected={newAlert.rssChannelIds}
                  onChange={(ids) => setNewAlert({ ...newAlert, rssChannelIds: ids })}
                  placeholder={t('alerts.rssChannelsPlaceholder')}
                />
              </div>

              <div className="space-y-2">
                <label className="block text-xs font-bold uppercase text-slate-500">
                  {t('alerts.frequencyLabel', 'Frecuencia')}
                </label>
                <select
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3"
                  value={newAlert.cron}
                  onChange={(e) => setNewAlert({ ...newAlert, cron: e.target.value })}
                  required
                >
                  {frequencies.map((f) => (
                    <option key={f.value} value={f.value}>
                      {f.label}
                    </option>
                  ))}
                </select>
              </div>

              {error && <p className="text-red-500 text-sm">{error}</p>}
              <div className="flex gap-4 justify-end pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-6 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-medium transition-colors"
                >
                  {t('alerts.cancel')}
                </button>
                <button
                  type="submit"
                  className="px-6 py-2.5 bg-primary-container text-white rounded-lg font-medium transition-colors hover:opacity-90"
                >
                  {t('alerts.createSubmit')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Edit Alert Modal ───────────────────────────────────────────────── */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full p-8 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-slate-900">
                {t('alerts.editTitle', 'Editar alerta')}
              </h3>
              <button
                onClick={() => setShowEditModal(false)}
                className="material-symbols-outlined text-slate-400 hover:text-slate-600"
              >
                close
              </button>
            </div>

            <form onSubmit={handleSaveEdit} className="space-y-6">
              <div className="space-y-2">
                <label className="block text-xs font-bold uppercase text-slate-500">
                  {t('alerts.colName')}
                </label>
                <div className="flex gap-2">
                  <input
                    className="flex-1 bg-slate-50 border border-slate-200 rounded-lg px-4 py-3"
                    placeholder={t('alerts.namePlaceholder')}
                    value={editData.name}
                    onChange={(e) => {
                      setEditData({ ...editData, name: e.target.value })
                      setEditSuggestions([])
                    }}
                    required
                  />
                  <button
                    type="button"
                    onClick={handleFetchEditSynonyms}
                    disabled={!editData.name.trim() || loadingEditSynonyms}
                    className="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-lg text-xs font-bold transition-colors disabled:opacity-40 whitespace-nowrap flex items-center gap-1"
                  >
                    <span className="material-symbols-outlined text-[16px]">
                      {loadingEditSynonyms ? 'progress_activity' : 'auto_awesome'}
                    </span>
                    {t('alerts.suggestSynonyms', 'Sinónimos')}
                  </button>
                </div>

                {editExtraDescriptors.length > 0 && (
                  <div className="pt-1">
                    <p className="text-[10px] uppercase font-bold text-slate-400 mb-2">
                      {t('alerts.currentDescriptors', 'Descriptores actuales')}
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {editExtraDescriptors.map((word) => (
                        <span
                          key={word}
                          className="flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-primary-container text-white"
                        >
                          {word}
                          <button
                            type="button"
                            onClick={() => removeEditDescriptor(word)}
                            className="ml-1 text-white/70 hover:text-white leading-none"
                          >
                            ×
                          </button>
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {editSuggestions.length > 0 && (
                  <div className="pt-1">
                    <p className="text-[10px] uppercase font-bold text-slate-400 mb-2">
                      {t('alerts.synonymsHint', 'Selecciona los que quieras incluir')}
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {editSuggestions.map((word) => {
                        const isAdded = editExtraDescriptors.includes(word)
                        return (
                          <button
                            key={word}
                            type="button"
                            onClick={() => toggleEditSuggestion(word)}
                            className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
                              isAdded
                                ? 'bg-primary-container text-white border-primary-container'
                                : 'bg-white text-slate-600 border-slate-200 hover:border-primary-container'
                            }`}
                          >
                            {isAdded && '✓ '}
                            {word}
                          </button>
                        )
                      })}
                    </div>
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <label className="block text-xs font-bold uppercase text-slate-500">
                  {t('alerts.colCategory')}
                </label>
                <select
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3"
                  value={editData.cat}
                  onChange={(e) => setEditData({ ...editData, cat: e.target.value })}
                >
                  {categories.length === 0 && (
                    <option value="" disabled>
                      Categorias no disponibles
                    </option>
                  )}
                  {categories.map((cat) => (
                    <option key={cat.value} value={cat.value}>
                      {cat.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-2">
                <label className="block text-xs font-bold uppercase text-slate-500">
                  {t('alerts.rssChannelsLabel', 'Canales RSS')}
                </label>
                <MultiSelectSearch
                  options={rssChannels}
                  selected={editData.rssChannelIds}
                  onChange={(ids) => setEditData({ ...editData, rssChannelIds: ids })}
                  placeholder={t('alerts.rssChannelsPlaceholder')}
                />
              </div>

              <div className="space-y-2">
                <label className="block text-xs font-bold uppercase text-slate-500">
                  {t('alerts.frequencyLabel', 'Frecuencia')}
                </label>
                <select
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3"
                  value={editData.cron}
                  onChange={(e) => setEditData({ ...editData, cron: e.target.value })}
                  required
                >
                  {frequencies.map((f) => (
                    <option key={f.value} value={f.value}>
                      {f.label}
                    </option>
                  ))}
                </select>
              </div>

              {editError && <p className="text-red-500 text-sm">{editError}</p>}
              <div className="flex gap-4 justify-end pt-4">
                <button
                  type="button"
                  onClick={() => setShowEditModal(false)}
                  className="px-6 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-medium transition-colors"
                >
                  {t('alerts.cancel')}
                </button>
                <button
                  type="submit"
                  className="px-6 py-2.5 bg-primary-container text-white rounded-lg font-medium transition-colors hover:opacity-90"
                >
                  {t('alerts.saveEdit', 'Guardar cambios')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default AlertsPage
