import { useState, useEffect, useRef } from 'react'
import TopNavBar from '../components/TopNavBar'
import SideNavBar from '../components/SideNavBar'
import MobileNav from '../components/MobileNav'

function ProfilePage() {
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [showSuccessMessage, setShowSuccessMessage] = useState(false)
  const timeoutRef = useRef(null)

  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
    }
  }, [])

  const handleSave = () => {
    setShowSuccessMessage(true)
    timeoutRef.current = setTimeout(() => setShowSuccessMessage(false), 3000)
  }

  const handleDeleteConfirm = () => {
    setShowDeleteModal(false)
    // Aquí iría la lógica de eliminación
  }

  return (
    <div className="bg-background min-h-screen">
      <TopNavBar />
      <SideNavBar />
      <main className="lg:pl-64 pt-20 px-6 pb-20 min-h-screen">
        <div className="max-w-6xl mx-auto">
          <header className="mb-10">
            <h1 className="text-3xl font-extrabold text-primary tracking-tight mb-2">
              Configuración de Perfil
            </h1>
          </header>
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            <div className="lg:col-span-4 space-y-6">
              <div className="bg-surface-container-lowest border border-slate-200 rounded-xl p-8 flex flex-col items-center text-center shadow-sm">
                <div className="w-32 h-32 rounded-full bg-slate-200 overflow-hidden mb-6 flex items-center justify-center">
                  <span className="material-symbols-outlined text-5xl text-slate-400">
                    person
                  </span>
                </div>
                <h3 className="text-xl font-bold text-primary">John Doe</h3>
                <p className="text-sm text-on-surface-variant mb-6">
                  john.doe@globalnews.org
                </p>
                <span className="px-3 py-1 bg-emerald-100 text-emerald-800 text-[10px] font-bold uppercase rounded-full">
                  Activo
                </span>
              </div>
            </div>
            <div className="lg:col-span-8">
              <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-8 space-y-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="space-y-2">
                    <label className="block text-xs font-bold uppercase text-slate-500">
                      Nombre
                    </label>
                    <input
                      className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3"
                      defaultValue="John"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="block text-xs font-bold uppercase text-slate-500">
                      Apellido
                    </label>
                    <input
                      className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3"
                      defaultValue="Doe"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="block text-xs font-bold uppercase text-slate-500">
                    Correo
                  </label>
                  <input
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3"
                    defaultValue="john.doe@globalnews.org"
                  />
                </div>
                <div className="pt-8 flex justify-between items-center">
                  <button
                    onClick={() => setShowDeleteModal(true)}
                    className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-bold shadow-md transition-colors flex items-center gap-2"
                  >
                    <span className="material-symbols-outlined text-[18px]">
                      delete
                    </span>
                    Borrar Perfil
                  </button>
                  <button
                    onClick={handleSave}
                    className="px-10 py-3 bg-primary text-white rounded-lg text-sm font-bold shadow-md hover:opacity-90 transition-opacity"
                  >
                    Guardar Perfil
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
      <MobileNav />

      {/* Success Message */}
      {showSuccessMessage && (
        <div className="fixed bottom-24 left-1/2 -translate-x-1/2 bg-emerald-600 text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-2 z-50 animate-pulse">
          <span className="material-symbols-outlined text-[20px]">
            check_circle
          </span>
          <span className="font-medium">Perfil guardado exitosamente</span>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-8">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                <span className="material-symbols-outlined text-red-600 text-2xl">
                  warning
                </span>
              </div>
              <div>
                <h3 className="text-xl font-bold text-slate-900">
                  Eliminar Perfil
                </h3>
                <p className="text-sm text-slate-500">
                  Esta acción no se puede deshacer
                </p>
              </div>
            </div>
            <p className="text-slate-600 mb-8">
              ¿Estás seguro de que deseas eliminar tu perfil? Todos tus datos,
              alertas y configuraciones serán eliminados permanentemente.
            </p>
            <div className="flex gap-4 justify-end">
              <button
                onClick={() => setShowDeleteModal(false)}
                className="px-6 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-medium transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleDeleteConfirm}
                className="px-6 py-2.5 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors"
              >
                Sí, eliminar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ProfilePage
