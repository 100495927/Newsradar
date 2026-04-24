import { useEffect, useState } from 'react'
import TopNavBar from '../components/TopNavBar'
import SideNavBar from '../components/SideNavBar'
import MobileNav from '../components/MobileNav'
import { getGlobalStats, getWordCloud } from '../api/apiClient'

const CATEGORY_COLORS = [
  'text-blue-700 bg-blue-50 border-blue-200',
  'text-emerald-700 bg-emerald-50 border-emerald-200',
  'text-violet-700 bg-violet-50 border-violet-200',
  'text-amber-700 bg-amber-50 border-amber-200',
  'text-rose-700 bg-rose-50 border-rose-200',
  'text-cyan-700 bg-cyan-50 border-cyan-200',
  'text-orange-700 bg-orange-50 border-orange-200',
  'text-slate-700 bg-slate-50 border-slate-200',
]

function scaleFont(value, min, max) {
  if (max === min) return 1.2
  return 0.75 + ((value - min) / (max - min)) * 1.75
}

function WordCloudDisplay({ words }) {
  if (words.length === 0) return null
  const values = words.map((w) => w.value)
  const min = Math.min(...values)
  const max = Math.max(...values)

  return (
    <div className="flex flex-wrap justify-center items-center gap-x-5 gap-y-4 py-4 px-2">
      {words.map((item, i) => {
        const size = scaleFont(item.value, min, max)
        // Opacity decreases slightly for smaller words
        const opacity = 0.45 + ((item.value - min) / (max - min || 1)) * 0.55
        // Alternate between dark navy and slate tones based on rank
        const color =
          i === 0
            ? '#0A192F'
            : i < 4
              ? '#1e3a5f'
              : i < 10
                ? '#334155'
                : '#64748b'
        return (
          <span
            key={item.word}
            className="font-black uppercase tracking-tight cursor-default select-none transition-all duration-200 hover:scale-110 hover:text-[#0A192F]"
            style={{ fontSize: `${size}rem`, color, opacity }}
            title={`${item.value} apariciones`}
          >
            {item.word}
          </span>
        )
      })}
    </div>
  )
}

function SummaryPage() {
  const [categories, setCategories] = useState([])
  const [cloudByCategory, setCloudByCategory] = useState({})
  const [combinedCloud, setCombinedCloud] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getGlobalStats()
      .then(async (global) => {
        const topCats = global.noticias_por_categoria.slice(0, 8)
        setCategories(topCats)

        if (topCats.length === 0) return

        const results = await Promise.all(
          topCats.map((cat) =>
            getWordCloud(cat.id).catch(() => [])
          )
        )

        const byCategory = {}
        topCats.forEach((cat, i) => {
          byCategory[cat.id] = results[i]
        })
        setCloudByCategory(byCategory)

        // Merge all words summing values across categories
        const merged = {}
        results.flat().forEach(({ word, value }) => {
          merged[word] = (merged[word] || 0) + value
        })
        const sorted = Object.entries(merged)
          .map(([word, value]) => ({ word, value }))
          .sort((a, b) => b.value - a.value)
          .slice(0, 20)
        setCombinedCloud(sorted)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="bg-background min-h-screen">
      <TopNavBar />
      <SideNavBar />
      <main className="lg:ml-64 pt-20 px-8 pb-16">
        <div className="max-w-6xl mx-auto space-y-12">

          {/* Header */}
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-slate-200 pb-8">
            <div>
              <h1 className="text-3xl font-extrabold font-headline tracking-tight text-slate-950 uppercase italic">
                Resumen de Inteligencia
              </h1>
              <p className="text-slate-500 mt-2 text-sm font-medium">
                Temas más candentes por categoría extraídos de los canales RSS monitorizados.
              </p>
            </div>
          </div>

          {loading ? (
            <div className="space-y-8">
              <div className="bg-white border border-slate-200 rounded-xl p-8 animate-pulse h-64" />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="bg-white border border-slate-200 rounded-xl p-6 animate-pulse h-48" />
                ))}
              </div>
            </div>
          ) : combinedCloud.length === 0 ? (
            <div className="bg-white border border-slate-200 rounded-xl p-16 text-center">
              <span className="material-symbols-outlined text-4xl text-slate-300">cloud_off</span>
              <p className="mt-4 text-slate-400 font-medium uppercase tracking-widest text-xs">
                No hay noticias procesadas todavía
              </p>
            </div>
          ) : (
            <>
              {/* Combined word cloud */}
              <section className="bg-white border border-slate-200 shadow-sm rounded-xl overflow-hidden">
                <div className="bg-[#0A192F] px-6 py-4">
                  <h2 className="text-white text-xs font-black uppercase tracking-[0.2em]">
                    Nube Global de Palabras Clave
                  </h2>
                  <p className="text-slate-400 text-[10px] mt-1 uppercase tracking-wider">
                    Todas las categorías · top 80 términos
                  </p>
                </div>
                <div className="p-8">
                  <WordCloudDisplay words={combinedCloud} />
                </div>
              </section>

              {/* Per-category keyword rankings */}
              <section>
                <h2 className="text-xs font-black text-slate-400 uppercase tracking-[0.2em] mb-6">
                  Palabras Clave por Categoría
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {categories.map((cat, i) => {
                    const words = cloudByCategory[cat.id] ?? []
                    const colorClass = CATEGORY_COLORS[i % CATEGORY_COLORS.length]
                    return (
                      <div
                        key={cat.id}
                        className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm"
                      >
                        <div className="px-5 py-3 border-b border-slate-100 flex items-center justify-between">
                          <h3 className="font-black text-xs uppercase tracking-widest text-slate-800">
                            {cat.id}
                          </h3>
                          <span className="text-[10px] font-bold text-slate-400">
                            {cat.total.toLocaleString('es-ES')} noticias
                          </span>
                        </div>
                        {words.length === 0 ? (
                          <p className="px-5 py-6 text-slate-400 text-xs text-center uppercase tracking-widest">
                            Sin datos
                          </p>
                        ) : (
                          <ol className="px-5 py-4 space-y-2">
                            {words.slice(0, 10).map((item, rank) => (
                              <li key={item.word} className="flex items-center justify-between gap-3">
                                <div className="flex items-center gap-3">
                                  <span className="text-[10px] font-black text-slate-300 w-4 text-right">
                                    {rank + 1}
                                  </span>
                                  <span
                                    className={`px-2 py-0.5 rounded border text-[11px] font-bold uppercase tracking-wide ${colorClass}`}
                                  >
                                    {item.word}
                                  </span>
                                </div>
                                <span className="text-[10px] text-slate-400 font-mono">
                                  {item.value}×
                                </span>
                              </li>
                            ))}
                          </ol>
                        )}
                      </div>
                    )
                  })}
                </div>
              </section>
            </>
          )}
        </div>
      </main>
      <MobileNav />
    </div>
  )
}

export default SummaryPage
