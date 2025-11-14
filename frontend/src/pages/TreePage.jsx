import { useState, useMemo } from 'react'
import { traverseDFS, findNode } from '../utils/tree-utils.js'
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

  // 使用真正的树结构计算进度
  const progress = useMemo(() => {
    if (!tree || !tree.root) return { mastered: 0, total: 0 }
    
    let total = 0
    let mastered = 0
    
    // 使用深度优先遍历计算进度
    traverseDFS(tree.root, (node) => {
      total++
      if (masteredSet.has(node.id)) {
        mastered++
      }
    })
    
    return { mastered, total }
  }, [tree, masteredSet])

  // 获取学习建议 - 基于树遍历
  const suggestions = useMemo(() => {
    if (!tree || !tree.root) return []
    
    const result = []
    traverseDFS(tree.root, (node) => {
      if (!masteredSet.has(node.id)) {
        result.push(node)
      }
    })
    
    // 按难度等级排序
    return result.sort((a, b) => a.level - b.level)
  }, [tree, masteredSet])

  function goNextSuggestion() {
    if (!tree || !tree.root || suggestions.length === 0) return
    const nextNode = suggestions[0]
    if (nextNode) setSelectedNodeId(nextNode.id)
  }

  const progressPercent = progress.total > 0 ? (progress.mastered / progress.total) * 100 : 0

  // 获取当前选中的节点
  const selectedNode = useMemo(() => {
    if (!tree || !tree.root || selectedNodeId === '__overall__') return null
    return findNode(tree.root, (node) => node.id === selectedNodeId)
  }, [tree, selectedNodeId])

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
          {selectedNode ? (
            <ConceptCard
              tree={tree}
              nodeId={selectedNodeId}
              node={selectedNode}
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
              {suggestions.length > 0 && (
                <button onClick={goNextSuggestion} className="btn-suggestion">
                  开始学习: {suggestions[0]?.name}
                </button>
              )}
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
