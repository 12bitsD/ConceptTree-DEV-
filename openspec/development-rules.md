# 项目开发规则

## 概述

本文件定义了ConceptTree项目的严格开发规范，基于OpenSpec开发流程和DEVELOPMENT_PLAN.md的具体要求制定。所有开发人员必须严格遵守这些规则。

## 核心原则

1. **数据结构优先** - 必须先解决树结构问题，再进行其他开发
2. **规范驱动开发** - 严格按照OpenSpec提案→评审→实现→归档流程
3. **质量零容忍** - 任何不符合规范的代码都必须修正
4. **前后端协同** - 前后端必须同步按照树结构规范进行重构

## 强制规范

### 1. 树结构规范 (最高优先级)

#### ❌ 禁止使用的结构
```javascript
// 绝对禁止使用 - 扁平数组结构
const badTree = {
  nodes: [  // 这是垃圾设计
    {id: "1", name: "概念", dependencies: ["2"]},
    {id: "2", name: "前置", dependencies: []}
  ]
};
```

#### ✅ 必须使用的结构
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

### 2. 前端开发强制规则

#### TreePage组件重构要求
```typescript
// 必须修改的Props接口
interface TreePageProps {
  concept: string;
  tree: ConceptTree;  // 必须使用真正的树结构，不是扁平数组
  masteredSet: Set<string>;
  onToggleMastered: (nodeId: string) => void;
  user: User;
  onLogout: () => void;
}

// 必须实现的进度计算
const calculateProgress = (root: ConceptNode, masteredSet: Set<string>) => {
  let total = 0;
  let mastered = 0;
  
  // 必须使用树遍历，不能是数组filter
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

#### GraphView组件修改要求
- 必须支持嵌套的children结构渲染
- 必须实现树状布局算法
- 必须处理任意深度的树结构

### 3. 后端开发强制规则

#### ConceptTree模型重写
```python
# 必须重写 - 禁止使用扁平结构
class ConceptTree(BaseModel):
    root: ConceptNode  # 必须是根节点，不是节点数组
    target: str
    total_nodes: int
    max_depth: int
    
    # 必须验证树结构完整性
    @validator('total_nodes')
    def validate_node_count(cls, v, values):
        if 'root' in values:
            actual = count_nodes(values['root'])
            if v != actual:
                raise ValueError(f"节点数量不匹配: 声明{v}, 实际{actual}")
        return v

# 必须实现 - 树节点计数
def count_nodes(node: ConceptNode) -> int:
    count = 1
    if node.children:
        for child in node.children:
            count += count_nodes(child)
    return count
```

#### API响应格式强制
```python
# 必须返回真正的树结构
@app.get("/api/concept/{concept_name}")
async def get_concept_tree(concept_name: str):
    # 必须生成或获取真正的树结构
    tree = await generate_real_tree(concept_name)  # 不是扁平数据
    
    return {
        "concept": concept_name,
        "tree": tree.model_dump(),  # 包含嵌套的children
        "cached": False
    }
```

### 4. AI服务强制要求

#### 必须生成树结构
```python
# AI服务必须输出真正的树
async def generate_concept_tree(concept: str) -> ConceptTree:
    # 必须使用能生成树结构的prompt
    prompt = f"""
    生成"{concept}"的完整学习树。
    要求：
    1. 输出必须是嵌套的树结构，有children字段
    2. 每个概念必须有明确的子概念
    3. 难度必须合理分级
    4. 不能是扁平列表结构
    
    输出格式：
    {{
        "root": {{
            "id": "1",
            "name": "{concept}",
            "description": "...",
            "level": 5,
            "children": [
                {{
                    "id": "2",
                    "name": "子概念",
                    "description": "...",
                    "level": 3,
                    "children": []
                }}
            ]
        }}
    }}
    """
    
    response = await call_ai_api(prompt)
    tree_data = parse_ai_response(response)
    
    # 必须验证是树结构
    if not tree_data.get('root') or not isinstance(tree_data['root'].get('children'), list):
        raise ValueError("AI响应格式错误：缺少树结构")
    
    return ConceptTree(**tree_data)
```

## 开发流程强制执行

### 阶段0: 数据结构重构 (必须先完成)
**时间**: 1-2天，**不能跳过**

1. **前端数据结构重构** (第1天)
   - [ ] 删除所有使用`tree.nodes`的代码
   - [ ] 实现树遍历工具函数
   - [ ] 修改TreePage组件使用`tree.root`
   - [ ] 更新进度计算逻辑

2. **后端数据结构重构** (第1-2天)
   - [ ] 重写ConceptTree模型
   - [ ] 修改API返回格式
   - [ ] 实现树结构验证
   - [ ] 更新测试用例

### 阶段1: AI服务实现
**前提**: 阶段0必须100%完成并通过测试

1. **AI Prompt重构**
   - 必须要求输出树结构
   - 必须包含children字段
   - 必须验证输出格式

2. **树结构验证**
   - 验证嵌套结构完整性
   - 检查循环引用
   - 确保ID唯一性

### 阶段2: API集成
**前提**: 阶段0和1必须完成

1. **前后端联调**
   - 验证数据结构一致性
   - 测试树渲染功能
   - 性能基准测试

## 代码审查检查单

### 必须通过的审查项

#### 前端审查
- [ ] 没有使用`tree.nodes`的代码
- [ ] 使用了`tree.root`访问根节点
- [ ] 实现了树遍历函数
- [ ] 进度计算使用树遍历
- [ ] GraphView支持嵌套children

#### 后端审查  
- [ ] ConceptTree模型有root字段
- [ ] 没有返回扁平节点数组
- [ ] 实现了树结构验证
- [ ] API响应包含嵌套children
- [ ] AI服务生成真正的树结构

#### 通用审查
- [ ] 代码通过所有测试
- [ ] 类型定义完整准确
- [ ] 错误处理完善
- [ ] 性能符合要求

## 违规处罚

### 数据结构违规
- **使用扁平数组**: 代码必须完全重写
- **缺少树遍历**: 必须补充完整实现
- **结构不一致**: 必须统一修正

### 流程违规
- **跳过阶段0**: 强制回滚到阶段0
- **未经评审**: 代码拒绝合并
- **测试失败**: 禁止继续开发

## 质量保证

### 测试要求
- 树结构单元测试: 100%覆盖
- 树遍历算法测试: 各种边界情况
- 前后端数据一致性测试: 必须通过
- 性能测试: 大树渲染<2秒

### 文档要求
- 所有树结构修改必须文档化
- API变更必须更新规范
- 代码必须有完整注释
- 设计决策必须记录原因

## 时间约束

### 强制deadline
- 阶段0完成: 2天内
- 阶段1完成: 阶段0完成后3天内  
- 阶段2完成: 阶段1完成后2天内
- 整体完成: 7天内

### 进度检查点
- 每天必须提交进度报告
- 每阶段必须通过代码审查
- 每阶段必须有测试报告
- 延期必须说明具体原因

---

**最后警告**: 任何违反树结构规范的代码都会被直接拒绝。不要试图绕过这些规则，它们是为了确保项目质量而设定的最低标准。