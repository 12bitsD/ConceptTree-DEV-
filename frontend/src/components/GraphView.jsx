import { useMemo, useRef, useState, useEffect } from 'react'
import { traverseDFS } from '../utils/tree-utils.js'

function NodeBox({ node, selectedNodeId, masteredSet, onSelect, collapsed, onToggle }) {
  const cls = [
    'org-box',
    selectedNodeId === node.id ? 'current' : '',
    masteredSet.has(node.id) ? 'mastered' : '',
  ].join(' ')
  return (
    <div className="org-node">
      <div className="org-node-head">
        {Array.isArray(node.children) && node.children.length > 0 && (
          <button className="org-toggle" onClick={() => onToggle(node.id)}>{collapsed.has(node.id) ? '+' : '−'}</button>
        )}
        <button className={cls} onClick={() => onSelect(node.id)}>
          <div className="org-title">{node.name || node.id}</div>
          {node.description && <div className="org-desc">{node.description}</div>}
        </button>
      </div>
      {Array.isArray(node.children) && node.children.length > 0 && !collapsed.has(node.id) && (
        <div className="org-children">
          <div className="org-line-h" />
          <div className="org-branches">
            {node.children.map((child) => (
              <div className="org-branch" key={child.id}>
                <div className="org-line-v" />
                <div className="org-line-h-branch" />
                <NodeBox node={child} selectedNodeId={selectedNodeId} masteredSet={masteredSet} onSelect={onSelect} collapsed={collapsed} onToggle={onToggle} />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default function GraphView({ tree, masteredSet, selectedNodeId, onSelect }) {
  const stats = useMemo(() => {
    if (!tree || !tree.root) return { total: 0 }
    let total = 0
    traverseDFS(tree.root, () => { total++ })
    return { total }
  }, [tree])

  if (!tree || !tree.root) return null

  const viewportRef = useRef(null)
  const canvasRef = useRef(null)
  const [scale, setScale] = useState(1)
  const [offset, setOffset] = useState({ x: 0, y: 0 })
  const dragRef = useRef({ dragging: false, startX: 0, startY: 0, baseX: 0, baseY: 0 })
  const [collapsed, setCollapsed] = useState(new Set())
  const [isDragging, setIsDragging] = useState(false)

  useEffect(() => {
    setScale(1)
    setOffset({ x: 0, y: 0 })
    const vp = viewportRef.current
    const cv = canvasRef.current
    if (vp && cv) {
      const vw = vp.clientWidth
      const vh = vp.clientHeight
      const cw = cv.scrollWidth
      const ch = cv.scrollHeight
      const margin = 120
      const sx = vw / (cw + margin)
      const sy = vh / (ch + margin)
      const targetScale = Math.max(0.45, Math.min(1.2, Math.min(sx, sy)))
      const tx = (vw - cw * targetScale) / 2
      const ty = Math.max(20, (vh - ch * targetScale) / 2)
      setScale(targetScale)
      setOffset({ x: tx, y: ty })
    }
  }, [tree?.root?.id])

  function onWheel(e) {
    e.preventDefault()
    const delta = -e.deltaY
    const next = Math.min(2.2, Math.max(0.4, scale + (delta > 0 ? 0.1 : -0.1)))
    setScale(next)
  }

  function onMouseDown(e) {
    dragRef.current = { dragging: true, startX: e.clientX, startY: e.clientY, baseX: offset.x, baseY: offset.y }
    setIsDragging(true)
  }
  function onMouseMove(e) {
    if (!dragRef.current.dragging) return
    const dx = e.clientX - dragRef.current.startX
    const dy = e.clientY - dragRef.current.startY
    setOffset({ x: dragRef.current.baseX + dx, y: dragRef.current.baseY + dy })
  }
  function onMouseUp() { dragRef.current.dragging = false; setIsDragging(false) }
  function onMouseLeave() { dragRef.current.dragging = false; setIsDragging(false) }

  return (
    <div className="org-tree">
      <div className="org-header">
        <button className={`org-overall ${selectedNodeId === '__overall__' ? 'current' : ''}`} onClick={() => onSelect('__overall__')}>概念总览</button>
        <span className="org-stats">节点数 {stats.total}</span>
      </div>
      <div
        className={`org-viewport ${isDragging ? 'dragging' : ''}`}
        ref={viewportRef}
        onWheel={onWheel}
        onMouseDown={onMouseDown}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseUp}
        onMouseLeave={onMouseLeave}
      >
        <div className="org-canvas" ref={canvasRef} style={{ transform: `translate(${offset.x}px, ${offset.y}px) scale(${scale})` }}>
          <NodeBox node={tree.root} selectedNodeId={selectedNodeId} masteredSet={masteredSet} onSelect={onSelect} collapsed={collapsed} onToggle={(id) => {
            const next = new Set(collapsed)
            if (next.has(id)) next.delete(id)
            else next.add(id)
            setCollapsed(next)
          }} />
        </div>
      </div>
    </div>
  )
}
