import { useState, useMemo } from 'react'
import { nextSuggestion } from '../utils/suggestions.js'
import GraphView from '../components/GraphView.jsx'
import ConceptCard from '../components/ConceptCard.jsx'
import ProgressBar from '../components/ProgressBar.jsx'
import '../styles/TreePage.css'

export default function TreePage({ 
  concept, 
  tree, 
  masteredSet, 
  onToggleMastered,
  user,
  onLogout 
}) {
  const [selectedNodeId, setSelectedNodeId] = useState('__overall__')
  const [isReadingMode, setIsReadingMode] = useState(false)

  // 学习顺序在按钮弹层中计算时再取用

  const progress = useMemo(() => {
    if (!tree) return { mastered: 0, total: 0 }
    const total = tree.nodes.length
    const mastered = tree.nodes.filter(n => masteredSet.has(n.id)).length
    return { mastered, total }
  }, [tree, masteredSet])

  function goNextSuggestion() {
    if (!tree) return
    const nextId = nextSuggestion(tree, masteredSet)
    if (nextId) setSelectedNodeId(nextId)
  }

  const progressPercent = progress.total > 0 ? (progress.mastered / progress.total) * 100 : 0

  return (
    <div className={`tree-page-container ${isReadingMode ? 'reading-mode' : ''}`}>
      {/* 顶部栏 */}
      <header className="tree-header">
        <div className="header-left">
          <h1 className="concept-title">{concept}</h1>
          <div className="progress-info">
            <span>{progress.mastered} / {progress.total} 已掌握</span>
            <div className="mini-progress-bar">
              <div className="progress-fill" style={{ width: `${progressPercent}%` }} />
            </div>
          </div>
        </div>
        <div className="header-right">
          {user && (
            <div className="user-info">
              <span>👤 {user.name}</span>
              <button onClick={onLogout} className="btn-logout">退出</button>
            </div>
          )}
          <button 
            onClick={() => setIsReadingMode(!isReadingMode)}
            className={`btn-reading-mode ${isReadingMode ? 'active' : ''}`}
          >
            {isReadingMode ? '📖 退出阅读' : '📝 阅读模式'}
          </button>
        </div>
      </header>

      {/* 主内容区 */}
      <div className={`tree-main-content ${isReadingMode ? 'reading-mode' : ''}`}>
        {/* 左侧：概念树 */}
        <aside className="tree-sidebar">
          <h3>概念图谱</h3>
          <GraphView
            tree={tree}
            masteredSet={masteredSet}
            selectedNodeId={selectedNodeId}
            onSelect={setSelectedNodeId}
          />
        </aside>

        {/* 右侧：详情 */}
        <main className="tree-detail">
          {selectedNodeId ? (
            <ConceptCard
              tree={tree}
              nodeId={selectedNodeId}
              mastered={masteredSet.has(selectedNodeId)}
              onToggleMastered={() => onToggleMastered(selectedNodeId)}
              onNext={goNextSuggestion}
              isReadingMode={isReadingMode}
              onToggleReadingMode={() => setIsReadingMode(!isReadingMode)}
            />
          ) : (
            <div className="empty-hint">
              <div className="empty-icon">🎯</div>
              <p>点击左侧节点查看详情</p>
            </div>
          )}
          
          {/* 底部进度 */}
          <div className="progress-section">
            <ProgressBar mastered={progress.mastered} total={progress.total} />
          </div>
        </main>
      </div>
    </div>
  )
}
