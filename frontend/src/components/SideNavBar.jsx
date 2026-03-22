import { Link, useLocation } from 'react-router-dom'

const navItems = [
  { id: 'dashboard', label: 'Panel de Control', icon: 'dashboard', path: '/dashboard' },
  { id: 'summary', label: 'Mi Resumen', icon: 'auto_stories', path: '/summary' },
  { id: 'alerts', label: 'Alertas', icon: 'notifications_active', path: '/alerts' },
  { id: 'sources', label: 'Fuentes', icon: 'rss_feed', path: '/sources' },
]

function SideNavBar() {
  const location = useLocation()
  const isActive = (path) => location.pathname === path

  return (
    <aside className="fixed left-0 top-0 h-full flex flex-col pt-20 pb-6 px-4 bg-slate-50 w-64 hidden lg:flex border-r border-slate-200 z-40">
      <div className="mb-8 px-4">
        <h2 className="text-lg font-black text-[#0A192F] headline-font">
          NewsRadar
        </h2>
        <p className="text-xs text-slate-500 font-medium uppercase tracking-widest opacity-70">
          Lente de Inteligencia
        </p>
      </div>
      <nav className="flex flex-col gap-1 flex-1">
        {navItems.map((item) => (
          <Link
            key={item.id}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all font-medium text-sm ${
              isActive(item.path)
                ? 'text-[#0A192F] bg-white shadow-sm ring-1 ring-slate-200/50 translate-x-1 font-bold'
                : 'text-slate-600 hover:text-[#0A192F] hover:bg-slate-100'
            }`}
            to={item.path}
          >
            <span className="material-symbols-outlined text-[20px]">
              {item.icon}
            </span>
            <span>{item.label}</span>
          </Link>
        ))}
        <Link
          className="flex items-center gap-3 px-4 py-3 text-slate-600 hover:text-[#0A192F] hover:bg-slate-100 transition-all mt-auto rounded-lg"
          to="/profile"
        >
          <span className="material-symbols-outlined text-[20px]">
            settings
          </span>
          <span className="text-sm">Configuración</span>
        </Link>
      </nav>
    </aside>
  )
}

export default SideNavBar
