import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import LanguageSwitcher from './LanguageSwitcher'

function TopNavBar() {
  const { t } = useTranslation()

  return (
    <header className="fixed top-0 left-0 w-full z-50 flex items-center px-6 h-16 bg-white shadow-none border-b border-slate-100">
      <Link
        to="/dashboard"
        className="text-xl font-extrabold tracking-tighter text-[#0A192F] headline-font"
      >
        NEWSRADAR
      </Link>

      <div className="flex-1" />

      <div className="flex items-center gap-1">
        <LanguageSwitcher />
        <Link
          to="/profile"
          className="p-2 text-slate-500 hover:bg-slate-50 rounded-full transition-transform active:scale-100 scale-95"
          aria-label="Perfil"
        >
          <span className="material-symbols-outlined">account_circle</span>
        </Link>
      </div>
    </header>
  )
}

export default TopNavBar
