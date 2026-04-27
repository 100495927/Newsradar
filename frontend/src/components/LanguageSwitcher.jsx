import { useState, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'

const LANGUAGES = [
  {
    code: 'es',
    label: 'Español',
    flag: (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 40" className="w-6 h-4 rounded-sm">
        <rect width="60" height="40" fill="#c60b1e"/>
        <rect y="10" width="60" height="20" fill="#ffc400"/>
      </svg>
    ),
  },
  {
    code: 'en',
    label: 'English',
    flag: (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 40" className="w-6 h-4 rounded-sm">
        {/* Blue background */}
        <rect width="60" height="40" fill="#012169"/>
        {/* White diagonals */}
        <line x1="0" y1="0" x2="60" y2="40" stroke="white" strokeWidth="6"/>
        <line x1="60" y1="0" x2="0" y2="40" stroke="white" strokeWidth="6"/>
        {/* Red diagonals */}
        <line x1="0" y1="0" x2="60" y2="40" stroke="#C8102E" strokeWidth="3.6"/>
        <line x1="60" y1="0" x2="0" y2="40" stroke="#C8102E" strokeWidth="3.6"/>
        {/* White cross */}
        <rect x="24" y="0" width="12" height="40" fill="white"/>
        <rect x="0" y="14" width="60" height="12" fill="white"/>
        {/* Red cross */}
        <rect x="26" y="0" width="8" height="40" fill="#C8102E"/>
        <rect x="0" y="16" width="60" height="8" fill="#C8102E"/>
      </svg>
    ),
  },
]

function LanguageSwitcher() {
  const { i18n, t } = useTranslation()
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  const currentLang = i18n.language?.startsWith('en') ? 'en' : 'es'

  // Close on outside click
  useEffect(() => {
    function handleClickOutside(e) {
      if (ref.current && !ref.current.contains(e.target)) {
        setOpen(false)
      }
    }
    if (open) document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [open])

  function selectLanguage(code) {
    i18n.changeLanguage(code)
    setOpen(false)
  }

  return (
    <div className="relative" ref={ref}>
      {/* Trigger button — globe icon */}
      <button
        onClick={() => setOpen((v) => !v)}
        className="p-2 text-slate-500 hover:bg-slate-50 rounded-full transition-colors"
        aria-label={t('language.select')}
        title={t('language.select')}
      >
        <span className="material-symbols-outlined" style={{ fontSize: '22px' }}>language</span>
      </button>

      {/* Dropdown popup */}
      {open && (
        <div className="absolute right-0 top-full mt-2 w-44 bg-white rounded-xl shadow-lg border border-slate-100 overflow-hidden z-50">
          <p className="px-4 py-2 text-[10px] font-bold uppercase tracking-widest text-slate-400 border-b border-slate-100">
            {t('language.select')}
          </p>
          {LANGUAGES.map((lang) => {
            const isActive = currentLang === lang.code
            return (
              <button
                key={lang.code}
                onClick={() => selectLanguage(lang.code)}
                className={`w-full flex items-center gap-3 px-4 py-3 text-sm font-medium transition-colors hover:bg-slate-50 ${
                  isActive ? 'text-[#0A192F] bg-slate-50' : 'text-slate-600'
                }`}
              >
                {lang.flag}
                <span>{lang.label}</span>
                {isActive && (
                  <span className="material-symbols-outlined ml-auto text-[#0A192F]" style={{ fontSize: '16px' }}>
                    check
                  </span>
                )}
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default LanguageSwitcher
