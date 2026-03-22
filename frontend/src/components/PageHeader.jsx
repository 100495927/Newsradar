function PageHeader() {
  return (
    <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
      <div className="space-y-1">
        <h1 className="text-3xl font-black headline-font tracking-tight text-slate-900">
          Resumen Global
        </h1>
        <p className="text-slate-500 font-medium text-sm">
          Extracción de inteligencia en tiempo real del panorama informativo
          mundial.
        </p>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-100 rounded-lg border border-slate-200">
          <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
          <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
            Sistema Activo
          </span>
        </div>
        <div className="text-right">
          <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">
            Última Actualización
          </p>
          <p className="text-sm text-slate-900 font-mono font-bold">
            hace 2 min
          </p>
        </div>
      </div>
    </div>
  )
}

export default PageHeader
