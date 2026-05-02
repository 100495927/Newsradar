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

  useEffect(() => {
    if (user?.id) fetchAllNotifications()
  }, [user?.id])

  const fetchAllNotifications = async () => {
    try {
      setLoading(true)
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
            alertId: alert.id,
            alertName: alert.name,
          }))
        }),
      )

      const all = byAlert
        .flat()
        .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      setNotifications(all)
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
          `/api/v1/users/${user.id}/alerts/${n.alertId}/notifications/${n.id}`,
          { method: 'DELETE' },
        ),
      ),
    )
    setNotifications([])
    setClearing(false)
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
                <div
                  key={i}
                  className="bg-white border border-slate-200 rounded-xl p-5 animate-pulse h-24"
                />
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
              {notifications.map((n) => (
                <div
                  key={n.id}
                  className="bg-white border border-slate-200 rounded-xl p-5 flex items-start gap-4 hover:border-primary-container/30 transition-colors"
                >
                  <div className="w-10 h-10 rounded-full bg-primary-container/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="material-symbols-outlined text-primary-container text-[20px]">
                      notifications_active
                    </span>
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="font-bold text-slate-900 text-sm">
                          Actualización de{' '}
                          <span className="text-primary-container">{n.alertName}</span>
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
                      <button
                        onClick={() => handleDelete(n.alertId, n.id)}
                        className="material-symbols-outlined text-slate-300 hover:text-red-500 transition-colors text-[20px] flex-shrink-0"
                      >
                        close
                      </button>
                    </div>

                    {n.metrics && n.metrics.length > 0 && (
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
              ))}
            </div>
          )}
        </div>
      </main>
      <MobileNav />
    </div>
  )
}

export default NotificationsPage
