import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import TopNavBar from '../components/TopNavBar'
import SideNavBar from '../components/SideNavBar'
import MobileNav from '../components/MobileNav'
import { useAuth } from '../context/AuthContext'
import { apiFetch } from '../api/apiClient'

function formatRelativeTime(dateStr) {
  const diff = Date.now() - new Date(dateStr).getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return 'ahora mismo'
  if (minutes < 60) return `hace ${minutes}m`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `hace ${hours}h`
  const days = Math.floor(hours / 24)
  return `hace ${days}d`
}

function NotificationsPage() {
  const { t } = useTranslation()
  const { user } = useAuth()
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)
  const [clearing, setClearing] = useState(false)
  const [expanded, setExpanded] = useState(new Set())

  useEffect(() => {
    if (user?.id) fetchNotifications()
  }, [user?.id])

  const fetchNotifications = async () => {
    try {
      setLoading(true)
      // Contrato: GET /users/{uid}/alerts → por cada alerta GET .../notifications
      const alertsRes = await apiFetch(`/api/v1/users/${user.id}/alerts`)
      if (!alertsRes.ok) return
      const alerts = await alertsRes.json()

      const byAlert = await Promise.all(
        alerts.map(async (alert) => {
          const res = await apiFetch(
            `/api/v1/users/${user.id}/alerts/${alert.id}/notifications`,
          )
          if (!res.ok) return []
          const items = await res.json()
          return items.map((n) => ({
            ...n,
            alert_id: alert.id,
            subject: `Actualización de ${alert.name} en ${new Date(n.timestamp).toLocaleString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })}`,
          }))
        }),
      )

      setNotifications(
        byAlert.flat().sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)),
      )
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (alertId, notificationId) => {
    setNotifications((prev) => prev.filter((n) => n.id !== notificationId))
    await apiFetch(
      `/api/v1/users/${user.id}/alerts/${alertId}/notifications/${notificationId}`,
      { method: 'DELETE' },
    )
  }

  const handleClearAll = async () => {
    setClearing(true)
    await Promise.all(
      notifications.map((n) =>
        apiFetch(
          `/api/v1/users/${user.id}/alerts/${n.alert_id}/notifications/${n.id}`,
          { method: 'DELETE' },
        ),
      ),
    )
    setNotifications([])
    setClearing(false)
  }

  const toggleExpand = (id) => {
    setExpanded((prev) => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  return (
    <div className="bg-background min-h-screen">
      <TopNavBar />
      <SideNavBar />
      <main className="lg:ml-64 pt-24 pb-12 px-6 lg:px-12">
        <div className="max-w-4xl mx-auto">
          <header className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
            <div>
              <h1 className="text-4xl font-extrabold tracking-tighter text-primary-container mb-2">
                {t('notifications.pageTitle', 'Notificaciones')}
              </h1>
              <p className="text-slate-500 font-medium">
                {t('notifications.pageSubtitle', 'Buzón de alertas procesadas')}
              </p>
            </div>
            {notifications.length > 0 && (
              <button
                onClick={handleClearAll}
                disabled={clearing}
                className="flex items-center gap-2 px-5 py-2.5 bg-slate-100 hover:bg-red-50 hover:text-red-600 text-slate-600 rounded-lg text-sm font-bold transition-colors disabled:opacity-50"
              >
                <span className="material-symbols-outlined text-[18px]">delete_sweep</span>
                {clearing
                  ? t('notifications.clearing', 'Limpiando...')
                  : t('notifications.clearAll', 'Limpiar buzón')}
              </button>
            )}
          </header>

          {loading ? (
            <div className="space-y-3">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="bg-white border border-slate-200 rounded-xl p-5 animate-pulse h-24" />
              ))}
            </div>
          ) : notifications.length === 0 ? (
            <div className="bg-white border border-slate-200 rounded-xl p-16 text-center">
              <span className="material-symbols-outlined text-5xl text-slate-300 mb-4 block">
                notifications_off
              </span>
              <p className="text-slate-400 font-medium uppercase tracking-widest text-xs">
                {t('notifications.empty', 'No hay notificaciones')}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {notifications.map((n) => {
                const isOpen = expanded.has(n.id)
                return (
                  <div
                    key={n.id}
                    className="bg-white border border-slate-200 rounded-xl overflow-hidden hover:border-primary-container/30 transition-colors"
                  >
                    {/* Header row */}
                    <div className="flex items-start gap-4 p-5">
                      <div className="w-10 h-10 rounded-full bg-primary-container/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="material-symbols-outlined text-primary-container text-[20px]">
                          notifications_active
                        </span>
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-4">
                          <div className="min-w-0">
                            <p className="font-bold text-slate-900 text-sm truncate">
                              {n.subject}
                            </p>
                            <p className="text-xs text-slate-400 mt-0.5">
                              {new Date(n.timestamp).toLocaleString('es-ES', {
                                day: '2-digit',
                                month: '2-digit',
                                year: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit',
                              })}{' '}
                              · {formatRelativeTime(n.timestamp)}
                            </p>
                          </div>
                          <div className="flex items-center gap-2 flex-shrink-0">
                            {n.matches?.length > 0 && (
                              <button
                                onClick={() => toggleExpand(n.id)}
                                className="text-xs text-primary-container font-bold flex items-center gap-1 hover:opacity-70"
                              >
                                <span className="material-symbols-outlined text-[16px]">
                                  {isOpen ? 'expand_less' : 'expand_more'}
                                </span>
                                {n.matches.length} noticias
                              </button>
                            )}
                            <button
                              onClick={() => handleDelete(n.alert_id, n.id)}
                              className="material-symbols-outlined text-slate-300 hover:text-red-500 transition-colors text-[20px]"
                            >
                              close
                            </button>
                          </div>
                        </div>

                        {/* Metrics */}
                        {n.metrics?.length > 0 && (
                          <div className="mt-3 flex flex-wrap gap-2">
                            {n.metrics.map((m) => (
                              <span
                                key={m.name}
                                className="inline-flex items-center gap-1 px-2.5 py-1 bg-slate-50 border border-slate-200 rounded-lg text-[11px] font-medium text-slate-600"
                              >
                                <span className="font-bold text-primary-container">{m.value}</span>
                                {m.name}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Matches (noticias que dispararon la alerta) */}
                    {isOpen && n.matches?.length > 0 && (
                      <div className="border-t border-slate-100 divide-y divide-slate-50">
                        {n.matches.map((match, i) => (
                          <div key={i} className="px-5 py-3 bg-slate-50/60">
                            <div className="flex items-start gap-3">
                              <span className="material-symbols-outlined text-slate-300 text-sm mt-0.5">
                                article
                              </span>
                              <div className="min-w-0">
                                {match.link ? (
                                  <a
                                    href={match.link}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-xs font-semibold text-primary-container hover:underline line-clamp-2"
                                  >
                                    {match.title || match.link}
                                  </a>
                                ) : (
                                  <p className="text-xs font-semibold text-slate-700 line-clamp-2">
                                    {match.title}
                                  </p>
                                )}
                                <div className="flex items-center gap-2 mt-1">
                                  {match.source && (
                                    <span className="text-[10px] text-slate-400">{match.source}</span>
                                  )}
                                  {match.published_at && (
                                    <span className="text-[10px] text-slate-400">
                                      {new Date(match.published_at).toLocaleDateString('es-ES')}
                                    </span>
                                  )}
                                </div>
                                {match.matched_descriptors?.length > 0 && (
                                  <div className="flex flex-wrap gap-1 mt-1">
                                    {match.matched_descriptors.map((d) => (
                                      <span
                                        key={d}
                                        className="text-[9px] bg-primary-container/10 text-primary-container px-1.5 py-0.5 rounded font-mono"
                                      >
                                        {d}
                                      </span>
                                    ))}
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </main>
      <MobileNav />
    </div>
  )
}

export default NotificationsPage
