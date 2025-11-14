import { useState } from 'react'
import './App.css'
import ConceptInput from './components/ConceptInput.jsx'
import TreePage from './pages/TreePage.jsx'
import LoadingStages from './components/LoadingStages.jsx'
import { getMastered, saveMastered, getMasteredForUser, saveMasteredForUser } from './utils/storage.js'
import Login from './components/Login.jsx'
import { getUser, saveUser, clearUser } from './utils/user.js'

// API配置
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [page, setPage] = useState('home')
  const [concept, setConcept] = useState('')
  const [tree, setTree] = useState(null)
  const [masteredSet, setMasteredSet] = useState(new Set())
  const [error, setError] = useState(null)
  const [user, setUser] = useState(getUser())
  const [showLoginGlobal, setShowLoginGlobal] = useState(false)
  const [loading, setLoading] = useState(false)
  const [loadingStage, setLoadingStage] = useState(0)
  const [loadingProgress, setLoadingProgress] = useState(0)
  const [loadingMessage, setLoadingMessage] = useState('')

  // TODO: 连接后端API
  async function handleLoadTree(conceptName, opts = {}) {
    setError(null)
    setLoading(true)
    setPage('loading')
    setLoadingStage(0)
    setLoadingProgress(0)
    setLoadingMessage('')
    
    try {
      const progressTimer = setInterval(async () => {
        try {
          const r = await fetch(`${API_BASE_URL}/api/progress/${encodeURIComponent(conceptName)}`)
          if (r.ok) {
            const p = await r.json()
            setLoadingStage(p.stage || 0)
            setLoadingProgress(p.percent || 0)
            setLoadingMessage(p.message || '')
          }
        } catch {}
      }, 400)
      // 调用后端API获取依赖树
      const params = new URLSearchParams()
      params.set('depth', '5')
      params.set('width', '6')
      if (opts.focus && opts.focus.trim()) params.set('focus', opts.focus.trim())
      if (opts.minWidth && opts.minWidth.trim()) params.set('minWidth', opts.minWidth.trim())
      if (opts.priority && opts.priority.trim()) params.set('priority', opts.priority.trim())
      const response = await fetch(`${API_BASE_URL}/api/concept/${encodeURIComponent(conceptName)}?${params.toString()}`)
      
      if (!response.ok) {
        throw new Error('获取依赖树失败')
      }
      
      const result = await response.json()
      clearInterval(progressTimer)
      
      // 获取用户进度
      const stored = user ? getMasteredForUser(user.name, conceptName) : getMastered(conceptName)
      
      setConcept(conceptName)
      setTree(result.tree)
      setMasteredSet(stored)
      setPage('tree')
      
    } catch (e) {
      setError(e.message || '获取依赖树失败')
      setPage('home')
    } finally {
      setLoadingMessage('')
      setLoadingStage(0)
      setLoadingProgress(0)
      setLoading(false)
    }
  }

  function toggleMastered(nodeId) {
    const next = new Set(masteredSet)
    if (next.has(nodeId)) next.delete(nodeId)
    else next.add(nodeId)
    setMasteredSet(next)
    if (user) saveMasteredForUser(user.name, concept, next)
    else saveMastered(concept, next)
  }

  function onLogin(name) {
    const saved = saveUser(name)
    if (saved) {
      setUser(saved)
      if (concept) {
        const stored = getMasteredForUser(saved.name, concept)
        setMasteredSet(stored)
      }
    }
  }

  function onLogout() {
    clearUser()
    setUser(null)
    if (concept) {
      const stored = getMastered(concept)
      setMasteredSet(stored)
    }
  }

  if (page === 'loading') {
    return <LoadingStages current={loadingStage} progress={loadingProgress} message={loadingMessage} />
  }
  
  if (page === 'home') {
    return (
      <div className="page">
        {/* CodeMonkey 装饰元素 - 对称布局 */}
        <div className="formula formula-1">f(x) = x² + 2x + 1</div>
        <div className="formula formula-2">∫ e^x dx = e^x + C</div>
        <div className="code-block code-block-1">if (concept) {'{'}
          <br/>&nbsp;&nbsp;learn();
          <br/>{'}'}
        </div>
        <div className="code-block code-block-2">while (learning) {'{'}
          <br/>&nbsp;&nbsp;grow();
          <br/>{'}'}
        </div>
        <div className="shape-circle shape-circle-left"></div>
        <div className="shape-circle shape-circle-right"></div>
        
        {/* 全局右上角登录区 */}
        <div className="global-login">
          {user ? (
            <>
              <span className="chip">{`已登录：${user.name}`}</span>
              <button className="danger" onClick={onLogout}>退出</button>
            </>
          ) : (
            <button className="primary" onClick={() => setShowLoginGlobal((v) => !v)}>登录</button>
          )}
          {showLoginGlobal && !user && (
            <div className="login-pop">
              <Login
                user={user}
                onLogin={(name) => {
                  onLogin(name)
                  setShowLoginGlobal(false)
                }}
                onLogout={onLogout}
              />
            </div>
          )}
        </div>
        <header className="header">
          <div className="monkey-logo">
            <img src="/logo.png" alt="CodeMonkey Logo" className="logo-img" />
          </div>
          <h1>ConceptTree</h1>
          <p className="subtitle">// 10 分钟看懂任何复杂概念的依赖关系</p>
        </header>
        <ConceptInput onSubmit={handleLoadTree} error={error} />
      </div>
    )
  }

  if (page === 'tree') {
    return (
      <TreePage
        concept={concept}
        tree={tree}
        masteredSet={masteredSet}
        onToggleMastered={toggleMastered}
        user={user}
        onLogout={onLogout}
      />
    )
  }

  return null
}

export default App
