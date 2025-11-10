function ResourceList({ resources }) {
  if (!Array.isArray(resources) || resources.length === 0) return null
  return (
    <div className="resource-list">
      {resources.map((r, idx) => (
        <a
          key={idx}
          className={`resource-link ${r.type || 'link'}`}
          href={r.url}
          target="_blank"
          rel="noreferrer"
        >
          <span className="res-type">{labelForType(r.type)}</span>
          <span className="res-title">{r.title || r.url}</span>
        </a>
      ))}
    </div>
  )
}

function labelForType(type) {
  switch (type) {
    case 'article': return '文章'
    case 'video': return '视频'
    case 'blog': return '博客'
    case 'doc': return '文档'
    default: return '链接'
  }
}

export default function ConceptCard({ tree, nodeId, mastered, onToggleMastered, onNext, isReadingMode, onToggleReadingMode }) {
  const node = tree.nodes.find((n) => n.id === nodeId)
  const card = tree.cards?.[nodeId]
  const rootId = tree.root || tree.nodes[0]?.id
  const idToLabel = new Map(tree.nodes.map((n) => [n.id, n.label]))

  function computeDepth(targetId) {
    if (!rootId) return 0
    const idToNode = new Map()
    tree.nodes.forEach((n) => idToNode.set(n.id, n))
    const visited = new Set([rootId])
    const queue = [{ id: rootId, depth: 0 }]
    while (queue.length) {
      const { id, depth } = queue.shift()
      if (id === targetId) return depth
      const prereqs = idToNode.get(id)?.prerequisites || []
      for (const p of prereqs) {
        if (!visited.has(p)) {
          visited.add(p)
          queue.push({ id: p, depth: depth + 1 })
        }
      }
    }
    return 0
  }

  function buildDependentsMap() {
    const m = new Map()
    for (const n of tree.nodes) {
      const pres = n.prerequisites || []
      for (const p of pres) {
        if (!m.has(p)) m.set(p, [])
        m.get(p).push(n.id)
      }
    }
    return m
  }

  function findPathToRoot(startId) {
    if (!startId || !rootId) return []
    if (startId === rootId) return [rootId]
    const dependentsMap = buildDependentsMap()
    const visited = new Set([startId])
    const queue = [{ id: startId, path: [startId] }]
    while (queue.length) {
      const { id, path } = queue.shift()
      if (id === rootId) return path
      const nexts = dependentsMap.get(id) || []
      for (const nx of nexts) {
        if (!visited.has(nx)) {
          visited.add(nx)
          queue.push({ id: nx, path: [...path, nx] })
        }
      }
    }
    return []
  }

  const isOverall = nodeId === '__overall__'
  const depth = isOverall ? 0 : computeDepth(nodeId)
  function levelText(d) {
    if (d <= 1) return '熟练（核心/关键前置）'
    if (d <= 3) return '熟练（建议）'
    return '入门（了解基本概念与常用术语）'
  }

  if (!isOverall && !node) return <div className="empty-card">未找到节点</div>

  return (
    <div className="modern-concept-card">
      {/* 卡片头部 */}
      <div className="card-header-modern">
        <div className="card-title-section">
          <h2 className="card-title">{isOverall ? tree.concept : node.label}</h2>
          {!isOverall && (
            <div className="status-badges">
              <span className={`status-badge ${mastered ? 'status-mastered' : 'status-unmastered'}`}>
                <span className="status-icon">{mastered ? '✅' : '⏳'}</span>
                {mastered ? '已掌握' : '学习中'}
              </span>
            </div>
          )}
        </div>
        <div className="card-actions">
          <button 
            className="reading-mode-toggle" 
            onClick={onToggleReadingMode}
            title={isReadingMode ? '退出阅读模式' : '进入阅读模式'}
          >
            {isReadingMode ? '📖' : '📝'}
          </button>
        </div>
      </div>

      {/* 卡片内容区域 */}
      <div className="card-content">
        {isOverall ? (
          <div className="overall-content">
            <div className="info-section">
              <div className="section-header">
                <div className="section-icon">🎯</div>
                <h3 className="section-title">总体概述</h3>
              </div>
              <p className="section-description">
                {tree.overall?.summary || '该概念的总体描述暂未提供。'}
              </p>
            </div>
            
            <div className="info-section">
              <div className="section-header">
                <div className="section-icon">📊</div>
                <h3 className="section-title">建议掌握等级</h3>
              </div>
              <div className="level-indicator">
                <span className="level-badge">
                  {tree.overall?.expectedLevel || '入门（了解基本概念与常用术语）'}
                </span>
              </div>
            </div>
            
            <div className="info-section">
              <div className="section-header">
                <div className="section-icon">📚</div>
                <h3 className="section-title">学习资源</h3>
              </div>
              <ResourceList resources={tree.overall?.resources} />
            </div>
          </div>
        ) : card ? (
        <>
          <div className="section">
            <div className="section-title">概念介绍</div>
            <div className="section-content">{card.definition}</div>
          </div>
          <div className="section">
            <div className="section-title">为什么重要</div>
            <div className="section-content">{card.importance}</div>
          </div>
          <div className="section">
            <div className="section-title">与目标的关系</div>
            {(() => {
              const path = findPathToRoot(nodeId)
              if (path.length === 0) {
                return <div className="section-content muted">未找到从该节点到目标概念的直接路径</div>
              }
              return (
                <div className="path-chips">
                  {path.map((id, idx) => (
                    <>
                      <span key={`chip-${id}-${idx}`} className="chip">{idToLabel.get(id) || id}</span>
                      {idx < path.length - 1 && (
                        <span key={`arrow-${id}-${idx}`} className="path-arrow">→</span>
                      )}
                    </>
                  ))}
                </div>
              )
            })()}
          </div>
          <div className="section">
            <div className="section-title">建议掌握等级</div>
            <div className="section-content">
              <span className="chip">{levelText(depth)}</span>
            </div>
          </div>
          <div className="section">
            <div className="section-title">前置知识</div>
            <div className="section-content">
              {node.prerequisites?.length ? (
                <div className="chips">
                  {node.prerequisites.map((p) => (
                    <span className="chip" key={p}>{idToLabel.get(p) || p}</span>
                  ))}
                </div>
              ) : '无'}
            </div>
          </div>
          <div className="section">
            <div className="section-title">学习资源</div>
            <ResourceList resources={card.resources} />
          </div>
        </>
        ) : (
          <div className="no-data-state">
            <div className="no-data-icon">📝</div>
            <h3>暂无详细信息</h3>
            <p>该概念的学习内容正在完善中，请稍后再来查看。</p>
          </div>
        )}
      </div>
      
      {/* 卡片底部操作区 */}
      <div className="card-footer">
        <div className="action-buttons">
          {!isOverall && (
            <button 
              className={`action-btn primary ${mastered ? 'mastered' : ''}`} 
              onClick={onToggleMastered}
            >
              <span className="action-icon">{mastered ? '✅' : '🎯'}</span>
              {mastered ? '取消掌握' : '标记已掌握'}
            </button>
          )}
          <button 
            className="action-btn secondary" 
            onClick={onNext}
          >
            <span className="action-icon">➡️</span>
            下一步建议
          </button>
        </div>
      </div>
    </div>
  )
}