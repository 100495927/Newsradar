import { useEffect, useState } from 'react'
import TopNavBar from '../components/TopNavBar'
import SideNavBar from '../components/SideNavBar'
import MobileNav from '../components/MobileNav'
import PageHeader from '../components/PageHeader'
import StatsGrid from '../components/StatsGrid'
import TrendChart from '../components/TrendChart'
import CategoryVolumeCard from '../components/CategoryVolumeCard'
import { getGlobalStats, getTimeline } from '../api/apiClient'

const CATEGORY_COLORS = [
  'bg-blue-400',
  'bg-emerald-400',
  'bg-violet-400',
  'bg-amber-400',
  'bg-rose-400',
  'bg-cyan-400',
  'bg-slate-300',
  'bg-orange-400',
]

function buildStatCards(data) {
  return [
    {
      id: 'total-news',
      title: 'Noticias Totales',
      value: data.n_noticias.toLocaleString('es-ES'),
      icon: 'newspaper',
      cardAccent: 'default',
    },
    {
      id: 'sources',
      title: 'Fuentes Activas',
      value: data.n_fuentes.toLocaleString('es-ES'),
      icon: 'source',
      cardAccent: 'default',
    },
    {
      id: 'alerts',
      title: 'Alertas',
      value: data.n_alertas.toLocaleString('es-ES'),
      icon: 'notifications_active',
      cardAccent: data.n_alertas > 0 ? 'critical' : 'default',
      badge: data.n_alertas > 0 ? 'Activas' : null,
      badgeTone: 'red',
    },
    {
      id: 'rss-channels',
      title: 'Canales RSS',
      value: data.n_canales_rss.toLocaleString('es-ES'),
      icon: 'rss_feed',
      cardAccent: 'default',
    },
  ]
}

function buildCategories(noticiasPorCategoria) {
  const top = noticiasPorCategoria.slice(0, 8)
  const total = top.reduce((sum, c) => sum + c.total, 0) || 1
  return top.map((cat, i) => ({
    id: cat.id,
    label: cat.id,
    value: Math.round((cat.total / total) * 100),
    color: CATEGORY_COLORS[i % CATEGORY_COLORS.length],
  }))
}

function DashboardPage() {
  const [stats, setStats] = useState(null)
  const [timeline, setTimeline] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getGlobalStats(), getTimeline()])
      .then(([globalData, timelineData]) => {
        setStats(globalData)
        setTimeline(timelineData)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const statCards = stats ? buildStatCards(stats) : []
  const categories = stats ? buildCategories(stats.noticias_por_categoria) : []

  return (
    <div className="bg-surface text-on-surface min-h-screen">
      <TopNavBar />
      <SideNavBar />
      <main className="lg:pl-64 pt-16 min-h-screen">
        <div className="p-6 md:p-10 max-w-7xl mx-auto space-y-10">
          <PageHeader />

          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm animate-pulse h-32" />
              ))}
            </div>
          ) : (
            <StatsGrid stats={statCards} />
          )}

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <TrendChart data={timeline} loading={loading} />
            <div className="lg:col-span-4 flex flex-col gap-8">
              <CategoryVolumeCard categories={categories} loading={loading} />
            </div>
          </div>
        </div>
      </main>
      <MobileNav />
    </div>
  )
}

export default DashboardPage
