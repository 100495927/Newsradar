import { Link, useNavigate } from 'react-router-dom'

function RegisterPage() {
  const navigate = useNavigate()

  const handleSubmit = (e) => {
    e.preventDefault()
    navigate('/login')
  }

  return (
    <div className="bg-surface font-body text-on-surface min-h-screen flex items-center justify-center p-4">
      <div className="max-w-6xl w-full grid grid-cols-1 lg:grid-cols-12 gap-0 overflow-hidden rounded-xl editorial-shadow bg-surface-container-lowest">
        <div className="lg:col-span-5 relative hidden lg:flex flex-col justify-between p-12 bg-primary-container text-white overflow-hidden">
          <div
            className="absolute inset-0 opacity-20 pointer-events-none"
            style={{
              backgroundImage:
                'radial-gradient(circle at 0% 0%, #39475f 0%, transparent 70%), linear-gradient(135deg, #0d1c32 0%, #000000 100%)',
            }}
          ></div>
          <div className="relative z-10">
            <div className="text-2xl font-extrabold font-headline tracking-tighter mb-2">
              NewsRadar
            </div>
            <div className="h-1 w-12 bg-secondary mb-12"></div>
            <h1 className="text-4xl font-headline font-bold leading-tight tracking-tight mb-6">
              El lente informado para la inteligencia global.
            </h1>
            <p className="text-on-primary-container text-lg leading-relaxed max-w-sm">
              Accede a análisis editoriales profundos y alertas de noticias en
              tiempo real impulsadas por procesamiento neuronal.
            </p>
          </div>
          <div className="relative z-10 space-y-8">
            <div className="flex items-start gap-4">
              <div className="bg-surface-container-high/10 p-2 rounded-lg">
                <span className="material-symbols-outlined text-tertiary-fixed">
                  auto_stories
                </span>
              </div>
              <div>
                <div className="font-bold font-headline">Precisión Editorial</div>
                <div className="text-sm text-on-primary-container">
                  Información curada que filtra el ruido de la señal.
                </div>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <div className="bg-surface-container-high/10 p-2 rounded-lg">
                <span className="material-symbols-outlined text-secondary-fixed">
                  notifications_active
                </span>
              </div>
              <div>
                <div className="font-bold font-headline">Conciencia Instantánea</div>
                <div className="text-sm text-on-primary-container">
                  Sé el primero en ver los cambios globales mientras ocurren.
                </div>
              </div>
            </div>
          </div>
          <div className="relative z-10 mt-12 pt-8 border-t border-white/10 flex items-center justify-between">
            <span className="text-xs uppercase tracking-widest text-on-primary-container">
              © 2026 Inteligencia NewsRadar
            </span>
          </div>
        </div>
        <div className="lg:col-span-7 p-8 md:p-16 flex flex-col justify-center">
          <div className="max-w-md mx-auto w-full">
            <div className="mb-10">
              <h2 className="text-3xl font-headline font-extrabold text-primary-container tracking-tight mb-2">
                Crea tu cuenta
              </h2>
              <p className="text-on-surface-variant font-medium">
                Únete a nuestra red de analistas profesionales.
              </p>
            </div>
            <form className="space-y-6" onSubmit={handleSubmit}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="block text-xs font-bold uppercase tracking-widest text-on-surface-variant px-1">
                    Nombre
                  </label>
                  <input
                    className="w-full px-4 py-3 rounded-lg bg-surface-container-low border-none focus:ring-2 focus:ring-surface-tint font-medium"
                    placeholder="Jane"
                    type="text"
                  />
                </div>
                <div className="space-y-2">
                  <label className="block text-xs font-bold uppercase tracking-widest text-on-surface-variant px-1">
                    Apellidos
                  </label>
                  <input
                    className="w-full px-4 py-3 rounded-lg bg-surface-container-low border-none focus:ring-2 focus:ring-surface-tint font-medium"
                    placeholder="Doe"
                    type="text"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <label className="block text-xs font-bold uppercase tracking-widest text-on-surface-variant px-1">
                  Correo Electrónico
                </label>
                <input
                  className="w-full px-4 py-3 rounded-lg bg-surface-container-low border-none focus:ring-2 focus:ring-surface-tint font-medium"
                  placeholder="jane.doe@organizacion.com"
                  type="email"
                />
              </div>
              <div className="pt-4">
                <button className="w-full py-4 bg-primary-container text-on-primary font-headline font-bold rounded-lg shadow-lg hover:opacity-90 active:scale-[0.98] transition-all flex items-center justify-center gap-2">
                  Registrarse{' '}
                  <span className="material-symbols-outlined text-[18px]">
                    arrow_forward
                  </span>
                </button>
              </div>
            </form>
            <div className="mt-8 text-center">
              <p className="text-sm text-on-surface-variant">
                ¿Ya tienes una cuenta?{' '}
                <Link
                  className="text-primary-container font-bold hover:underline"
                  to="/login"
                >
                  Inicia sesión en NewsRadar
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RegisterPage
