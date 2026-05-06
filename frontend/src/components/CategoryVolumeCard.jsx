import { useTranslation } from 'react-i18next'

function CategoryVolumeCard({ categories, loading }) {
  const { t } = useTranslation()
  return (
    <section className="bg-slate-900 text-white p-8 rounded-xl shadow-xl flex-1 ring-1 ring-white/10">
      <h2 className="text-sm font-black headline-font uppercase tracking-[0.2em] mb-8 border-b border-white/10 pb-4">
        {t('dashboard.volumeByCategory')}
      </h2>

      {loading ? (
        <div className="space-y-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="space-y-2">
              <div className="h-3 bg-white/10 rounded animate-pulse w-3/4" />
              <div className="w-full bg-white/10 h-1.5 rounded-full" />
            </div>
          ))}
        </div>
      ) : categories.length === 0 ? (
        <p className="text-slate-500 text-xs uppercase tracking-widest text-center py-8">
          {t('dashboard.noData')}
        </p>
      ) : (
        <div className="space-y-6">
          {categories.map((category) => (
            <div key={category.id} className="space-y-2">
              <div className="flex justify-between text-[10px] font-bold tracking-widest uppercase">
                <span className="text-slate-400 truncate max-w-[70%]">{category.label}</span>
                <span>{category.value}%</span>
              </div>
              <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden">
                <div
                  className={`${category.color} h-full rounded-full transition-all duration-500`}
                  style={{ width: `${category.value}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}

export default CategoryVolumeCard
