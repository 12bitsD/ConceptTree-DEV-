# 数据结构规范

## 概念树数据结构 (ConceptTree)

### 核心原则
- 使用真正的树状结构，非扁平数组
- 支持嵌套children，支持无限层级
- 每个节点包含完整的元数据
- 支持多种遍历算法

### 树节点结构 (ConceptNode)

```typescript
interface ConceptNode {
  // 基础属性
  id: string;                    // 唯一标识符
  name: string;                  // 概念名称
  description: string;           // 详细描述
  level: number;                 // 难度等级 (0-10)
  
  // 树结构属性
  children?: ConceptNode[];      // 子节点数组
  parent?: string;               // 父节点ID (可选，用于反向查找)
  
  // 学习相关属性
  mastered?: boolean;            // 是否已掌握
  estimatedTime?: number;        // 预计学习时间(分钟)
  prerequisites?: string[];      // 前置概念ID列表
  
  // 元数据
  metadata?: {
    tags?: string[];             // 概念标签
    category?: string;           // 概念分类
    importance?: number;         // 重要程度 (1-5)
    complexity?: number;         // 复杂度 (1-5)
  };
}
```

### 概念树结构 (ConceptTree)

```typescript
interface ConceptTree {
  // 根节点
  root: ConceptNode;
  
  // 元数据
  target: string;                // 目标概念名称
  totalNodes: number;            // 总节点数
  maxDepth: number;              // 最大深度
  
  // 统计信息
  stats: {
    masteredNodes: number;       // 已掌握节点数
    totalLearningTime: number;   // 总学习时间
    completionRate: number;      // 完成率 (0-1)
  };
  
  // 生成信息
  generatedAt: string;             // ISO时间戳
  version: string;                // 数据格式版本
}
```

## 遍历算法规范

### 深度优先遍历 (DFS)
```javascript
function dfsTraversal(node: ConceptNode, callback: (node: ConceptNode) => void) {
  callback(node);
  if (node.children) {
    node.children.forEach(child => dfsTraversal(child, callback));
  }
}
```

### 广度优先遍历 (BFS)
```javascript
function bfsTraversal(root: ConceptNode, callback: (node: ConceptNode) => void) {
  const queue = [root];
  while (queue.length > 0) {
    const node = queue.shift();
    callback(node);
    if (node.children) {
      queue.push(...node.children);
    }
  }
}
```

### 层级遍历
```javascript
function getNodesByLevel(root: ConceptNode): Map<number, ConceptNode[]> {
  const levels = new Map();
  bfsTraversal(root, (node) => {
    const level = getNodeLevel(node);
    if (!levels.has(level)) levels.set(level, []);
    levels.get(level).push(node);
  });
  return levels;
}
```

## 数据验证规则

### 必填字段验证
- `id`: 必须存在，必须是字符串，必须唯一
- `name`: 必须存在，必须是字符串，长度>0
- `description`: 必须存在，必须是字符串，长度>10
- `level`: 必须存在，必须是整数，范围0-10

### 结构完整性验证
- 所有节点ID必须在树中唯一
- 子节点数组必须有效（不存在循环引用）
- 父节点引用必须有效（如果存在）
- 树必须连通（所有节点都能从根节点访问到）

### 业务逻辑验证
- 难度等级必须合理（前置概念难度 < 当前概念难度）
- 学习时间必须为正数
- 重要程度和复杂度必须在有效范围内

## 序列化格式

### JSON序列化
```json
{
  "root": {
    "id": "1",
    "name": "机器学习",
    "description": "机器学习的核心概念...",
    "level": 5,
    "children": [
      {
        "id": "2",
        "name": "线性代数",
        "description": "数学基础...",
        "level": 3,
        "children": [...]
      }
    ]
  },
  "target": "机器学习",
  "totalNodes": 15,
  "maxDepth": 4,
  "stats": {
    "masteredNodes": 3,
    "totalLearningTime": 480,
    "completionRate": 0.2
  },
  "generatedAt": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

## 性能要求

### 时间复杂度
- 节点查找: O(n)
- 树遍历: O(n)
- 层级计算: O(n)
- 完整性验证: O(n)

### 空间复杂度
- 树存储: O(n)
- 遍历栈空间: O(h) (h为树高度)
- 临时缓存: O(n)

### 大小限制
- 单棵树最大节点数: 10000
- 最大深度: 20
- 单个节点描述长度: < 1000字符
- 元数据字段数量: < 50