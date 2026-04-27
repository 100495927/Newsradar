import { Link, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

function MobileNav() {
  const location = useLocation()
  const { t } = useTranslation()
  const isActive = (path) => location.pathname === path

  const mobileItems = [
    { id: 'dashboard', label: t('mobileNav.dashboard'), icon: 'dashboard', path: '/dashboard' },
    { id: 'summary', label: t('mobileNav.summary'), icon: 'auto_stories', path: '/summary' },
    { id: 'alerts', label: t('mobileNav.alerts'), icon: 'notification_important', path: '/alerts' },
    { id: 'profile', label: t('mobileNav.profile'), icon: 'settings', path: '/profile' },
  ]

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
