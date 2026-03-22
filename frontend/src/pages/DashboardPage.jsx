import TopNavBar from '../components/TopNavBar'
import SideNavBar from '../components/SideNavBar'
import MobileNav from '../components/MobileNav'
import PageHeader from '../components/PageHeader'
import StatsGrid from '../components/StatsGrid'
import TrendChart from '../components/TrendChart'
import CategoryVolumeCard from '../components/CategoryVolumeCard'

const stats = [
  {
    id: 'total-news',
    title: 'Noticias Totales',
    value: '1,429,082',
    icon: 'newspaper',
    badge: '+12.4%',
    badgeTone: 'emerald',
    cardAccent: 'default',
  },
  {
    id: 'sources',
    title: 'Nº de Fuentes',
    value: '12,540',
    icon: 'source',
    cardAccent: 'default',
  },
  {
    id: 'critical-alerts',
    title: 'Alertas Críticas',
    value: '342',
    icon: 'warning',
    badge: 'Activas',
    badgeTone: 'red',
    cardAccent: 'critical',
  },
  {
    id: 'extraction-rate',
    title: 'Extracción Global',
    value: '42.8k',
    unit: '/ hr',
    icon: 'speed',
    cardAccent: 'default',
  },
]

const categories = [
  { id: 'tech', label: 'Tecnología', value: 34, color: 'bg-blue-400' },
  { id: 'finance', label: 'Finanzas', value: 28, color: 'bg-slate-300' },
  { id: 'politics', label: 'Política', value: 22, color: 'bg-slate-500' },
  { id: 'health', label: 'Salud', value: 16, color: 'bg-white/40' },
]


function DashboardPage() {
  return (
    <div className="bg-surface text-on-surface min-h-screen">
      <TopNavBar />
      <SideNavBar />
      <main className="lg:pl-64 pt-16 min-h-screen">
        <div className="p-6 md:p-10 max-w-7xl mx-auto space-y-10">
          <PageHeader />
          <StatsGrid stats={stats} />
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <TrendChart />
            <div className="lg:col-span-4 flex flex-col gap-8">
              <CategoryVolumeCard categories={categories} />
            </div>
          </div>
                  </div>
      </main>
      <MobileNav />
    </div>
  )
}

export default DashboardPage
