const USER_KEY = 'conceptTree:user'

export function getUser() {
  try {
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

export function clearUser() {
  try {
    localStorage.removeItem(USER_KEY)
  } catch {
    // ignore
  }
}