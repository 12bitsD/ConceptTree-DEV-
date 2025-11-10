import { useMemo } from 'react'

function buildPrereqMap(tree) {
  const map = new Map()
  for (const n of tree.nodes) {
    map.set(n.id, n.prerequisites || [])
  }
  return map
}

export default function GraphView({ tree, masteredSet, selectedNodeId, onSelect }) {
  const idToNode = useMemo(() => {
    const m = new Map()
    tree.nodes.forEach((n) => m.set(n.id, n))
    return m
  }, [tree])

  const prereqMap = useMemo(() => buildPrereqMap(tree), [tree])

  // 新 UI：按层级展示为横向行，每层若干节点 chip
  const rootId = tree.root || tree.nodes[0]?.id

  function buildLevels() {
    if (!rootId) return []
    const levels = []
    const visited = new Set()
    let current = [rootId]
    while (current.length) {
      const unique = Array.from(new Set(current)).filter((id) => idToNode.has(id))
      levels.push(unique)
      const next = []
      for (const id of unique) {
        visited.add(id)
        const children = prereqMap.get(id) || []
        for (const c of children) {
          if (!visited.has(c)) next.push(c)
        }
      }
      current = next
    }
    return levels
  }

  const levels = useMemo(buildLevels, [rootId, prereqMap, idToNode])
  const effectiveLevels = useMemo(() => levels.slice(1), [levels])

  return (
    <div className="graph-grid">
      <div className="graph-row overall-row">
        <div className="row-title">总体</div>
        <div className="row-nodes">
          <button
            className={`node-chip ${selectedNodeId === '__overall__' ? 'current' : ''}`}
            onClick={() => onSelect('__overall__')}
          >概念总览</button>
          <button
            className={`node-chip ${selectedNodeId === rootId ? 'current' : ''} ${masteredSet.has(rootId) ? 'mastered' : ''}`}
            onClick={() => onSelect(rootId)}
          >{idToNode.get(rootId)?.label || rootId}</button>
        </div>
      </div>
      {effectiveLevels.map((ids, idx) => (
        <div className="graph-row" key={idx}>
          <div className="row-title">层级 {idx}</div>
          <div className="row-nodes">
            {ids.map((id) => {
              const node = idToNode.get(id)
              const cls = [
                'node-chip',
                selectedNodeId === id ? 'current' : '',
                masteredSet.has(id) ? 'mastered' : '',
              ].join(' ')
              return (
                <button className={cls} key={id} onClick={() => onSelect(id)}>
                  {node?.label || id}
                </button>
              )
            })}
          </div>
        </div>
      ))}
    </div>
  )
}