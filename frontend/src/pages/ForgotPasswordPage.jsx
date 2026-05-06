import { useState } from 'react'
import { Link } from 'react-router-dom'

function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const res = await fetch('/api/v1/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password: '' }),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || 'Error al enviar el correo')
      }
      setSent(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-[#f0f2f5] min-h-screen flex flex-col relative overflow-hidden">
      <header className="fixed top-0 left-0 w-full z-50 flex justify-start items-center px-8 h-20 bg-transparent">
        <div className="flex items-center gap-2.5">
          <div className="bg-primary-container p-1.5 rounded-lg shadow-sm">
            <span className="material-symbols-outlined text-on-primary text-xl">radar</span>
          </div>
          <span className="text-xl font-extrabold tracking-tighter text-primary-container headline-font">
            NewsRadar
          </span>
        </div>
      </header>

      <main className="flex-grow flex items-center justify-center p-6 z-10">
        <div className="w-full max-w-[440px]">
          <div className="bg-surface-container-lowest p-10 md:p-12 rounded-2xl shadow-[0_32px_64px_-12px_rgba(13,28,50,0.12)] border border-outline-variant/30 backdrop-blur-sm bg-opacity-95">
            {sent ? (
              <div className="text-center">
                <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <span className="material-symbols-outlined text-emerald-600 text-3xl">
                    mark_email_read
                  </span>
                </div>
                <h1 className="text-2xl font-extrabold text-primary-container mb-3">
                  Correo enviado
                </h1>
                <p className="text-on-surface-variant mb-8">
                  Si existe una cuenta con ese correo, recibirás un enlace para restablecer tu
                  contraseña en los próximos minutos.
                </p>
                <Link
                  to="/login"
                  className="text-primary-container font-bold hover:underline"
                >
                  ← Volver al inicio de sesión
                </Link>
              </div>
            ) : (
              <>
                <div className="mb-10">
                  <h1 className="headline-font text-3xl font-extrabold text-primary-container tracking-tight mb-3">
                    Recuperar contraseña
                  </h1>
                  <p className="text-on-surface-variant text-base font-medium">
                    Introduce tu correo y te enviaremos un enlace de recuperación.
                  </p>
                </div>

                <form className="space-y-7" onSubmit={handleSubmit}>
                  <div className="space-y-2.5">
                    <label className="block text-xs font-bold uppercase tracking-[0.15em] text-on-surface-variant/80 font-label">
                      Correo electrónico
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

                  {error && <p className="text-red-500 text-sm font-medium">{error}</p>}

                  <button
                    className="w-full bg-primary-container text-on-primary font-bold py-4 rounded-xl shadow-lg hover:shadow-xl hover:bg-black active:scale-[0.98] transition-all flex justify-center items-center gap-2.5 h-14 disabled:opacity-60"
                    type="submit"
                    disabled={loading}
                  >
                    {loading ? 'Enviando...' : 'Enviar enlace de recuperación'}
                  </button>
                </form>

                <div className="mt-10 pt-8 border-t border-outline-variant/20 text-center">
                  <Link
                    to="/login"
                    className="text-sm text-primary-container font-bold hover:underline"
                  >
                    ← Volver al inicio de sesión
                  </Link>
                </div>
              </>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

export default ForgotPasswordPage
