function TrendChart({ data, loading }) {
  const maxVal = data.length > 0 ? Math.max(...data.map((d) => d.total)) : 1

  // Show at most 30 bars; if fewer, pad with nulls so bars have consistent width
  const bars = data.slice(-30)

  // X-axis labels: show first, middle and last date only
  const firstLabel = bars[0]?.fecha?.slice(5) ?? ''
  const midLabel = bars[Math.floor(bars.length / 2)]?.fecha?.slice(5) ?? ''
  const lastLabel = bars[bars.length - 1]?.fecha?.slice(5) ?? ''

  return (
    <section className="lg:col-span-8 bg-white p-8 rounded-xl border border-slate-200 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-10 gap-4">
        <div>
          <h2 className="text-lg font-extrabold headline-font text-slate-900 uppercase tracking-tight">
            Noticias Capturadas por Día
          </h2>
          <p className="text-xs text-slate-500 font-medium">
            Volumen de ingesta diaria (últimos 30 días)
          </p>
        </div>
      </div>

      {loading ? (
        <div className="h-[320px] bg-slate-50 rounded-lg animate-pulse" />
      ) : bars.length === 0 ? (
        <div className="h-[320px] flex items-center justify-center text-slate-400 text-sm font-medium uppercase tracking-widest">
          Sin datos de captura disponibles
        </div>
      ) : (
        <>
          <div className="relative h-[320px] w-full border-l border-b border-slate-200">
            <div className="absolute bottom-0 left-0 w-full h-full flex items-end px-2 gap-1">
              {bars.map((entry, index) => {
                const heightPct = Math.round((entry.total / maxVal) * 100)
                const isMax = entry.total === maxVal
                return (
                  <div
                    key={entry.fecha}
                    title={`${entry.fecha}: ${entry.total.toLocaleString('es-ES')} noticias`}
                    className={`flex-1 rounded-t transition-all cursor-default ${
                      isMax
                        ? 'bg-slate-900 hover:bg-black'
                        : index % 7 === 0
                          ? 'bg-slate-300 hover:bg-slate-400'
                          : 'bg-slate-200/70 hover:bg-slate-300'
                    }`}
                    style={{ height: `${heightPct}%` }}
                  />
                )
              })}
            </div>
          </div>
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
