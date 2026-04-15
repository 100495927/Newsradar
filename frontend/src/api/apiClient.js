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
