const badgeStyles = {
  emerald:
    'text-emerald-600 bg-emerald-50 border-emerald-100 uppercase tracking-widest',
  red: 'text-red-600 bg-red-50 border-red-100 uppercase tracking-widest',
}

function StatCard({ title, value, unit, icon, badge, badgeTone, cardAccent }) {
  const accentClasses =
    cardAccent === 'critical'
      ? 'border-l-4 border-l-red-500'
      : 'border border-slate-200'

  return (
    <div
      className={`bg-white p-6 rounded-xl ${accentClasses} shadow-sm transition-shadow hover:shadow-md`}
    >
      <div className="flex justify-between items-start mb-4">
        <div className="p-2 bg-slate-50 rounded-lg text-slate-600">
          <span className="material-symbols-outlined text-xl">{icon}</span>
        </div>
        {badge ? (
          <span
            className={`text-[10px] font-bold px-2 py-1 rounded-md border ${
              badgeTone ? badgeStyles[badgeTone] : ''
            }`}
          >
            {badge}
          </span>
        ) : null}
      </div>
      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">
        {title}
      </p>
      <h3
        className={`text-2xl font-black headline-font ${
          cardAccent === 'critical' ? 'text-red-600' : 'text-slate-900'
        }`}
      >
        {value}
        {unit ? (
          <span className="text-sm font-medium text-slate-400"> {unit}</span>
        ) : null}
      </h3>
    </div>
  )
}

export default StatCard
