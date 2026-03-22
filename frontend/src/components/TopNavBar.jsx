import { Link } from 'react-router-dom'

function TopNavBar() {
  return (
    <header className="fixed top-0 left-0 w-full z-50 flex items-center px-6 h-16 bg-white shadow-none border-b border-slate-100">
      <Link
        to="/dashboard"
        className="text-xl font-extrabold tracking-tighter text-[#0A192F] headline-font"
      >
        NEWSRADAR
      </Link>

      <div className="flex-1 flex justify-center">
        <div className="relative hidden sm:block">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm">
            search
          </span>
          <input
            className="pl-12 pr-6 py-3 bg-slate-50 border border-slate-200 rounded-xl text-base focus:ring-2 focus:ring-slate-400 focus:border-slate-400 w-[48rem] outline-none transition-all"
            placeholder="Búsqueda Global..."
            type="text"
          />
        </div>
      </div>

      <Link
        to="/profile"
        className="p-2 text-slate-500 hover:bg-slate-50 rounded-full transition-transform active:scale-100 scale-95"
        aria-label="Perfil"
      >
        <span className="material-symbols-outlined">account_circle</span>
      </Link>
    </header>
  )
}

export default TopNavBar
