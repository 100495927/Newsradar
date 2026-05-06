import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function LoginPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [toastVisible, setToastVisible] = useState(searchParams.get('registered') === 'true')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-[#f0f2f5] min-h-screen flex flex-col relative overflow-hidden">
      {toastVisible && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-[100] w-full max-w-md px-4">
          <div className="flex items-start gap-3 bg-emerald-50 border border-emerald-300 text-emerald-800 rounded-xl px-5 py-4 shadow-lg">
            <span className="material-symbols-outlined text-emerald-600 text-xl mt-0.5 shrink-0">mark_email_read</span>
            <div className="flex-1 text-sm font-medium">
              Cuenta creada correctamente. Revisa tu bandeja de entrada y haz clic en el enlace de verificación (válido 24 h).
            </div>
            <button
              onClick={() => setToastVisible(false)}
              className="text-emerald-600 hover:text-emerald-800 shrink-0 ml-1"
              aria-label="Cerrar"
            >
              <span className="material-symbols-outlined text-lg">close</span>
            </button>
          </div>
        </div>
      )}
      <header className="fixed top-0 left-0 w-full z-50 flex justify-start items-center px-8 h-20 bg-transparent">
        <div className="flex items-center gap-2.5">
          <div className="bg-primary-container p-1.5 rounded-lg shadow-sm">
            <span className="material-symbols-outlined text-on-primary text-xl">
              radar
            </span>
          </div>
          <span className="text-xl font-extrabold tracking-tighter text-primary-container headline-font">
            NewsRadar
          </span>
        </div>
      </header>
      <main className="flex-grow flex items-center justify-center p-6 z-10">
        <div className="w-full max-w-[440px]">
          <div className="bg-surface-container-lowest p-10 md:p-12 rounded-2xl shadow-[0_32px_64px_-12px_rgba(13,28,50,0.12)] border border-outline-variant/30 backdrop-blur-sm bg-opacity-95">
            <div className="mb-12">
              <h1 className="headline-font text-4xl font-extrabold text-primary-container tracking-tight mb-3">
                El Lente Informado
              </h1>
              <p className="text-on-surface-variant text-base font-medium">
                Accede a tu panel de inteligencia
              </p>
            </div>
            <form className="space-y-7" onSubmit={handleSubmit}>
              <div className="space-y-2.5">
                <label className="block text-xs font-bold uppercase tracking-[0.15em] text-on-surface-variant/80 font-label">
                  Usuario
                </label>
                <input
                  className="w-full bg-surface-container-low border border-outline-variant/40 rounded-xl px-5 py-4 text-sm font-medium"
                  placeholder="nombre@newsradar.com"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2.5">
                <div className="flex justify-between items-center">
                  <label className="block text-xs font-bold uppercase tracking-[0.15em] text-on-surface-variant/80 font-label">
                    Contraseña
                  </label>
                  <Link
                    to="/forgot-password"
                    className="text-xs text-primary-container font-medium hover:underline"
                  >
                    ¿Olvidaste tu contraseña?
                  </Link>
                </div>
                <input
                  className="w-full bg-surface-container-low border border-outline-variant/40 rounded-xl px-5 py-4 text-sm font-medium"
                  placeholder="••••••••"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              {error && (
                <p className="text-red-500 text-sm font-medium">{error}</p>
              )}
              <button
                className="w-full bg-primary-container text-on-primary font-bold py-4 rounded-xl shadow-lg hover:shadow-xl hover:bg-black active:scale-[0.98] transition-all flex justify-center items-center gap-2.5 group h-14 disabled:opacity-60"
                type="submit"
                disabled={loading}
              >
                <span>{loading ? 'Iniciando...' : 'Iniciar Sesión'}</span>
                {!loading && (
                  <span className="material-symbols-outlined text-xl transition-transform group-hover:translate-x-1">
                    arrow_forward
                  </span>
                )}
              </button>
            </form>
            <div className="mt-10 pt-8 border-t border-outline-variant/20 text-center">
              <p className="text-sm text-on-surface-variant font-medium">
                ¿No tienes cuenta?{' '}
                <Link
                  className="text-primary-container font-bold hover:underline"
                  to="/register"
                >
                  Solicitar acceso
                </Link>
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default LoginPage
