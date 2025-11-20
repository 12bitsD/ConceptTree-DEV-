import { useState, useEffect, useMemo } from 'react'
import './App.css'
import ConceptInput from './components/ConceptInput.jsx'
import RefineDialog from './components/RefineDialog.jsx'
import TreePage from './pages/TreePage.jsx'
import LoadingStages from './components/LoadingStages.jsx'
import { getMastered, saveMastered, getMasteredForUser, saveMasteredForUser } from './utils/storage.js'
import AuthDialog from './components/AuthDialog.jsx'
import { getUser, saveAuth, clearUser } from './utils/user.js'

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
  const [pendingConcept, setPendingConcept] = useState('')
  const [refineOptions, setRefineOptions] = useState(null)
  const [loadingPayload, setLoadingPayload] = useState(null)
  const [refineLoading, setRefineLoading] = useState(false)
  const [typedText, setTypedText] = useState('')
  const [overlayProgress, setOverlayProgress] = useState(0)
  const overlayMessages = useMemo(() => ['解析关键词...', '理解意图与场景...', '生成细化维度...', '筛选建议选项...'], [])
  useEffect(() => {
    if (!refineLoading) return
    setTypedText('')
    let i = 0
    let pos = 0
    let timer
    const typeNext = () => {
      const msg = overlayMessages[i]
      if (pos <= msg.length) {
        setTypedText(msg.slice(0, pos))
        pos += 1
        timer = setTimeout(typeNext, 45)
      } else {
        i = (i + 1) % overlayMessages.length
        pos = 0
        timer = setTimeout(typeNext, 300)
      }
    }
    typeNext()
    return () => { if (timer) clearTimeout(timer) }
  }, [refineLoading, overlayMessages])

  useEffect(() => {
    if (!refineLoading) return
    setOverlayProgress(0)
    const t = setInterval(() => {
      setOverlayProgress((p) => (p < 60 ? p + 2 : p))
    }, 80)
    return () => clearInterval(t)
  }, [refineLoading])
 

  // TODO: 连接后端API
  async function handleLoadTree(conceptName) {
    setError(null)
    setLoadingPayload({ concept: conceptName, details: null })
    setPage('loading')
    
    try {
      // 调用后端API获取依赖树
      const response = await fetch(`${API_BASE_URL}/api/concept/${encodeURIComponent(conceptName)}`)
      
      if (!response.ok) {
        throw new Error('获取依赖树失败')
      }
      
      const result = await response.json()

      // 统一后端返回到前端期望的数据结构
      const raw = result.tree
      const mappedNodes = Array.isArray(raw?.nodes) ? raw.nodes.map((n) => ({
        id: n.id,
        label: n.name,
        prerequisites: Array.isArray(n.dependencies) ? n.dependencies : [],
      })) : []
      const mappedTree = {
        concept: result.concept || raw?.target || conceptName,
        root: raw?.nodes?.[0]?.id,
        nodes: mappedNodes,
        total: typeof raw?.total_nodes === 'number' ? raw.total_nodes : mappedNodes.length,
        overall: raw?.overall || {},
        cards: raw?.cards,
      }

      // 获取用户进度
      const stored = user ? getMasteredForUser(user.name, conceptName) : getMastered(conceptName)

      setConcept(conceptName)
      setTree(mappedTree)
      setMasteredSet(stored)
      setPage('tree')
      
    } catch (e) {
      setError(e.message)
      setPage('home')
    } finally {
      void 0
    }
  }

  async function handleConceptSubmit(conceptName) {
    setError(null)
    setPendingConcept(conceptName)
    setRefineLoading(true)
    const start = Date.now()
    try {
      const res = await fetch(`${API_BASE_URL}/api/prompt/refine`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ concept: conceptName })
      })
      if (!res.ok) throw new Error('细节选项生成失败')
      const data = await res.json()
      const opts = Array.isArray(data.options) ? data.options : []
      setRefineOptions(opts)
      setPage('refine')
      const elapsed = Date.now() - start
      const hold = Math.max(0, 700 - elapsed)
      setTimeout(() => setRefineLoading(false), hold)
    } catch {
      setRefineOptions([])
      setPage('refine')
      const elapsed = Date.now() - start
      const hold = Math.max(0, 700 - elapsed)
      setTimeout(() => setRefineLoading(false), hold)
    }
  }

  async function handleConfirmRefine(details) {
    setLoadingPayload({ concept: pendingConcept, details })
    setPage('loading')
    try {
      const res = await fetch(`${API_BASE_URL}/api/concept`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ concept: pendingConcept, details })
      })
      if (!res.ok) throw new Error('获取依赖树失败')
      const result = await res.json()
      const raw = result.tree
      const mappedNodes = Array.isArray(raw?.nodes) ? raw.nodes.map((n) => ({
        id: n.id,
        label: n.name,
        prerequisites: Array.isArray(n.dependencies) ? n.dependencies : [],
      })) : []
      const mappedTree = {
        concept: result.concept || raw?.target || pendingConcept,
        root: raw?.nodes?.[0]?.id,
        nodes: mappedNodes,
        total: typeof raw?.total_nodes === 'number' ? raw.total_nodes : mappedNodes.length,
        overall: raw?.overall || {},
        cards: raw?.cards,
      }
      const stored = user ? getMasteredForUser(user.name, pendingConcept) : getMastered(pendingConcept)
      setConcept(pendingConcept)
      setTree(mappedTree)
      setMasteredSet(stored)
      setPage('tree')
    } catch (e) {
      setError(e.message)
      setPage('home')
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

  function onLoggedIn(u) {
    const saved = saveAuth(u?.name, u?.token)
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
    return <LoadingStages payload={loadingPayload} />
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
            <AuthDialog
              onSuccess={(u) => { onLoggedIn(u); setShowLoginGlobal(false) }}
              onClose={() => setShowLoginGlobal(false)}
            />
          )}
        </div>
        <header className="header">
          <div className="monkey-logo">
            <img src="/logo.png" alt="CodeMonkey Logo" className="logo-img" />
          </div>
          <h1>ConceptTree</h1>
          <p className="subtitle">// 10 分钟看懂任何复杂概念的依赖关系</p>
        </header>
        <ConceptInput onSubmit={handleConceptSubmit} error={error} loading={refineLoading} />
        {refineLoading && (
          <div className="overlay-mask">
            <div className="overlay-card">
              <div className="overlay-title">正在分析你的问题</div>
              <div className="overlay-subtitle">{pendingConcept || concept}</div>
              <div className="overlay-terminal">{typedText}</div>
              <div className="overlay-progress">
                <div className="overlay-progress-fill" style={{ width: `${overlayProgress}%` }} />
              </div>
            </div>
          </div>
        )}
      </div>
    )
  }

  if (page === 'refine') {
    return (
      <div className="page">
        <header className="header">
          <div className="monkey-logo">
            <img src="/logo.png" alt="CodeMonkey Logo" className="logo-img" />
          </div>
          <h1>ConceptTree</h1>
          <p className="subtitle">// 细节补充</p>
        </header>
        {refineOptions && (
          <RefineDialog
            concept={pendingConcept}
            options={refineOptions}
            onConfirm={handleConfirmRefine}
            onSkip={() => handleLoadTree(pendingConcept)}
            onClose={() => { setPage('home') }}
          />
        )}
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
