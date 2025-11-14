# ConceptTree 项目开发规则

## 项目概述

ConceptTree 是一个基于AI的概念学习树生成工具，帮助用户通过可视化的树状结构学习复杂概念。项目采用OpenSpec规范进行开发管理。

## 技术栈

### 前端
- React 19 + Vite
- ReactFlow (图可视化)
- Tailwind CSS (样式)
- React Query (数据获取)

### 后端  
- FastAPI (Python Web框架)
- Pydantic (数据验证)
- MiniMax API (AI服务)
- Redis (缓存)

## 核心开发规则

### 1. 数据结构强制规范

#### ❌ 绝对禁止
```javascript
// 禁止使用 - 扁平数组结构
const badTree = {
  nodes: [  // 这是垃圾设计
    {id: "1", name: "概念", dependencies: ["2"]},
    {id: "2", name: "前置", dependencies: []}
  ]
};
```

#### ✅ 必须使用
```javascript
// 必须使用 - 真正的树结构
const correctTree = {
  root: {  // 正确的嵌套结构
    id: "1",
    name: "概念",
    children: [
      {
        id: "2", 
        name: "前置概念",
        children: []
      }
    ]
  }
};
```

### 2. 前端强制规则

#### TreePage组件必须修改
```typescript
interface TreePageProps {
  concept: string;
  tree: ConceptTree;  // 必须使用真正的树结构
  masteredSet: Set<string>;
  onToggleMastered: (nodeId: string) => void;
  user: User;
  onLogout: () => void;
}

// 必须使用树遍历计算进度
const calculateProgress = (root: ConceptNode, masteredSet: Set<string>) => {
  let total = 0;
  let mastered = 0;
  
  function traverse(node: ConceptNode) {
    total++;
    if (masteredSet.has(node.id)) mastered++;
    if (node.children) {
      node.children.forEach(traverse);
    }
  }
  
  traverse(root);
  return { mastered, total, percentage: total > 0 ? mastered / total : 0 };
};
```

### 3. 后端强制规则

#### ConceptTree模型重写
```python
class ConceptTree(BaseModel):
    root: ConceptNode  # 必须是根节点，不是节点数组
    target: str
    total_nodes: int
    max_depth: int
    
    @validator('total_nodes')
    def validate_node_count(cls, v, values):
        if 'root' in values:
            actual = count_nodes(values['root'])
            if v != actual:
                raise ValueError(f"节点数量不匹配")
        return v
```

#### API响应格式
```python
# 必须返回真正的树结构
@app.get("/api/concept/{concept_name}")
async def get_concept_tree(concept_name: str):
    tree = await generate_real_tree(concept_name)  # 生成真正的树
    return {
        "concept": concept_name,
        "tree": tree.model_dump(),  # 包含嵌套的children
        "cached": False
    }
```

### 4. AI服务强制要求

AI服务必须生成真正的树结构，包含嵌套的children字段，禁止输出扁平数组。

## 开发阶段要求

### 阶段0: 数据结构重构 (1-2天，必须先完成)
- 前端删除所有`tree.nodes`使用
- 后端重写ConceptTree模型
- 实现树结构验证

### 阶段1: AI服务实现 (阶段0完成后)
- AI Prompt要求输出树结构
- 实现树结构解析和验证

### 阶段2: API集成 (阶段1完成后)
- 前后端联调
- 验证数据结构一致性

## 代码审查检查单

### 必须通过
- [ ] 没有使用扁平数组结构
- [ ] 使用了真正的树遍历
- [ ] 数据结构验证完整
- [ ] 前后端结构一致

## 违规处理

任何违反树结构规范的代码都会被直接拒绝，必须完全重写。质量不容妥协。

---

**记住：先修复数据结构，再进行其他开发。这是项目成功的根基。**