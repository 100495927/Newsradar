import { useTranslation } from 'react-i18next'

function PageHeader() {
  const { t } = useTranslation()

  return (
    <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
      <div className="space-y-1">
        <h1 className="text-3xl font-black headline-font tracking-tight text-slate-900">
          {t('pageHeader.title')}
        </h1>
        <p className="text-slate-500 font-medium text-sm">
          {t('pageHeader.subtitle')}
        </p>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-100 rounded-lg border border-slate-200">
          <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
          <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
            {t('pageHeader.statusActive')}
          </span>
        </div>
        <div className="text-right">
          <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">
            {t('pageHeader.lastUpdate')}
          </p>
          <p className="text-sm text-slate-900 font-mono font-bold">
            {t('pageHeader.lastUpdateValue')}
          </p>
        </div>
      </div>
    </div>
  )
}

export default PageHeader
