export function topoSort(tree) {
  const ids = tree.nodes.map((n) => n.id)
  const indegree = new Map()
  const dependents = new Map() // a -> [b...], b depends on a
  ids.forEach((id) => {
    indegree.set(id, 0)
    dependents.set(id, [])
  })
  for (const n of tree.nodes) {
    const pres = n.prerequisites || []
    indegree.set(n.id, pres.length)
    for (const p of pres) {
      if (!dependents.has(p)) dependents.set(p, [])
      dependents.get(p).push(n.id)
    }
  }
  const queue = []
  for (const [id, deg] of indegree.entries()) {
    if (deg === 0) queue.push(id)
  }
  const order = []
  while (queue.length) {
    const a = queue.shift()
    order.push(a)
    for (const b of dependents.get(a) || []) {
      indegree.set(b, indegree.get(b) - 1)
      if (indegree.get(b) === 0) queue.push(b)
    }
  }
  return order
}

export function nextSuggestion(tree, masteredSet) {
  const order = topoSort(tree)
  return order.find((id) => !masteredSet.has(id))
}