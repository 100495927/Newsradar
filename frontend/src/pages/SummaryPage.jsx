import TopNavBar from '../components/TopNavBar'
import SideNavBar from '../components/SideNavBar'
import MobileNav from '../components/MobileNav'

const signals = [
  { n: '01', t: 'Presión Inflacionaria', v: '+42%' },
  { n: '02', t: 'Mandatos Sostenibles', v: '+28%' },
]

const secondarySignals = [
  'Regulación IA',
  'Computación Cuántica',
  'Transición Energética',
  'Ciberseguridad',
  'Cadena Suministro',
]

function SummaryPage() {
  return (
    <div className="bg-background min-h-screen">
      <TopNavBar />
      <SideNavBar />
      <main className="lg:ml-64 pt-20 px-8 pb-16">
        <div className="max-w-6xl mx-auto space-y-12">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-slate-200 pb-8">
            <div>
              <h1 className="text-3xl font-extrabold font-headline tracking-tight text-slate-950 uppercase italic">
                Resumen de Inteligencia
              </h1>
              <p className="text-slate-500 mt-2 text-sm font-medium">
                Señales técnicas y de mercado consolidadas para el 24 de noviembre.
              </p>
            </div>
            <div className="flex items-center bg-slate-100 border border-slate-200 p-0.5 rounded-lg">
              <button className="px-4 py-1.5 bg-white text-[#0A192F] font-bold text-[10px] uppercase shadow-sm rounded-md">
                24h
              </button>
              <button className="px-4 py-1.5 text-slate-500 font-bold text-[10px] uppercase">
                7d
              </button>
            </div>
          </div>

          <section className="bg-white border border-slate-200 shadow-sm overflow-hidden rounded-xl">
            <div className="bg-[#0A192F] px-6 py-4 flex justify-between items-center">
              <h2 className="text-white text-xs font-black uppercase tracking-[0.2em]">
                Índice de Señales Macroglobales
              </h2>
              <span className="text-slate-400 text-[10px] font-bold uppercase">
                Actualizado hace 2m
              </span>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2">
              <div className="p-8 border-r border-slate-100 bg-slate-50/30">
                <div className="space-y-4">
                  {signals.map((s) => (
                    <div
                      key={s.n}
                      className="flex items-center justify-between p-5 bg-white border border-slate-200 rounded-xl shadow-sm cursor-pointer hover:border-slate-400"
                    >
                      <div className="flex items-center gap-4">
                        <span className="text-3xl font-black text-[#0A192F]">
                          {s.n}
                        </span>
                        <div>
                          <h4 className="font-headline font-black text-slate-900 uppercase">
                            {s.t}
                          </h4>
                          <p className="text-[10px] text-slate-500 uppercase">
                            Impacto Global
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="text-xs font-black">{s.v}</span>
                        <div className="w-16 h-1 bg-slate-100 mt-1 rounded-full">
                          <div className="w-full h-full bg-[#0A192F]"></div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="p-8">
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-6">
                  Señales Secundarias
                </p>
                <div className="flex flex-wrap gap-2">
                  {secondarySignals.map((tag) => (
                    <span
                      key={tag}
                      className="px-3 py-1.5 border border-slate-200 rounded text-[#0A192F] text-xs font-bold uppercase hover:bg-slate-50 cursor-pointer"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </section>
        </div>
      </main>
      <MobileNav />
    </div>
  )
}

export default SummaryPage
