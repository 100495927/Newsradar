import { useState, useEffect } from 'react'
import TopNavBar from '../components/TopNavBar'
import SideNavBar from '../components/SideNavBar'
import MobileNav from '../components/MobileNav'

const mockAlerts = [
  { id: 1, name: 'Volatilidad Energética', cat: 'FIN_MRKT', cron: '0 9 * * 1-5', enabled: true },
  { id: 2, name: 'Tensión Geopolítica: Báltico', cat: 'SEC_POL', cron: '*/15 * * * *', enabled: true },
]

const categories = [
  { value: 'FIN_MRKT', label: 'Finanzas y Mercados' },
  { value: 'SEC_POL', label: 'Seguridad Política' },
  { value: 'TECH', label: 'Tecnología' },
  { value: 'ENERGY', label: 'Energía' },
  { value: 'HEALTH', label: 'Salud' },
]

function AlertsPage() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [newAlert, setNewAlert] = useState({ name: '', cat: 'FIN_MRKT', cron: '' })

  useEffect(() => {
    fetchAlerts()
  }, [])

  const fetchAlerts = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/alertas')
      if (!response.ok) throw new Error('API no disponible')
      const data = await response.json()
      setAlerts(data)
    } catch (err) {
      console.warn('Usando datos de fallback:', err.message)
      setAlerts(mockAlerts)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    try {
      await fetch(`/api/alertas/${id}`, { method: 'DELETE' })
    } catch (err) {
      console.warn('API no disponible, eliminando localmente')
    }
    setAlerts(alerts.filter((a) => a.id !== id))
  }

  const handleToggle = async (id) => {
    const updated = alerts.map((a) =>
      a.id === id ? { ...a, enabled: !a.enabled } : a
    )
    setAlerts(updated)

    try {
      const alert = updated.find((a) => a.id === id)
      await fetch(`/api/alertas/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: alert.enabled }),
      })
    } catch (err) {
      console.warn('API no disponible, cambio guardado localmente')
    }
  }

  const handleCreateAlert = async (e) => {
    e.preventDefault()
    if (!newAlert.name.trim() || !newAlert.cron.trim()) return

    const alertToCreate = {
      id: Date.now(),
      ...newAlert,
      enabled: true,
    }

    try {
      const response = await fetch('/api/alertas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(alertToCreate),
      })
      if (response.ok) {
        const savedAlert = await response.json()
        setAlerts([...alerts, savedAlert])
      } else {
        throw new Error('API error')
      }
    } catch (err) {
      console.warn('API no disponible, agregando localmente')
      setAlerts([...alerts, alertToCreate])
    }

    setNewAlert({ name: '', cat: 'FIN_MRKT', cron: '' })
    setShowModal(false)
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
                Gestión de Alertas
              </h1>
              <p className="text-on-primary-container font-medium max-w-lg">
                Configure sus disparadores de inteligencia.
              </p>
            </div>
            <button
              onClick={() => setShowModal(true)}
              className="bg-primary-container text-on-primary px-6 py-3 rounded-lg font-bold flex items-center gap-2 hover:opacity-90 active:scale-95 transition-all"
            >
              <span className="material-symbols-outlined">add</span> Crear Nueva
              Alerta
            </button>
          </header>

          <div className="bg-surface-container-low rounded-xl overflow-hidden">
            <div className="grid grid-cols-12 gap-4 px-6 py-4 bg-surface-container-highest/50 border-b border-outline-variant/10">
              <div className="col-span-4 text-xs font-bold uppercase tracking-widest text-on-surface-variant">
                Nombre de Alerta
              </div>
              <div className="col-span-2 text-xs font-bold uppercase tracking-widest text-on-surface-variant">
                Categoría
              </div>
              <div className="col-span-3 text-xs font-bold uppercase tracking-widest text-on-surface-variant">
                Frecuencia
              </div>
              <div className="col-span-3 text-xs font-bold uppercase tracking-widest text-on-surface-variant text-right">
                Estado
              </div>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-12">
                <span className="material-symbols-outlined animate-spin text-slate-400">
                  progress_activity
                </span>
                <span className="ml-2 text-slate-500">Cargando alertas...</span>
              </div>
            ) : alerts.length === 0 ? (
              <div className="text-center py-12 text-slate-500">
                <span className="material-symbols-outlined text-4xl mb-2">
                  notifications_off
                </span>
                <p>No hay alertas configuradas</p>
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
              <h3 className="text-2xl font-bold text-slate-900">Nueva Alerta</h3>
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
                  Nombre de Alerta
                </label>
                <input
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3"
                  placeholder="Ej: Volatilidad del Mercado"
                  value={newAlert.name}
                  onChange={(e) =>
                    setNewAlert({ ...newAlert, name: e.target.value })
                  }
                  required
                />
              </div>

              <div className="space-y-2">
                <label className="block text-xs font-bold uppercase text-slate-500">
                  Categoría
                </label>
                <select
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3"
                  value={newAlert.cat}
                  onChange={(e) =>
                    setNewAlert({ ...newAlert, cat: e.target.value })
                  }
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
                  Frecuencia (Cron)
                </label>
                <input
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 font-mono text-sm"
                  placeholder="*/15 * * * *"
                  value={newAlert.cron}
                  onChange={(e) =>
                    setNewAlert({ ...newAlert, cron: e.target.value })
                  }
                  required
                />
                <p className="text-xs text-slate-400">
                  Ejemplos: */15 * * * * (cada 15 min), 0 9 * * 1-5 (9AM L-V)
                </p>
              </div>

              <div className="flex gap-4 justify-end pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-6 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-medium transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-6 py-2.5 bg-primary-container text-white rounded-lg font-medium transition-colors hover:opacity-90"
                >
                  Crear Alerta
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
