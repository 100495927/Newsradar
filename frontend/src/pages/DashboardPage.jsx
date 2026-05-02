import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import TopNavBar from '../components/TopNavBar'
import SideNavBar from '../components/SideNavBar'
import MobileNav from '../components/MobileNav'
import PageHeader from '../components/PageHeader'
import StatsGrid from '../components/StatsGrid'
import TrendChart from '../components/TrendChart'
import CategoryVolumeCard from '../components/CategoryVolumeCard'
import { apiFetch, getGlobalStats, getTimeline } from '../api/apiClient'

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

function buildStatCards(data, t) {
  return [
    {
      id: 'total-news',
      title: t('dashboard.totalNews'),
      value: data.n_noticias.toLocaleString(),
      icon: 'newspaper',
      cardAccent: 'default',
    },
    {
      id: 'sources',
      title: t('dashboard.activeSources'),
      value: data.n_fuentes.toLocaleString(),
      icon: 'source',
      cardAccent: 'default',
    },
    {
      id: 'alerts',
      title: t('dashboard.alerts'),
      value: data.n_alertas.toLocaleString(),
      icon: 'notifications_active',
      cardAccent: 'default',
      badge: null,
      badgeTone: 'red',
    },
    {
      id: 'rss-channels',
      title: t('dashboard.rssChannels'),
      value: data.n_canales_rss.toLocaleString(),
      icon: 'rss_feed',
      cardAccent: 'default',
    },
  ]
}

function buildCategories(noticiasPorCategoria, categoryNames) {
  const top = noticiasPorCategoria.slice(0, 8)
  const total = top.reduce((sum, c) => sum + c.total, 0) || 1
  return top.map((cat, i) => ({
    id: cat.id,
    label: categoryNames[cat.id] || cat.id,
    value: Math.round((cat.total / total) * 100),
    color: CATEGORY_COLORS[i % CATEGORY_COLORS.length],
  }))
}

function DashboardPage() {
  const { t } = useTranslation()
  const [stats, setStats] = useState(null)
  const [timeline, setTimeline] = useState([])
  const [categoryNames, setCategoryNames] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      getGlobalStats(),
      getTimeline(),
      apiFetch('/api/v1/categories').then((res) => res.json()).catch(() => []),
    ])
      .then(([globalData, timelineData, categories]) => {
        setStats(globalData)
        setTimeline(timelineData)
        setCategoryNames(
          Object.fromEntries(categories.map((category) => [String(category.id), category.name])),
        )
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const statCards = stats ? buildStatCards(stats, t) : []
  const categories = stats ? buildCategories(stats.noticias_por_categoria, categoryNames) : []

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
