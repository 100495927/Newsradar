import { createContext, useContext, useState } from 'react'

const AuthContext = createContext(null)

const TOKEN_KEY = 'nr_token'
const USER_KEY = 'nr_user'

function parseJwtId(token) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return parseInt(payload.sub, 10)
  } catch {
    return null
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem(USER_KEY)
    return stored ? JSON.parse(stored) : null
  })

  async function login(email, password) {
    const res = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Error al iniciar sesión')
    }
    const data = await res.json()
    _persist(data.access_token, { email })
  }

  async function register(fields) {
    const res = await fetch('/api/v1/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(fields),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Error al registrarse')
    }
    const data = await res.json()
    _persist(data.access_token, { email: fields.email })
  }

  function logout() {
    setToken(null)
    setUser(null)
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  function _persist(accessToken, userData) {
    const id = parseJwtId(accessToken)
    const full = { ...userData, id }
    setToken(accessToken)
    setUser(full)
    localStorage.setItem(TOKEN_KEY, accessToken)
    localStorage.setItem(USER_KEY, JSON.stringify(full))
  }

  return (
    <AuthContext.Provider value={{ token, user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
