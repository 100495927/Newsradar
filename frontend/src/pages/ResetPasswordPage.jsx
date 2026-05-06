import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')

  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (newPassword !== confirmPassword) {
      setError('Las contraseñas no coinciden.')
      return
    }
    if (newPassword.length < 6) {
      setError('La contraseña debe tener al menos 6 caracteres.')
      return
    }

    setLoading(true)
    try {
      const params = new URLSearchParams({ token, new_password: newPassword })
      const res = await fetch(`/api/v1/auth/reset-password?${params}`, {
        method: 'POST',
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) {
        throw new Error(data.detail || 'Error al restablecer la contraseña.')
      }
      setDone(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (!token) {
    return (
      <div className="bg-[#f0f2f5] min-h-screen flex items-center justify-center p-6">
        <div className="bg-surface-container-lowest p-10 rounded-2xl shadow-[0_32px_64px_-12px_rgba(13,28,50,0.12)] border border-outline-variant/30 text-center max-w-[440px] w-full">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <span className="material-symbols-outlined text-red-600 text-3xl">link_off</span>
          </div>
          <h1 className="text-2xl font-extrabold text-primary-container mb-3">Enlace no válido</h1>
          <p className="text-on-surface-variant mb-8">
            Este enlace de recuperación no contiene un token válido.
          </p>
          <Link to="/forgot-password" className="text-primary-container font-bold hover:underline">
            Solicitar un nuevo enlace
          </Link>
        </div>
      </div>
    )
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
            {done ? (
              <div className="text-center">
                <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <span className="material-symbols-outlined text-emerald-600 text-3xl">
                    lock_reset
                  </span>
                </div>
                <h1 className="text-2xl font-extrabold text-primary-container mb-3">
                  Contraseña actualizada
                </h1>
                <p className="text-on-surface-variant mb-8">
                  Tu contraseña se ha restablecido correctamente. Ya puedes iniciar sesión.
                </p>
                <Link
                  to="/login"
                  className="inline-flex items-center gap-2 bg-primary-container text-on-primary font-bold px-6 py-3 rounded-xl hover:opacity-90 transition-all"
                >
                  Iniciar sesión
                  <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
                </Link>
              </div>
            ) : (
              <>
                <div className="mb-10">
                  <h1 className="headline-font text-3xl font-extrabold text-primary-container tracking-tight mb-3">
                    Nueva contraseña
                  </h1>
                  <p className="text-on-surface-variant text-base font-medium">
                    Introduce y confirma tu nueva contraseña.
                  </p>
                </div>

                <form className="space-y-7" onSubmit={handleSubmit}>
                  <div className="space-y-2.5">
                    <label className="block text-xs font-bold uppercase tracking-[0.15em] text-on-surface-variant/80">
                      Nueva contraseña
                    </label>
                    <input
                      className="w-full bg-surface-container-low border border-outline-variant/40 rounded-xl px-5 py-4 text-sm font-medium"
                      placeholder="Mínimo 6 caracteres"
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      minLength={6}
                      required
                    />
                  </div>

                  <div className="space-y-2.5">
                    <label className="block text-xs font-bold uppercase tracking-[0.15em] text-on-surface-variant/80">
                      Confirmar contraseña
                    </label>
                    <input
                      className="w-full bg-surface-container-low border border-outline-variant/40 rounded-xl px-5 py-4 text-sm font-medium"
                      placeholder="Repite la contraseña"
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      minLength={6}
                      required
                    />
                  </div>

                  {error && <p className="text-red-500 text-sm font-medium">{error}</p>}

                  <button
                    className="w-full bg-primary-container text-on-primary font-bold py-4 rounded-xl shadow-lg hover:shadow-xl hover:bg-black active:scale-[0.98] transition-all flex justify-center items-center gap-2.5 h-14 disabled:opacity-60"
                    type="submit"
                    disabled={loading}
                  >
                    {loading ? 'Guardando...' : 'Establecer nueva contraseña'}
                  </button>
                </form>

                <div className="mt-10 pt-8 border-t border-outline-variant/20 text-center">
                  <Link to="/login" className="text-sm text-primary-container font-bold hover:underline">
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

export default ResetPasswordPage
