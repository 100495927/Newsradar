import { useTranslation } from 'react-i18next'

function TrendChart({ data, loading }) {
  const { t } = useTranslation()
  const maxVal = data.length > 0 ? Math.max(...data.map((d) => d.total)) : 1

  const bars = data.slice(-30)

  // X-axis labels: show first, middle and last date only
  const firstLabel = bars[0]?.fecha?.slice(5) ?? ''
  const midLabel = bars[Math.floor(bars.length / 2)]?.fecha?.slice(5) ?? ''
  const lastLabel = bars[bars.length - 1]?.fecha?.slice(5) ?? ''

  const W = 800
  const H = 320
  const PAD = { top: 16, right: 16, bottom: 8, left: 8 }

  const toX = (i) => PAD.left + (i / (bars.length - 1 || 1)) * (W - PAD.left - PAD.right)
  const toY = (val) => PAD.top + (1 - val / maxVal) * (H - PAD.top - PAD.bottom)

  const points = bars.map((d, i) => `${toX(i)},${toY(d.total)}`).join(' ')
  const areaPoints = [
    `${toX(0)},${H - PAD.bottom}`,
    ...bars.map((d, i) => `${toX(i)},${toY(d.total)}`),
    `${toX(bars.length - 1)},${H - PAD.bottom}`,
  ].join(' ')

  return (
    <section className="lg:col-span-8 bg-white p-8 rounded-xl border border-slate-200 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-10 gap-4">
        <div>
          <h2 className="text-lg font-extrabold headline-font text-slate-900 uppercase tracking-tight">
            {t('dashboard.chartTitle')}
          </h2>
          <p className="text-xs text-slate-500 font-medium">
            {t('dashboard.chartSubtitle')}
          </p>
        </div>
      </div>

      {loading ? (
        <div className="h-[320px] bg-slate-50 rounded-lg animate-pulse" />
      ) : bars.length === 0 ? (
        <div className="h-[320px] flex items-center justify-center text-slate-400 text-sm font-medium uppercase tracking-widest">
          {t('dashboard.noCapture')}
        </div>
      ) : (
        <>
          <svg
            viewBox={`0 0 ${W} ${H}`}
            className="w-full h-[320px] border-l border-b border-slate-200"
            preserveAspectRatio="none"
          >
            <defs>
              <linearGradient id="lineArea" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#1e293b" stopOpacity="0.15" />
                <stop offset="100%" stopColor="#1e293b" stopOpacity="0" />
              </linearGradient>
            </defs>
            <polygon points={areaPoints} fill="url(#lineArea)" />
            <polyline
              points={points}
              fill="none"
              stroke="#1e293b"
              strokeWidth="2"
              strokeLinejoin="round"
              strokeLinecap="round"
            />
            {bars.map((d, i) => (
              <circle
                key={d.fecha}
                cx={toX(i)}
                cy={toY(d.total)}
                r="3"
                fill={d.total === maxVal ? '#0f172a' : '#64748b'}
                stroke="white"
                strokeWidth="1.5"
              >
                <title>{t('dashboard.newsTooltip', { date: d.fecha, count: d.total.toLocaleString() })}</title>
              </circle>
            ))}
          </svg>
          <div className="flex justify-between mt-4 text-[10px] font-black text-slate-400 uppercase tracking-[0.15em]">
            <span>{firstLabel}</span>
            <span>{midLabel}</span>
            <span>{lastLabel}</span>
          </div>
        </>
      )}
    </section>
  )
}

export default TrendChart
