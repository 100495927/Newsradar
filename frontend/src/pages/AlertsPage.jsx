import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import TopNavBar from '../components/TopNavBar'
import SideNavBar from '../components/SideNavBar'
import MobileNav from '../components/MobileNav'
import MultiSelectSearch from '../components/MultiSelectSearch'
import { useAuth } from '../context/AuthContext'
import { apiFetch } from '../api/apiClient'

// Map backend Alert to local shape
function toLocal(a) {
  return {
    id: a.id,
    name: a.name,
    cat: a.categories?.[0]?.code ?? '',
    cron: a.cron_expression,
    enabled: a.enabled ?? true,
    rssChannelIds: (a.rss_channels_ids ?? []).map(String),
  }
}

function AlertsPage() {
  const { t } = useTranslation()
  const { user } = useAuth()
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [newAlert, setNewAlert] = useState({ name: '', cat: 'FIN_MRKT', cron: '', rssChannelIds: [] })
  const [error, setError] = useState('')
  const [rssChannels, setRssChannels] = useState([])

  const categories = [
    { value: 'FIN_MRKT', label: t('categories.FIN_MRKT') },
    { value: 'SEC_POL', label: t('categories.SEC_POL') },
    { value: 'TECH', label: t('categories.TECH') },
    { value: 'ENERGY', label: t('categories.ENERGY') },
    { value: 'HEALTH', label: t('categories.HEALTH') },
  ]

  useEffect(() => {
    if (user?.id) fetchAlerts()
    fetchRssChannels()
  }, [user?.id])

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
          return channels.map((ch) => ({
            id: String(ch.id),
            label: `${src.name} — ${ch.url}`,
          }))
        }),
      )
      setRssChannels(channelLists.flat())
    } catch {
      // silencioso si la API no está disponible
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
    const updated = alerts.map((a) => a.id === id ? { ...a, enabled: !a.enabled } : a)
    setAlerts(updated)
    const alert = updated.find((a) => a.id === id)
    await apiFetch(`/api/v1/users/${user.id}/alerts/${id}`, {
      method: 'PUT',
      body: JSON.stringify({
        name: alert.name,
        cron_expression: alert.cron,
        enabled: alert.enabled,
        descriptors: [alert.name],
        categories: categories
          .filter((c) => c.value === alert.cat)
          .map((c) => ({ code: c.value, label: c.label })),
        rss_channels_ids: alert.rssChannelIds ?? [],
      }),
    })
  }

  const handleCreateAlert = async (e) => {
    e.preventDefault()
    setError('')
    if (!newAlert.name.trim() || !newAlert.cron.trim()) return

    const catInfo = categories.find((c) => c.value === newAlert.cat)
    const payload = {
      name: newAlert.name,
      cron_expression: newAlert.cron,
      descriptors: [newAlert.name],
      categories: catInfo ? [{ code: catInfo.value, label: catInfo.label }] : [],
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
      setNewAlert({ name: '', cat: 'FIN_MRKT', cron: '', rssChannelIds: [] })
      setShowModal(false)
    } catch (err) {
      setError(err.message)
    }
  }

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
            <button
              onClick={() => setShowModal(true)}
              className="bg-primary-container text-on-primary px-6 py-3 rounded-lg font-bold flex items-center gap-2 hover:opacity-90 active:scale-95 transition-all"
            >
              <span className="material-symbols-outlined">add</span>
              {t('alerts.createButton')}
            </button>
          </header>

          <div className="bg-surface-container-low rounded-xl overflow-hidden">
            <div className="grid grid-cols-12 gap-4 px-6 py-4 bg-surface-container-highest/50 border-b border-outline-variant/10">
              <div className="col-span-4 text-xs font-bold uppercase tracking-widest text-on-surface-variant">
                {t('alerts.colName')}
              </div>
              <div className="col-span-2 text-xs font-bold uppercase tracking-widest text-on-surface-variant">
                {t('alerts.colCategory')}
              </div>
              <div className="col-span-3 text-xs font-bold uppercase tracking-widest text-on-surface-variant">
                {t('alerts.colFrequency')}
              </div>
              <div className="col-span-3 text-xs font-bold uppercase tracking-widest text-on-surface-variant text-right">
                {t('alerts.colStatus')}
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
                <span className="material-symbols-outlined text-4xl mb-2">
                  notifications_off
                </span>
                <p>{t('alerts.empty')}</p>
              </div>
            ) : (
              alerts.map((a) => (
                <div
                  key={a.id}
                  className={`grid grid-cols-12 gap-4 px-6 py-6 items-center hover:bg-white border-b border-outline-variant/10 transition-opacity ${
                    !a.enabled ? 'opacity-50' : ''
                  }`}
                >
                  <div className="col-span-4">
                    <div className="font-bold text-primary-container text-lg">
                      {a.name}
                    </div>
                  </div>
                  <div className="col-span-2">
                    <span className="text-xs font-mono bg-surface-variant px-2 py-1 rounded">
                      {a.cat}
                    </span>
                  </div>
                  <div className="col-span-3 font-mono text-xs">{a.cron}</div>
                  <div className="col-span-3 flex justify-end items-center gap-3">
                    <button
                      onClick={() => handleToggle(a.id)}
                      className={`w-11 h-6 rounded-full relative transition-colors ${
                        a.enabled ? 'bg-primary-container' : 'bg-slate-300'
                      }`}
                    >
                      <div
                        className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${
                          a.enabled ? 'right-1' : 'left-1'
                        }`}
                      ></div>
                    </button>
                    <button
                      onClick={() => handleDelete(a.id)}
                      className="material-symbols-outlined text-on-surface-variant hover:text-red-500 transition-colors"
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

      {/* Create Alert Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full p-8">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-slate-900">{t('alerts.modalTitle')}</h3>
              <button
                onClick={() => setShowModal(false)}
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
                <input
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3"
                  placeholder={t('alerts.namePlaceholder')}
                  value={newAlert.name}
                  onChange={(e) => setNewAlert({ ...newAlert, name: e.target.value })}
                  required
                />
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
                  placeholder="Buscar canales RSS..."
                />
              </div>

              <div className="space-y-2">
                <label className="block text-xs font-bold uppercase text-slate-500">
                  {t('alerts.cronLabel')}
                </label>
                <input
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 font-mono text-sm"
                  placeholder="*/15 * * * *"
                  value={newAlert.cron}
                  onChange={(e) => setNewAlert({ ...newAlert, cron: e.target.value })}
                  required
                />
                <p className="text-xs text-slate-400">{t('alerts.cronHint')}</p>
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
    </div>
  )
}

export default AlertsPage
