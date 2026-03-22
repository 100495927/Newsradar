function CategoryVolumeCard({ categories }) {
  return (
    <section className="bg-slate-900 text-white p-8 rounded-xl shadow-xl flex-1 ring-1 ring-white/10">
      <h2 className="text-sm font-black headline-font uppercase tracking-[0.2em] mb-8 border-b border-white/10 pb-4">
        Volumen por Categoría
      </h2>
      <div className="space-y-6">
        {categories.map((category) => (
          <div key={category.id} className="space-y-2">
            <div className="flex justify-between text-[10px] font-bold tracking-widest uppercase">
              <span className="text-slate-400">{category.label}</span>
              <span>{category.value}%</span>
            </div>
            <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden">
              <div
                className={`${category.color} h-full`}
                style={{ width: `${category.value}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
          </section>
  )
}

export default CategoryVolumeCard
