import { Link, useLocation } from 'react-router-dom'

const mobileItems = [
  { id: 'dashboard', label: 'Panel', icon: 'dashboard', path: '/dashboard' },
  { id: 'summary', label: 'Resumen', icon: 'auto_stories', path: '/summary' },
  { id: 'alerts', label: 'Alertas', icon: 'notification_important', path: '/alerts' },
  { id: 'profile', label: 'Perfil', icon: 'settings', path: '/profile' },
]

function MobileNav() {
  const location = useLocation()
  const isActive = (path) => location.pathname === path

  return (
    <nav className="md:hidden fixed bottom-0 left-0 w-full bg-[#0A192F] h-16 flex items-center justify-around px-4 z-50 border-t border-white/10">
      {mobileItems.map((item) => (
        <Link
          key={item.id}
          to={item.path}
          className={`flex flex-col items-center gap-1 ${
            isActive(item.path) ? 'text-white' : 'text-slate-400'
          }`}
        >
          <span className="material-symbols-outlined text-[20px]">
            {item.icon}
          </span>
          <span className="text-[8px] font-black uppercase tracking-tighter">
            {item.label}
          </span>
        </Link>
      ))}
    </nav>
  )
}

export default MobileNav
