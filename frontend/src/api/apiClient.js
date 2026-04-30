const TOKEN_KEY = 'nr_token'

/**
 * Wrapper sobre fetch que añade automáticamente el header Authorization: Bearer <token>
 * a todas las peticiones autenticadas.
 */
export async function apiFetch(path, options = {}) {
  const token = localStorage.getItem(TOKEN_KEY)
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }
  return fetch(path, { ...options, headers })
}

// ---------------------------------------------------------------------------
// Stats
// ---------------------------------------------------------------------------

export async function getGlobalStats() {
  const res = await apiFetch('/api/v1/stats/global')
  if (!res.ok) throw new Error('Error al obtener estadísticas globales')
  return res.json()
}

export async function getTimeline() {
  const res = await apiFetch('/api/v1/stats/timeline')
  if (!res.ok) throw new Error('Error al obtener timeline')
  return res.json()
}

export async function getWordCloud(categoria) {
  const res = await apiFetch(`/api/v1/stats/cloud/${encodeURIComponent(categoria)}`)
  if (!res.ok) throw new Error('Error al obtener nube de palabras')
  return res.json()
}
