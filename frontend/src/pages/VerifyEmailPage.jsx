import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

function VerifyEmailPage() {
  const { token } = useParams()
  const [status, setStatus] = useState('loading') // 'loading' | 'success' | 'error'
  const [message, setMessage] = useState('')

  useEffect(() => {
    if (!token) {
      setStatus('error')
      setMessage('Token de verificación no encontrado en la URL.')
      return
    }

    fetch(`/api/v1/auth/verify/${token}`)
      .then(async (res) => {
        const data = await res.json().catch(() => ({}))
        if (res.ok) {
          setStatus('success')
          setMessage(data.message || 'Cuenta verificada correctamente.')
        } else {
          setStatus('error')
          setMessage(data.detail || 'El enlace es inválido o ha caducado.')
        }
      })
      .catch(() => {
        setStatus('error')
        setMessage('No se pudo conectar con el servidor.')
      })
  }, [token])

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
          <div className="bg-surface-container-lowest p-10 md:p-12 rounded-2xl shadow-[0_32px_64px_-12px_rgba(13,28,50,0.12)] border border-outline-variant/30 text-center">
            {status === 'loading' && (
              <>
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <span className="material-symbols-outlined text-blue-600 text-3xl animate-spin">
                    progress_activity
                  </span>
                </div>
                <h1 className="text-2xl font-extrabold text-primary-container mb-3">
                  Verificando cuenta...
                </h1>
                <p className="text-on-surface-variant">Por favor espera un momento.</p>
              </>
            )}

            {status === 'success' && (
              <>
                <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <span className="material-symbols-outlined text-emerald-600 text-3xl">
                    verified
                  </span>
                </div>
                <h1 className="text-2xl font-extrabold text-primary-container mb-3">
                  ¡Cuenta verificada!
                </h1>
                <p className="text-on-surface-variant mb-8">{message}</p>
                <Link
                  to="/login"
                  className="inline-flex items-center gap-2 bg-primary-container text-on-primary font-bold px-6 py-3 rounded-xl hover:opacity-90 transition-all"
                >
                  Iniciar sesión
                  <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
                </Link>
              </>
            )}

            {status === 'error' && (
              <>
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <span className="material-symbols-outlined text-red-600 text-3xl">
                    error
                  </span>
                </div>
                <h1 className="text-2xl font-extrabold text-primary-container mb-3">
                  Enlace no válido
                </h1>
                <p className="text-on-surface-variant mb-8">{message}</p>
                <Link
                  to="/login"
                  className="text-primary-container font-bold hover:underline"
                >
                  ← Volver al inicio de sesión
                </Link>
              </>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

export default VerifyEmailPage
