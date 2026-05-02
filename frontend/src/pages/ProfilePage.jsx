import { useState, useEffect, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import TopNavBar from '../components/TopNavBar'
import SideNavBar from '../components/SideNavBar'
import MobileNav from '../components/MobileNav'
import { useAuth } from '../context/AuthContext'
import { apiFetch } from '../api/apiClient'

function ProfilePage() {
  const { t } = useTranslation()
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', organization: '' })
  const [pwForm, setPwForm] = useState({ new_password: '', confirm_password: '' })
  const [roleName, setRoleName] = useState(null)

  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [showSuccessMessage, setShowSuccessMessage] = useState(false)
  const [saveError, setSaveError] = useState('')
  const [savingProfile, setSavingProfile] = useState(false)

  const [pwError, setPwError] = useState('')
  const [pwSuccess, setPwSuccess] = useState(false)
  const [savingPw, setSavingPw] = useState(false)

  const timeoutRef = useRef(null)

  useEffect(() => {
    return () => { if (timeoutRef.current) clearTimeout(timeoutRef.current) }
  }, [])

  useEffect(() => {
    if (!user?.id) return
    apiFetch(`/api/v1/users/${user.id}`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data) {
          setForm({
            first_name: data.first_name ?? '',
            last_name: data.last_name ?? '',
            email: data.email ?? '',
            organization: data.organization ?? '',
          })
          const role = data.roles?.[0]?.name ?? data.role ?? null
          setRoleName(role)
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [user?.id])

  const handleSave = async () => {
    setSaveError('')
    setSavingProfile(true)
    try {
      const res = await apiFetch(`/api/v1/users/${user.id}`, {
        method: 'PUT',
        body: JSON.stringify({
          first_name: form.first_name,
          last_name: form.last_name,
          email: form.email,
          organization: form.organization,
        }),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || t('profile.saveError', 'Error al guardar'))
      }
      setShowSuccessMessage(true)
      timeoutRef.current = setTimeout(() => setShowSuccessMessage(false), 3000)
    } catch (err) {
      setSaveError(err.message)
    } finally {
      setSavingProfile(false)
    }
  }

  const handleChangePassword = async (e) => {
    e.preventDefault()
    setPwError('')
    setPwSuccess(false)
    if (pwForm.new_password !== pwForm.confirm_password) {
      setPwError(t('profile.pwMismatch', 'Las contraseñas no coinciden'))
      return
    }
    if (pwForm.new_password.length < 6) {
      setPwError(t('profile.pwTooShort', 'La contraseña debe tener al menos 6 caracteres'))
      return
    }
    setSavingPw(true)
    try {
      const res = await apiFetch(`/api/v1/users/${user.id}`, {
        method: 'PUT',
        body: JSON.stringify({ password: pwForm.new_password }),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || t('profile.pwError', 'Error al cambiar la contraseña'))
      }
      setPwForm({ new_password: '', confirm_password: '' })
      setPwSuccess(true)
      setTimeout(() => setPwSuccess(false), 3000)
    } catch (err) {
      setPwError(err.message)
    } finally {
      setSavingPw(false)
    }
  }

  const handleDeleteConfirm = async () => {
    try {
      await apiFetch(`/api/v1/users/${user.id}`, { method: 'DELETE' })
    } catch {
      // continuar con el logout aunque falle
    }
    logout()
    navigate('/login')
  }

  const displayName =
    form.first_name || form.last_name
      ? `${form.first_name} ${form.last_name}`.trim()
      : user?.email ?? ''

  return (
    <div className="bg-background min-h-screen">
      <TopNavBar />
      <SideNavBar />
      <main className="lg:pl-64 pt-20 px-6 pb-20 min-h-screen">
        <div className="max-w-6xl mx-auto">
          <header className="mb-10">
            <h1 className="text-3xl font-extrabold text-primary tracking-tight mb-2">
              {t('profile.pageTitle')}
            </h1>
          </header>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* ── Left: profile card ─────────────────────────────────────── */}
            <div className="lg:col-span-4 space-y-6">
              <div className="bg-surface-container-lowest border border-slate-200 rounded-xl p-8 flex flex-col items-center text-center shadow-sm">
                <div className="w-32 h-32 rounded-full bg-slate-200 overflow-hidden mb-6 flex items-center justify-center">
                  <span className="material-symbols-outlined text-5xl text-slate-400">person</span>
                </div>

                {loading ? (
                  <div className="space-y-2 w-full">
                    <div className="h-5 bg-slate-200 rounded animate-pulse w-3/4 mx-auto" />
                    <div className="h-4 bg-slate-100 rounded animate-pulse w-1/2 mx-auto" />
                  </div>
                ) : (
                  <>
                    <h3 className="text-xl font-bold text-primary">{displayName}</h3>
                    <p className="text-sm text-on-surface-variant mt-1 mb-1">{form.email}</p>
                    {form.organization && (
                      <p className="text-xs text-slate-500 mb-4">{form.organization}</p>
                    )}
                    <div className="flex flex-wrap justify-center gap-2 mt-3">
                      {roleName && (
                        <span className="px-3 py-1 bg-primary-container/10 text-primary-container text-[10px] font-bold uppercase rounded-full">
                          {roleName}
                        </span>
                      )}
                      <span className="px-3 py-1 bg-emerald-100 text-emerald-800 text-[10px] font-bold uppercase rounded-full">
                        {t('profile.statusActive')}
                      </span>
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* ── Right: forms ───────────────────────────────────────────── */}
            <div className="lg:col-span-8 space-y-6">
              {/* Personal info */}
              <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-8 space-y-6">
                <h2 className="text-lg font-bold text-slate-800">
                  {t('profile.personalInfo', 'Información personal')}
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="block text-xs font-bold uppercase text-slate-500">
                      {t('profile.firstName')}
                    </label>
                    <input
                      className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3"
                      value={form.first_name}
                      onChange={(e) => setForm({ ...form, first_name: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="block text-xs font-bold uppercase text-slate-500">
                      {t('profile.lastName')}
                    </label>
                    <input
                      className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3"
                      value={form.last_name}
                      onChange={(e) => setForm({ ...form, last_name: e.target.value })}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="block text-xs font-bold uppercase text-slate-500">
                    {t('profile.email')}
                  </label>
                  <input
                    type="email"
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3"
                    value={form.email}
                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                  />
                </div>

                <div className="space-y-2">
                  <label className="block text-xs font-bold uppercase text-slate-500">
                    {t('profile.organization', 'Organización')}
                  </label>
                  <input
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3"
                    value={form.organization}
                    onChange={(e) => setForm({ ...form, organization: e.target.value })}
                  />
                </div>

                {saveError && <p className="text-red-500 text-sm">{saveError}</p>}

                <div className="flex justify-end pt-2">
                  <button
                    onClick={handleSave}
                    disabled={savingProfile || loading}
                    className="px-10 py-3 bg-primary text-white rounded-lg text-sm font-bold shadow-md hover:opacity-90 transition-opacity disabled:opacity-60"
                  >
                    {savingProfile
                      ? t('profile.saving', 'Guardando...')
                      : t('profile.saveButton')}
                  </button>
                </div>
              </div>

              {/* Change password */}
              <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-8">
                <h2 className="text-lg font-bold text-slate-800 mb-6">
                  {t('profile.changePassword', 'Cambiar contraseña')}
                </h2>
                <form onSubmit={handleChangePassword} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label className="block text-xs font-bold uppercase text-slate-500">
                        {t('profile.newPassword', 'Nueva contraseña')}
                      </label>
                      <input
                        type="password"
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3"
                        placeholder="••••••••"
                        value={pwForm.new_password}
                        onChange={(e) => setPwForm({ ...pwForm, new_password: e.target.value })}
                        minLength={6}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="block text-xs font-bold uppercase text-slate-500">
                        {t('profile.confirmPassword', 'Confirmar contraseña')}
                      </label>
                      <input
                        type="password"
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3"
                        placeholder="••••••••"
                        value={pwForm.confirm_password}
                        onChange={(e) =>
                          setPwForm({ ...pwForm, confirm_password: e.target.value })
                        }
                        required
                      />
                    </div>
                  </div>

                  {pwError && <p className="text-red-500 text-sm">{pwError}</p>}
                  {pwSuccess && (
                    <p className="text-emerald-600 text-sm">
                      {t('profile.pwChanged', 'Contraseña actualizada correctamente')}
                    </p>
                  )}

                  <div className="flex justify-end pt-2">
                    <button
                      type="submit"
                      disabled={savingPw}
                      className="px-8 py-3 bg-slate-800 text-white rounded-lg text-sm font-bold hover:opacity-90 transition-opacity disabled:opacity-60"
                    >
                      {savingPw
                        ? t('profile.saving', 'Guardando...')
                        : t('profile.changePassword', 'Cambiar contraseña')}
                    </button>
                  </div>
                </form>
              </div>

              {/* Danger zone */}
              <div className="bg-red-50 border border-red-200 rounded-xl shadow-sm p-8">
                <h2 className="text-lg font-bold text-red-800 mb-2">
                  {t('profile.dangerZone', 'Zona de peligro')}
                </h2>
                <p className="text-sm text-red-600 mb-6">
                  {t('profile.deleteModalBody')}
                </p>
                <button
                  onClick={() => setShowDeleteModal(true)}
                  className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-bold shadow-md transition-colors flex items-center gap-2"
                >
                  <span className="material-symbols-outlined text-[18px]">delete</span>
                  {t('profile.deleteButton')}
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
      <MobileNav />

      {/* Success toast */}
      {showSuccessMessage && (
        <div className="fixed bottom-24 left-1/2 -translate-x-1/2 bg-emerald-600 text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-2 z-50 animate-pulse">
          <span className="material-symbols-outlined text-[20px]">check_circle</span>
          <span className="font-medium">{t('profile.savedMessage')}</span>
        </div>
      )}

      {/* Delete confirmation modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-8">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                <span className="material-symbols-outlined text-red-600 text-2xl">warning</span>
              </div>
              <div>
                <h3 className="text-xl font-bold text-slate-900">
                  {t('profile.deleteModalTitle')}
                </h3>
                <p className="text-sm text-slate-500">{t('profile.deleteModalWarning')}</p>
              </div>
            </div>
            <p className="text-slate-600 mb-8">{t('profile.deleteModalBody')}</p>
            <div className="flex gap-4 justify-end">
              <button
                onClick={() => setShowDeleteModal(false)}
                className="px-6 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-medium transition-colors"
              >
                {t('profile.deleteModalCancel')}
              </button>
              <button
                onClick={handleDeleteConfirm}
                className="px-6 py-2.5 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors"
              >
                {t('profile.deleteModalConfirm')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ProfilePage
