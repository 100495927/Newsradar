import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import TopNavBar from '../components/TopNavBar'
import SideNavBar from '../components/SideNavBar'
import MobileNav from '../components/MobileNav'
import MultiSelectSearch from '../components/MultiSelectSearch'
import { useAuth } from '../context/AuthContext'
import { apiFetch, getCategories } from '../api/apiClient'

const MAX_ALERTS = 20

function normalizeCategoryCode(code) {
  const raw = String(code ?? '').trim()
  return /^\d+$/.test(raw) ? raw.padStart(8, '0') : raw
}

function parseDescriptors(value) {
  return String(value ?? '')
    .split(/[,;\n]/)
    .map((descriptor) => descriptor.trim())
    .filter(Boolean)
}

function mergeDescriptors(...descriptorGroups) {
  const seen = new Set()
  const merged = []
  descriptorGroups.flat().forEach((descriptor) => {
    const normalized = descriptor.trim()
    const key = normalized.toLocaleLowerCase()
    if (!normalized || seen.has(key)) return
    seen.add(key)
    merged.push(normalized)
  })
  return merged
}

function toLocal(a) {
  return {
    id: a.id,
    name: a.name,
    cat: normalizeCategoryCode(a.categories?.[0]?.code),
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
  const [newAlert, setNewAlert] = useState({
    name: '',
    descriptorsText: '',
    cat: '',
    cron: '*/15 * * * *',
    rssChannelIds: [],
  })
  const [error, setError] = useState('')
  const [synonymSuggestions, setSynonymSuggestions] = useState([])
  const [acceptedSynonyms, setAcceptedSynonyms] = useState([])
  const [loadingSynonyms, setLoadingSynonyms] = useState(false)
  const [synonymsFetched, setSynonymsFetched] = useState(false)
  const [synonymsError, setSynonymsError] = useState('')

  // Edit modal
  const [showEditModal, setShowEditModal] = useState(false)
  const [editData, setEditData] = useState({
    id: null,
    name: '',
    descriptorsText: '',
    cat: '',
    cron: '*/15 * * * *',
    rssChannelIds: [],
  })
  const [editAcceptedSynonyms, setEditAcceptedSynonyms] = useState([])
  const [editSuggestions, setEditSuggestions] = useState([])
  const [editError, setEditError] = useState('')
  const [loadingEditSynonyms, setLoadingEditSynonyms] = useState(false)
  const [editSynonymsFetched, setEditSynonymsFetched] = useState(false)
  const [editSynonymsError, setEditSynonymsError] = useState('')

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
  const categoryPayload = (code) => {
    const normalizedCode = normalizeCategoryCode(code)
    const category = categories.find((c) => c.value === normalizedCode)
    return category ? [{ code: normalizedCode, label: category.canonicalName }] : []
  }

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
        canonicalName: category.name,
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
          return channels.map((ch) => ({ id: String(ch.id), label: `${src.name} — ${ch.url}`, categoryId: ch.category_id }))
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
        descriptors: alert.descriptors ?? [],
        categories: categoryPayload(alert.cat),
        rss_channels_ids: alert.rssChannelIds ?? [],
      }),
    })
  }

  // ── Create modal handlers ──────────────────────────────────────────────────

  const fetchNvidiaSynonyms = async (word) => {
    const apiKey = import.meta.env.VITE_NVIDIA_API_KEY
    const res = await fetch('https://integrate.api.nvidia.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: 'meta/llama-3.1-8b-instruct',
        messages: [
          {
            role: 'user',
            content: `Dame exactamente 3 sinónimos o palabras relacionadas en español para el término "${word}" en el contexto de noticias. Responde SOLO con un array JSON de strings, sin explicación. Ejemplo: ["término1","término2","término3"]`,
          },
        ],
        temperature: 0.3,
        max_tokens: 60,
      }),
    })
    if (!res.ok) throw new Error('nvidia_error')
    const data = await res.json()
    const text = data.choices?.[0]?.message?.content ?? ''
    const match = text.match(/\[.*?\]/s)
    if (!match) throw new Error('parse_error')
    return JSON.parse(match[0]).slice(0, 3)
  }

  const handleFetchSynonyms = async () => {
    if (!newAlert.name.trim()) return
    setLoadingSynonyms(true)
    setSynonymSuggestions([])
    setAcceptedSynonyms([])
    setSynonymsFetched(false)
    setSynonymsError('')
    try {
      const synonyms = await fetchNvidiaSynonyms(newAlert.name.trim())
      setSynonymSuggestions(synonyms)
    } catch {
      setSynonymsError(t('alerts.synonymsError', 'No se pudieron obtener sugerencias'))
    } finally {
      setLoadingSynonyms(false)
      setSynonymsFetched(true)
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
    const descriptors = mergeDescriptors(parseDescriptors(newAlert.descriptorsText), acceptedSynonyms)
    if (descriptors.length === 0) {
      setError(t('alerts.descriptorsRequired', 'Introduce al menos un descriptor separado por comas'))
      return
    }
    const payload = {
      name: newAlert.name.trim(),
      cron_expression: newAlert.cron,
      descriptors,
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
      setNewAlert({
        name: '',
        descriptorsText: '',
        cat: categories[0]?.value ?? '',
        cron: '*/15 * * * *',
        rssChannelIds: [],
      })
      setSynonymSuggestions([])
      setAcceptedSynonyms([])
      setShowModal(false)
    } catch (err) {
      setError(err.message)
    }
  }

  // ── Edit modal handlers ────────────────────────────────────────────────────

  const handleOpenEdit = (alert) => {
    setEditData({
      id: alert.id,
      name: alert.name,
      descriptorsText: (alert.descriptors ?? []).join(', '),
      cat: alert.cat,
      cron: alert.cron,
      rssChannelIds: alert.rssChannelIds,
    })
    setEditAcceptedSynonyms([])
    setEditSuggestions([])
    setEditError('')
    setEditSynonymsFetched(false)
    setEditSynonymsError('')
    setShowEditModal(true)
  }

  const handleFetchEditSynonyms = async () => {
    if (!editData.name.trim()) return
    setLoadingEditSynonyms(true)
    setEditSuggestions([])
    setEditSynonymsFetched(false)
    setEditSynonymsError('')
    try {
      const synonyms = await fetchNvidiaSynonyms(editData.name.trim())
      const currentDescriptors = mergeDescriptors(parseDescriptors(editData.descriptorsText), editAcceptedSynonyms)
      setEditSuggestions(
        synonyms.filter((w) => !currentDescriptors.some((d) => d.toLocaleLowerCase() === w.toLocaleLowerCase())),
      )
    } catch {
      setEditSynonymsError(t('alerts.synonymsError', 'No se pudieron obtener sugerencias'))
    } finally {
      setLoadingEditSynonyms(false)
      setEditSynonymsFetched(true)
    }
  }

  const toggleEditSuggestion = (word) => {
    if (editAcceptedSynonyms.includes(word)) {
      setEditAcceptedSynonyms((prev) => prev.filter((d) => d !== word))
    } else {
      setEditAcceptedSynonyms((prev) => [...prev, word])
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
    const descriptors = mergeDescriptors(parseDescriptors(editData.descriptorsText), editAcceptedSynonyms)
    if (descriptors.length === 0) {
      setEditError(t('alerts.descriptorsRequired', 'Introduce al menos un descriptor separado por comas'))
      return
    }
    const payload = {
      name: editData.name.trim(),
      cron_expression: editData.cron,
      enabled: currentAlert?.enabled ?? true,
      descriptors,
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
                  setSynonymsFetched(false)
                  setSynonymsError('')
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
                      setSynonymsFetched(false)
                      setSynonymsError('')
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
                <p className="text-xs text-slate-500">
                  {t('alerts.nameHint', 'Solo identifica la alerta; no se usa como descriptor de búsqueda.')}
                </p>
              </div>

              <div className="space-y-2">
                <label className="block text-xs font-bold uppercase text-slate-500">
                  {t('alerts.descriptorsLabel', 'Descriptores')}
                </label>
                <textarea
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 min-h-24 resize-y"
                  placeholder={t('alerts.descriptorsPlaceholder', 'Ej: elecciones, congreso, senado')}
                  value={newAlert.descriptorsText}
                  onChange={(e) => setNewAlert({ ...newAlert, descriptorsText: e.target.value })}
                  required
                />
                <p className="text-xs text-slate-500">
                  {t('alerts.descriptorsHint', 'Separa cada descriptor con una coma. Estos términos son los que disparan la alerta.')}
                </p>
                {synonymsError && (
                  <p className="text-xs text-red-500 pt-1">{synonymsError}</p>
                )}
                {!synonymsError && synonymsFetched && !loadingSynonyms && synonymSuggestions.length === 0 && (
                  <p className="text-xs text-slate-400 pt-1">
                    {t('alerts.synonymsEmpty', 'No se encontraron sugerencias para esta palabra')}
                  </p>
                )}
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
                  onChange={(e) => setNewAlert({ ...newAlert, cat: e.target.value, rssChannelIds: [] })}
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
                  options={rssChannels.filter((ch) => ch.categoryId === parseInt(newAlert.cat, 10))}
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
                      setEditSynonymsFetched(false)
                      setEditSynonymsError('')
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
                <p className="text-xs text-slate-500">
                  {t('alerts.nameHint', 'Solo identifica la alerta; no se usa como descriptor de búsqueda.')}
                </p>
              </div>

              <div className="space-y-2">
                <label className="block text-xs font-bold uppercase text-slate-500">
                  {t('alerts.descriptorsLabel', 'Descriptores')}
                </label>
                <textarea
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 min-h-24 resize-y"
                  placeholder={t('alerts.descriptorsPlaceholder', 'Ej: elecciones, congreso, senado')}
                  value={editData.descriptorsText}
                  onChange={(e) => {
                    setEditData({ ...editData, descriptorsText: e.target.value })
                    setEditSuggestions([])
                  }}
                  required
                />
                <p className="text-xs text-slate-500">
                  {t('alerts.descriptorsHint', 'Separa cada descriptor con una coma. Estos términos son los que disparan la alerta.')}
                </p>

                {editAcceptedSynonyms.length > 0 && (
                  <div className="flex flex-wrap gap-2 pt-1">
                    {editAcceptedSynonyms.map((word) => (
                      <button
                        key={word}
                        type="button"
                        onClick={() => toggleEditSuggestion(word)}
                        className="px-3 py-1 rounded-full text-xs font-medium bg-primary-container text-white"
                      >
                        {word} ×
                      </button>
                    ))}
                  </div>
                )}

                {editSynonymsError && (
                  <p className="text-xs text-red-500 pt-1">{editSynonymsError}</p>
                )}
                {!editSynonymsError && editSynonymsFetched && !loadingEditSynonyms && editSuggestions.length === 0 && (
                  <p className="text-xs text-slate-400 pt-1">
                    {t('alerts.synonymsEmpty', 'No se encontraron sugerencias para esta palabra')}
                  </p>
                )}
                {editSuggestions.length > 0 && (
                  <div className="pt-1">
                    <p className="text-[10px] uppercase font-bold text-slate-400 mb-2">
                      {t('alerts.synonymsHint', 'Selecciona los que quieras incluir')}
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {editSuggestions.map((word) => {
                        const isAdded = editAcceptedSynonyms.includes(word)
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
                  onChange={(e) => setEditData({ ...editData, cat: e.target.value, rssChannelIds: [] })}
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
                  options={rssChannels.filter((ch) => ch.categoryId === parseInt(editData.cat, 10))}
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
