const bars = [
  40, 45, 60, 85, 70, 95, 100, 80, 65, 50, 40, 35,
]

function TrendChart() {
  return (
    <section className="lg:col-span-8 bg-white p-8 rounded-xl border border-slate-200 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-10 gap-4">
        <div>
          <h2 className="text-lg font-extrabold headline-font text-slate-900 uppercase tracking-tight">
            Evolución de Captura Temporal
          </h2>
          <p className="text-xs text-slate-500 font-medium">
            Volumen histórico de noticias (Ventana 24h)
          </p>
        </div>
        <div className="flex bg-slate-100 p-1 rounded-lg">
          {['24H', '7D', '30D'].map((label, index) => (
            <button
              key={label}
              className={`px-4 py-1.5 text-[10px] font-black uppercase tracking-wider ${
                index === 0
                  ? 'bg-white shadow-sm text-slate-900 rounded-md'
                  : 'text-slate-500 hover:text-slate-900 transition-colors'
              }`}
              type="button"
            >
              {label}
            </button>
          ))}
        </div>
      </div>
      <div className="relative h-[320px] w-full chart-grid border-l border-b border-slate-200">
        <div className="absolute bottom-0 left-0 w-full h-full flex items-end px-4 gap-2">
          {bars.map((height, index) => (
            <div
              key={`${height}-${index}`}
              className={`flex-1 rounded-t transition-all ${
                index === 6
                  ? 'bg-slate-900 hover:bg-black'
                  : index === 3 || index === 7
                    ? 'bg-slate-300 hover:bg-slate-400'
                    : index === 11
                      ? 'bg-slate-100 hover:bg-slate-200'
                      : 'bg-slate-200/60 hover:bg-slate-300'
              }`}
              style={{ height: `${height}%` }}
            ></div>
          ))}
        </div>
        <svg
          className="absolute top-0 left-0 w-full h-full pointer-events-none"
          preserveAspectRatio="none"
          viewBox="0 0 1000 320"
          aria-hidden="true"
        >
          <path
            d="M 0 200 Q 150 160 300 100 T 600 20 T 900 120 L 1000 140"
            fill="none"
            opacity="0.3"
            stroke="#0f172a"
            strokeDasharray="4"
            strokeWidth="1.5"
          />
        </svg>
      </div>
      <div className="flex justify-between mt-6 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">
        <span>00:00</span>
        <span>06:00</span>
        <span>12:00</span>
        <span>18:00</span>
        <span>23:59</span>
      </div>
    </section>
  )
}

export default TrendChart
