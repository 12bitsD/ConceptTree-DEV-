/**
 * 树结构工具函数
 * 提供树遍历、查找、验证等核心功能
 */

/**
 * 深度优先遍历树节点
 * @param {Object} node - 起始节点
 * @param {Function} callback - 处理函数 (node) => void
 */
export function traverseDFS(node, callback) {
  if (!node) return
  
  callback(node)
  
  if (node.children && Array.isArray(node.children)) {
    node.children.forEach(child => {
      traverseDFS(child, callback)
    })
  }
}

/**
 * 广度优先遍历树节点
 * @param {Object} node - 起始节点
 * @param {Function} callback - 处理函数 (node) => void
 */
export function traverseBFS(node, callback) {
  if (!node) return
  
  const queue = [node]
  
  while (queue.length > 0) {
    const currentNode = queue.shift()
    callback(currentNode)
    
    if (currentNode.children && Array.isArray(currentNode.children)) {
      queue.push(...currentNode.children)
    }
  }
}

/**
 * 根据条件查找节点
 * @param {Object} root - 根节点
 * @param {Function} predicate - 查找条件 (node) => boolean
 * @returns {Object|null} 找到的节点或null
 */
export function findNode(root, predicate) {
  if (!root || !predicate) return null
  
  if (predicate(root)) {
    return root
  }
  
  if (root.children && Array.isArray(root.children)) {
    for (const child of root.children) {
      const result = findNode(child, predicate)
      if (result) return result
    }
  }
  
  return null
}

/**
 * 根据ID查找节点
 * @param {Object} root - 根节点
 * @param {string} nodeId - 节点ID
 * @returns {Object|null} 找到的节点或null
 */
export function findNodeById(root, nodeId) {
  return findNode(root, node => node.id === nodeId)
}

/**
 * 获取节点在树中的层级
 * @param {Object} targetNode - 目标节点
 * @param {Object} root - 根节点
 * @returns {number} 层级数字 (根节点为0)
 */
export function getNodeLevel(targetNode, root) {
  if (!targetNode || !root) return -1
  
  function findLevel(node, targetId, currentLevel) {
    if (node.id === targetId) {
      return currentLevel
    }
    
    if (node.children && Array.isArray(node.children)) {
      for (const child of node.children) {
        const level = findLevel(child, targetId, currentLevel + 1)
        if (level !== -1) return level
      }
    }
    
    return -1
  }
  
  return findLevel(root, targetNode.id, 0)
}

/**
 * 统计子树中的节点总数
 * @param {Object} node - 起始节点
 * @returns {number} 节点数量
 */
export function countNodes(node) {
  if (!node) return 0
  
  let count = 1
  
  if (node.children && Array.isArray(node.children)) {
    node.children.forEach(child => {
      count += countNodes(child)
    })
  }
  
  return count
}

/**
 * 按层级分组获取所有节点
 * @param {Object} root - 根节点
 * @returns {Map<number, Array>} Map<level, ConceptNode[]>
 */
export function getNodesByLevel(root) {
  const levelMap = new Map()
  
  if (!root) return levelMap
  
  traverseBFS(root, (node) => {
    const level = getNodeLevel(node, root)
    if (!levelMap.has(level)) {
      levelMap.set(level, [])
    }
    levelMap.get(level).push(node)
  })
  
  return levelMap
}

/**
 * 验证树结构完整性
 * @param {Object} node - 根节点
 * @returns {Object} {valid: boolean, errors: string[]}
 */
export function validateTree(node) {
  const errors = []
  const visitedIds = new Set()
  
  function validateNode(currentNode, path = []) {
    if (!currentNode) {
      errors.push('节点不能为空')
      return
    }
    
    if (!currentNode.id) {
      errors.push('节点必须包含id字段')
      return
    }
    
    // 检查ID唯一性
    if (visitedIds.has(currentNode.id)) {
      errors.push(`检测到重复的节点ID: ${currentNode.id}`)
    }
    visitedIds.add(currentNode.id)
    
    // 检查循环引用
    if (path.includes(currentNode.id)) {
      errors.push(`检测到循环引用: ${currentNode.id}`)
      return
    }
    
    const newPath = [...path, currentNode.id]
    
    if (currentNode.children && Array.isArray(currentNode.children)) {
      currentNode.children.forEach(child => {
        validateNode(child, newPath)
      })
    }
  }
  
  validateNode(node)
  
  return {
    valid: errors.length === 0,
    errors
  }
}

/**
 * 将树结构扁平化为数组
 * @param {Object} node - 根节点
 * @returns {Array} 节点数组
 */
export function flattenTree(node) {
  const result = []
  
  traverseDFS(node, (n) => {
    result.push(n)
  })
  
  return result
}

/**
 * 从扁平数据构建树结构
 * @param {Array} nodes - 扁平节点数组
 * @param {string} rootId - 根节点ID
 * @returns {Object} 树结构根节点
 */
export function buildTreeFromFlat(nodes, rootId) {
  if (!nodes || !Array.isArray(nodes) || nodes.length === 0) {
    return null
  }
  
  const nodeMap = new Map()
  
  // 创建节点映射
  nodes.forEach(node => {
    nodeMap.set(node.id, { ...node, children: [] })
  })
  
  let root = null
  
  // 构建树结构
  nodes.forEach(node => {
    const currentNode = nodeMap.get(node.id)
    
    if (node.id === rootId) {
      root = currentNode
    }
    
    // 如果有父节点ID，添加到父节点的children中
    if (node.parentId) {
      const parentNode = nodeMap.get(node.parentId)
      if (parentNode) {
        if (!parentNode.children) {
          parentNode.children = []
        }
        parentNode.children.push(currentNode)
      }
    }
    
    // 如果有依赖关系，构建子节点
    if (node.dependencies && Array.isArray(node.dependencies)) {
      node.dependencies.forEach(depId => {
        const childNode = nodeMap.get(depId)
        if (childNode) {
          if (!currentNode.children) {
            currentNode.children = []
          }
          currentNode.children.push(childNode)
        }
      })
    }
  })
  
  return root
}

/**
 * 获取节点的所有祖先节点
 * @param {Object} targetNode - 目标节点
 * @param {Object} root - 根节点
 * @returns {Array} 祖先节点数组
 */
export function getAncestors(targetNode, root) {
  const ancestors = []
  
  function findPath(node, targetId, path = []) {
    if (node.id === targetId) {
      return path
    }
    
    if (node.children && Array.isArray(node.children)) {
      for (const child of node.children) {
        const result = findPath(child, targetId, [...path, node])
        if (result) return result
      }
    }
    
    return null
  }
  
  const path = findPath(root, targetNode.id)
  return path || []
}

/**
 * 获取节点的所有后代节点
 * @param {Object} node - 起始节点
 * @returns {Array} 后代节点数组
 */
export function getDescendants(node) {
  const descendants = []
  
  traverseDFS(node, (n) => {
    if (n !== node) { // 排除自身
      descendants.push(n)
    }
  })
  
  return descendants
}

/**
 * 计算两个节点之间的路径
 * @param {Object} fromNode - 起始节点
 * @param {Object} toNode - 目标节点
 * @param {Object} root - 根节点
 * @returns {Array} 路径节点数组
 */
export function getPath(fromNode, toNode, root) {
  if (!fromNode || !toNode || !root) return []
  
  // 获取从根节点到目标节点的路径
  function getNodePath(targetId, currentNode, path = []) {
    const newPath = [...path, currentNode]
    
    if (currentNode.id === targetId) {
      return newPath
    }
    
    if (currentNode.children && Array.isArray(currentNode.children)) {
      for (const child of currentNode.children) {
        const result = getNodePath(targetId, child, newPath)
        if (result) return result
      }
    }
    
    return null
  }
  
  const fromPath = getNodePath(fromNode.id, root)
  const toPath = getNodePath(toNode.id, root)
  
  if (!fromPath || !toPath) return []
  
  // 找到最近公共祖先
  let lcaIndex = 0
  for (let i = 0; i < Math.min(fromPath.length, toPath.length); i++) {
    if (fromPath[i].id === toPath[i].id) {
      lcaIndex = i
    } else {
      break
    }
  }
  
  // 构建路径
  const upPath = fromPath.slice(lcaIndex + 1).reverse()
  const downPath = toPath.slice(lcaIndex + 1)
  
  return [...upPath, fromPath[lcaIndex], ...downPath]
}

/**
 * 克隆树结构（深拷贝）
 * @param {Object} node - 要克隆的节点
 * @returns {Object} 克隆后的节点
 */
export function cloneTree(node) {
  if (!node) return null
  
  const cloned = { ...node }
  
  if (node.children && Array.isArray(node.children)) {
    cloned.children = node.children.map(child => cloneTree(child))
  }
  
  return cloned
}

/**
 * 比较两棵树是否相等
 * @param {Object} node1 - 第一棵树
 * @param {Object} node2 - 第二棵树
 * @returns {boolean} 是否相等
 */
export function compareTrees(node1, node2) {
  if (!node1 && !node2) return true
  if (!node1 || !node2) return false
  
  if (node1.id !== node2.id) return false
  
  const children1 = node1.children || []
  const children2 = node2.children || []
  
  if (children1.length !== children2.length) return false
  
  return children1.every((child1, index) => 
    compareTrees(child1, children2[index])
  )
}