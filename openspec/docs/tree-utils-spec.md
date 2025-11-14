# 树结构工具函数

## 概述
提供树结构相关的核心工具函数，用于前端组件处理嵌套的树数据。

## 函数列表

### traverseDFS(node, callback)
深度优先遍历树节点。

**参数:**
- `node`: ConceptNode - 起始节点
- `callback`: (node: ConceptNode) => void - 处理函数

**示例:**
```javascript
import { traverseDFS } from './tree-utils';

traverseDFS(tree.root, (node) => {
  console.log(node.name);
});
```

### traverseBFS(node, callback)
广度优先遍历树节点。

**参数:**
- `node`: ConceptNode - 起始节点  
- `callback`: (node: ConceptNode) => void - 处理函数

**示例:**
```javascript
traverseBFS(tree.root, (node) => {
  console.log(node.name);
});
```

### findNode(root, predicate)
根据条件查找节点。

**参数:**
- `root`: ConceptNode - 根节点
- `predicate`: (node: ConceptNode) => boolean - 查找条件

**返回:** 找到的节点或null

**示例:**
```javascript
const node = findNode(tree.root, (n) => n.id === "123");
```

### getNodeLevel(node, root)
获取节点在树中的层级。

**参数:**
- `node`: ConceptNode - 目标节点
- `root`: ConceptNode - 根节点

**返回:** 层级数字 (根节点为0)

### countNodes(node)
统计子树中的节点总数。

**参数:**
- `node`: ConceptNode - 起始节点

**返回:** 节点数量

### getNodesByLevel(root)
按层级分组获取所有节点。

**参数:**
- `root`: ConceptNode - 根节点

**返回:** Map<level, ConceptNode[]>

**示例:**
```javascript
const levelMap = getNodesByLevel(tree.root);
// 返回: {0: [root], 1: [child1, child2], ...}
```

### validateTree(node)
验证树结构完整性。

**参数:**
- `node`: ConceptNode - 根节点

**返回:** {valid: boolean, errors: string[]}

### flattenTree(node)
将树结构扁平化为数组（用于特定场景）。

**参数:**
- `node`: ConceptNode - 根节点

**返回:** ConceptNode[]

### buildTreeFromFlat(nodes, rootId)
从扁平数据构建树结构。

**参数:**
- `nodes`: FlatNode[] - 扁平节点数组
- `rootId`: string - 根节点ID

**返回:** ConceptNode（树结构）

## 使用示例

```javascript
import { 
  traverseDFS, 
  findNode, 
  countNodes,
  getNodesByLevel 
} from './tree-utils';

// 计算学习进度
function calculateProgress(root, masteredSet) {
  let total = 0;
  let mastered = 0;
  
  traverseDFS(root, (node) => {
    total++;
    if (masteredSet.has(node.id)) {
      mastered++;
    }
  });
  
  return {
    mastered,
    total, 
    percentage: total > 0 ? mastered / total : 0
  };
}

// 获取推荐学习节点
function getRecommendedNodes(root, currentLevel) {
  const levelNodes = getNodesByLevel(root).get(currentLevel + 1) || [];
  return levelNodes.filter(node => !node.mastered);
}

// 查找前置概念
function findPrerequisites(root, targetNodeId) {
  const target = findNode(root, n => n.id === targetNodeId);
  if (!target || !target.prerequisites) return [];
  
  return target.prerequisites.map(prereqId => 
    findNode(root, n => n.id === prereqId)
  ).filter(Boolean);
}
```

## 性能说明

- 所有遍历函数时间复杂度: O(n)
- 空间复杂度: O(h) (h为树高度)
- 适用于大型树结构 (测试通过10000+节点)

## 错误处理

所有函数都会进行参数验证:
- 空节点处理
- 循环引用检测  
- 数据类型验证
- 边界情况处理

## 测试覆盖

- 单元测试: 100%覆盖
- 集成测试: 主要使用场景
- 性能测试: 大数据集验证
- 边界测试: 空树、单节点、循环引用