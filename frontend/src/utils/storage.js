const KEY_PREFIX = 'conceptTree:'
const USER_SEP = ':'

export function getMastered(concept) {
  try {
    const raw = localStorage.getItem(KEY_PREFIX + concept)
    if (!raw) return new Set()
    const arr = JSON.parse(raw)
    return new Set(Array.isArray(arr) ? arr : [])
  } catch {
    return new Set()
  }
}

export function saveMastered(concept, set) {
  try {
    const arr = Array.from(set)
    localStorage.setItem(KEY_PREFIX + concept, JSON.stringify(arr))
  } catch (err) {
    // 在某些环境（隐私模式/受限存储）下可能抛错，保持静默降级
    // eslint-disable-next-line no-console
    console.warn('[storage] saveMastered failed:', err)
  }
}

export function resetProgress(concept) {
  try {
    localStorage.removeItem(KEY_PREFIX + concept)
  } catch (err) {
    // eslint-disable-next-line no-console
    console.warn('[storage] resetProgress failed:', err)
  }
}

// per-user variants
export function getMasteredForUser(userName, concept) {
  if (!userName) return getMastered(concept)
  const key = KEY_PREFIX + String(userName) + USER_SEP + concept
  try {
    const raw = localStorage.getItem(key)
    if (!raw) return new Set()
    const arr = JSON.parse(raw)
    return new Set(Array.isArray(arr) ? arr : [])
  } catch {
    return new Set()
  }
}

export function saveMasteredForUser(userName, concept, set) {
  if (!userName) return saveMastered(concept, set)
  const key = KEY_PREFIX + String(userName) + USER_SEP + concept
  try {
    const arr = Array.from(set)
    localStorage.setItem(key, JSON.stringify(arr))
  } catch (err) {
    // eslint-disable-next-line no-console
    console.warn('[storage] saveMasteredForUser failed:', err)
  }
}

export function resetProgressForUser(userName, concept) {
  if (!userName) return resetProgress(concept)
  const key = KEY_PREFIX + String(userName) + USER_SEP + concept
  try {
    localStorage.removeItem(key)
  } catch (err) {
    // eslint-disable-next-line no-console
    console.warn('[storage] resetProgressForUser failed:', err)
  }
}