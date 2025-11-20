const USER_KEY = 'conceptTree:user'
const AUTH_KEY = 'conceptTree:auth'

export function getUser() {
  try {
    const authRaw = localStorage.getItem(AUTH_KEY)
    if (authRaw) {
      const a = JSON.parse(authRaw)
      if (a && typeof a.name === 'string' && a.name.trim() && typeof a.token === 'string' && a.token) {
        return { name: a.name.trim(), token: a.token }
      }
    }
    const raw = localStorage.getItem(USER_KEY)
    if (!raw) return null
    const obj = JSON.parse(raw)
    if (obj && typeof obj.name === 'string' && obj.name.trim()) {
      return { name: obj.name.trim() }
    }
    return null
  } catch {
    return null
  }
}

export function saveUser(name) {
  try {
    const obj = { name: String(name || '').trim() }
    if (!obj.name) return null
    localStorage.setItem(USER_KEY, JSON.stringify(obj))
    return obj
  } catch {
    return null
  }
}

export function saveAuth(name, token) {
  try {
    const n = String(name || '').trim()
    const t = String(token || '')
    if (!n || !t) return null
    const obj = { name: n, token: t }
    localStorage.setItem(AUTH_KEY, JSON.stringify(obj))
    return obj
  } catch {
    return null
  }
}

export function clearUser() {
  try {
    localStorage.removeItem(USER_KEY)
    localStorage.removeItem(AUTH_KEY)
  } catch {
    void 0
  }
}