import { useState } from 'react'

export default function Login({ user, onLogin, onLogout }) {
  const [name, setName] = useState('')
  if (user) {
    return (
      <div className="login-box">
        <span className="login-info">已登录：{user.name}</span>
        <button className="secondary" onClick={onLogout}>退出登录</button>
      </div>
    )
  }
  return (
    <div className="login-box">
      <input
        className="concept-input-box"
        placeholder="请输入昵称，开始个性化学习"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <button
        className="primary"
        onClick={() => name.trim() && onLogin(name.trim())}
        disabled={!name.trim()}
      >登录</button>
    </div>
  )
}