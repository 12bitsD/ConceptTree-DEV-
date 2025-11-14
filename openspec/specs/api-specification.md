# API接口规范

## 基础规范

### 请求格式
- 所有请求使用JSON格式
- Content-Type: `application/json`
- 字符编码: UTF-8
- 时间格式: ISO 8601

### 响应格式
```typescript
interface ApiResponse<T> {
  success: boolean;           // 请求是否成功
  data?: T;                  // 响应数据
  error?: {
    code: string;            // 错误代码
    message: string;         // 错误信息
    details?: any;           // 详细错误信息
  };
  timestamp: string;        // 响应时间戳
  requestId?: string;       // 请求ID，用于追踪
}
```

### 错误代码规范
```typescript
enum ErrorCode {
  // 通用错误 (1xxx)
  INVALID_REQUEST = "1000",
  UNAUTHORIZED = "1001", 
  FORBIDDEN = "1002",
  NOT_FOUND = "1003",
  INTERNAL_ERROR = "1004",
  
  // 概念相关错误 (2xxx)
  CONCEPT_NOT_FOUND = "2000",
  CONCEPT_GENERATION_FAILED = "2001",
  CONCEPT_VALIDATION_ERROR = "2002",
  TREE_STRUCTURE_INVALID = "2003",
  
  // AI服务错误 (3xxx)
  AI_SERVICE_UNAVAILABLE = "3000",
  AI_RATE_LIMIT_EXCEEDED = "3001",
  AI_RESPONSE_INVALID = "3002",
  AI_TIMEOUT = "3003"
}
```

## 概念树API

### 1. 生成概念树

**POST** `/api/concept/generate`

**请求参数**:
```typescript
interface GenerateConceptRequest {
  concept: string;              // 目标概念名称
  options?: {
    maxDepth?: number;           // 最大深度 (默认: 10)
    maxNodes?: number;           // 最大节点数 (默认: 100)
    difficulty?: number;         // 起始难度等级 (默认: 5)
    includeExamples?: boolean;   // 是否包含示例 (默认: true)
    language?: string;           // 语言 (默认: "zh-CN")
  };
}
```

**响应数据**:
```typescript
interface GenerateConceptResponse {
  concept: string;              // 目标概念
  tree: ConceptTree;            // 概念树数据
  metadata: {
    generationTime: number;       // 生成耗时(毫秒)
    aiModel: string;             // 使用的AI模型
    cost?: number;               // 调用成本(如果有)
  };
}
```

**错误响应**:
- `2000`: 概念生成失败
- `3000`: AI服务不可用
- `3001`: 超过频率限制

### 2. 获取概念树

**GET** `/api/concept/{concept_name}`

**路径参数**:
- `concept_name`: string - 概念名称

**查询参数**:
- `format`: "tree" | "flat" - 返回格式 (默认: "tree")
- `include_stats`: boolean - 是否包含统计信息 (默认: true)

**响应数据**:
```typescript
interface GetConceptResponse {
  concept: string;
  tree: ConceptTree;
  cached: boolean;              // 是否来自缓存
  cacheKey?: string;            // 缓存键
}
```

**错误响应**:
- `2003`: 树结构数据损坏
- `404`: 概念不存在

### 3. 验证概念树结构

**POST** `/api/concept/validate`

**请求体**:
```typescript
interface ValidateTreeRequest {
  tree: ConceptTree;            // 待验证的树结构
}
```

**响应数据**:
```typescript
interface ValidateTreeResponse {
  valid: boolean;                 // 是否有效
  errors: ValidationError[];    // 错误列表
  warnings: ValidationWarning[]; // 警告列表
}

interface ValidationError {
  code: string;
  message: string;
  path: string;                 // 错误路径
  nodeId?: string;              // 相关节点ID
}

interface ValidationWarning {
  code: string;
  message: string;
  path: string;
  suggestion?: string;          // 改进建议
}
```

## 学习进度API

### 1. 更新节点状态

**PUT** `/api/concept/{concept_name}/node/{node_id}/status`

**请求体**:
```typescript
interface UpdateNodeStatusRequest {
  mastered: boolean;              // 是否已掌握
  learningTime?: number;          // 学习用时(分钟)
  notes?: string;                 // 学习笔记
  rating?: number;                // 难度评分(1-5)
}
```

**响应数据**:
```typescript
interface UpdateNodeStatusResponse {
  nodeId: string;
  status: "mastered" | "learning" | "pending";
  progress: {
    overall: number;              // 总体进度(0-1)
    level: number;                // 当前层级
    remainingNodes: number;       // 剩余节点数
  };
}
```

### 2. 获取学习建议

**GET** `/api/concept/{concept_name}/suggestions`

**查询参数**:
- `strategy`: "dfs" | "bfs" | "adaptive" - 学习策略 (默认: "adaptive")
- `limit`: number - 返回建议数量 (默认: 5)

**响应数据**:
```typescript
interface LearningSuggestionsResponse {
  suggestions: LearningSuggestion[];
  strategy: string;
  reasoning: string;              // 建议理由
}

interface LearningSuggestion {
  nodeId: string;
  nodeName: string;
  priority: number;               // 优先级(1-10)
  estimatedTime: number;          // 预计学习时间
  prerequisites: string[];         // 前置要求
  why: string;                    // 推荐理由
}
```

## 缓存策略

### 缓存键规范
```
concept:{concept_name}:{format}:{include_stats}
```

### 缓存时间
- 概念树数据: 24小时
- 学习进度: 实时更新，不缓存
- 学习建议: 1小时
- 验证结果: 不缓存

### 缓存控制
**请求头**:
- `Cache-Control`: "no-cache" - 强制刷新缓存

**响应头**:
- `X-Cache-Status`: "HIT" | "MISS" | "STALE"
- `X-Cache-Key`: 缓存键
- `X-Cache-TTL`: 剩余缓存时间(秒)

## 性能要求

### 响应时间
- 概念生成: < 30秒
- 概念获取: < 1秒(缓存) / < 5秒(无缓存)
- 状态更新: < 500ms
- 学习建议: < 2秒

### 并发限制
- 概念生成: 10请求/分钟/IP
- 概念获取: 100请求/分钟/IP
- 状态更新: 50请求/分钟/用户

### 数据大小限制
- 请求体: < 1MB
- 响应体: < 10MB
- 概念树节点数: < 10000
- 概念名称长度: < 100字符
- 描述长度: < 2000字符