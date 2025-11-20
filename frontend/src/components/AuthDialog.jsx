import { useState } from 'react'

function LoginForm({ onSuccess }) {
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  const [id, setId] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const disabled = !id.trim() || password.length < 6

  async function submit(e) {
    e.preventDefault()
    setError('')
    const body = { phoneOrName: id.trim(), password }
    try {
      const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })
      if (!res.ok) {
        throw new Error('登录失败')
      }
      const data = await res.json()
      onSuccess({ name: data.user?.name, token: data.token })
    } catch (e) {
      setError(e.message || '登录失败')
    }
  }

  return (
    <form onSubmit={submit} className="login-box">
      <input className="concept-input-box" placeholder="手机号或用户名" value={id} onChange={(e) => setId(e.target.value)} />
      <input className="concept-input-box" placeholder="密码" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      <button className="primary" type="submit" disabled={disabled}>登录</button>
      {error && <div className="error-tip">{error}</div>}
    </form>
  )
}

function RegisterForm({ onSuccess }) {
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  const [phone, setPhone] = useState('')
  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const phoneOk = /^[0-9]{6,15}$/.test(phone)
  const nameOk = !!name.trim() && name.trim().length <= 32
  const passOk = password.length >= 6
  const disabled = !(phoneOk && nameOk && passOk)

  async function submit(e) {
    e.preventDefault()
    setError('')
    const body = { phone: phone.trim(), name: name.trim(), password }
    try {
      const res = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })
      if (!res.ok) {
        if (res.status === 409) throw new Error('账号已存在')
        throw new Error('注册失败')
      }
      const loginRes = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phoneOrName: body.phone, password: body.password })
      })
      if (!loginRes.ok) throw new Error('自动登录失败')
      const data = await loginRes.json()
      onSuccess({ name: data.user?.name, token: data.token })
    } catch (e) {
      setError(e.message || '注册失败')
    }
  }

  return (
    <form onSubmit={submit} className="login-box">
      <input className="concept-input-box" placeholder="手机号" value={phone} onChange={(e) => setPhone(e.target.value)} />
      <input className="concept-input-box" placeholder="用户名" value={name} onChange={(e) => setName(e.target.value)} />
      <input className="concept-input-box" placeholder="密码（≥6位）" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      <button className="primary" type="submit" disabled={disabled}>注册并登录</button>
      {error && <div className="error-tip">{error}</div>}
    </form>
  )
}

export default function AuthDialog({ onSuccess, onClose }) {
  const [tab, setTab] = useState('login')
  return (
    <div className="login-pop">
      <div className="modern-toolbar">
        <button className={`toolbar-btn ${tab === 'login' ? 'active' : ''}`} onClick={() => setTab('login')}>登录</button>
        <button className={`toolbar-btn ${tab === 'register' ? 'active' : ''}`} onClick={() => setTab('register')}>注册</button>
        <button className="toolbar-btn" onClick={onClose}>关闭</button>
      </div>
      {tab === 'login' ? (
        <LoginForm onSuccess={onSuccess} />
      ) : (
        <RegisterForm onSuccess={onSuccess} />
      )}
    </div>
  )
}