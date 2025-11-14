# AI服务规范

## 核心原则
- 生成真正的树状结构，非扁平列表
- 概念间必须有明确的依赖关系
- 难度分级必须合理且一致
- 输出格式必须严格符合数据结构规范

## 输入规范

### 概念生成请求
```typescript
interface AIConceptRequest {
  concept: string;              // 目标概念
  context?: {
    domain?: string;            // 领域(计算机、数学等)
    audience?: string;          // 受众(初学者、进阶等)
    depth?: number;             // 深度要求(1-10)
    breadth?: number;           // 广度要求(1-10)
  };
  constraints?: {
    maxNodes?: number;          // 最大节点数
    maxDepth?: number;          // 最大深度
    minPrerequisites?: number;  // 最小前置概念数
    language?: string;          // 输出语言
  };
}
```

## 输出规范

### 概念树输出
```typescript
interface AIConceptResponse {
  tree: {
    name: string;               // 根概念名称
    description: string;          // 详细描述
    level: number;               // 难度等级(1-10)
    children: AIConceptNode[];    // 子概念数组
  };
  metadata: {
    totalNodes: number;           // 总节点数
    maxDepth: number;             // 最大深度
    complexityScore: number;      // 复杂度评分
    estimatedLearningTime: number; // 预计学习时间(小时)
  };
}

interface AIConceptNode {
  name: string;                 // 概念名称
  description: string;           // 概念描述
  level: number;                 // 难度等级(1-10)
  learningTime: number;          // 学习时间(分钟)
  importance: number;             // 重要程度(1-5)
  children?: AIConceptNode[];    // 子概念(可选)
  prerequisites?: string[];     // 前置概念名称列表
  examples?: string[];          // 示例列表
  commonMisconceptions?: string[]; // 常见误解
}
```

## Prompt模板

### 概念树生成Prompt
```
你是一个专业的教育内容设计师。请为"{concept}"概念创建一个完整的学习树。

要求：
1. 生成真正的树状结构，每个概念有明确的子概念
2. 概念间必须有合理的依赖关系
3. 难度分级要准确且一致
4. 输出必须符合JSON格式规范

上下文信息：
- 领域：{domain}
- 受众：{audience}  
- 深度要求：{depth}/10
- 广度要求：{breadth}/10

约束条件：
- 最大节点数：{maxNodes}
- 最大深度：{maxDepth}
- 输出语言：{language}

输出格式要求：
{format_specification}

请确保：
1. 根概念就是用户请求的概念
2. 每个概念都有清晰的学习路径
3. 难度等级从基础(1)到高级(10)
4. 描述要详细且易于理解
5. 包含实际的学习时间估算

返回纯JSON，不要有任何额外解释。
```

## 质量要求

### 概念质量
- 概念名称必须准确且无歧义
- 描述必须清晰、简洁、准确
- 难度分级必须合理且一致
- 学习时间估算必须现实可行

### 结构质量
- 必须是真正的树结构（有children数组）
- 概念间依赖关系必须合理
- 不能有循环依赖
- 深度和广度必须平衡

### 格式质量
- 必须是有效的JSON格式
- 所有必填字段必须存在
- 数据类型必须正确
- 字符串必须进行适当的转义

## 错误处理

### 生成失败
```typescript
interface AIGenerationError {
  type: "generation_failed";
  reason: string;
  suggestion?: string;
  fallback?: string[]; // 建议的替代概念
}
```

### 解析失败
```typescript
interface AIParseError {
  type: "parse_failed";
  rawResponse: string;
  parseError: string;
  attemptedFix?: boolean;
}
```

### 内容质量问题
```typescript
interface AIQualityError {
  type: "quality_issue";
  issues: string[];
  severity: "low" | "medium" | "high";
  autoFixable: boolean;
}
```

## 性能要求

### 响应时间
- 简单概念（<50节点）: < 10秒
- 中等概念（50-200节点）: < 30秒
- 复杂概念（>200节点）: < 60秒

### 重试策略
- 第一次失败：等待2秒后重试
- 第二次失败：等待5秒后重试
- 第三次失败：返回错误，不再重试

### 缓存策略
- 相同概念请求：缓存24小时
- 相似概念请求：缓存6小时
- 错误响应：缓存1小时（避免重复失败）

## 内容审核

### 安全检查
- 概念内容必须适合教育用途
- 不能包含不当内容
- 不能传播错误信息
- 必须符合教育伦理

### 准确性验证
- 概念定义必须准确
- 依赖关系必须正确
- 难度分级必须合理
- 学习时间必须现实

### 一致性检查
- 同一概念的不同部分必须一致
- 相关概念的难度关系必须合理
- 描述风格必须统一
- 术语使用必须一致