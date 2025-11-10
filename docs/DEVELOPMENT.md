# 开发文档

## 前端界面

**访问地址:** `http://localhost:5173`（所有页面都在这个URL，通过状态切换）

### 1. 首页 (Home Page)
**文件:** `frontend/src/App.jsx`

**显示条件:** `page === 'home'`

**功能:**
- 用户输入概念名称
- 用户登录/退出

**API调用:**
| 操作 | API端点 | 方法 | 函数 | 后端文件 |
|-----|---------|------|------|---------|
| 点击"生成依赖树"按钮 | `/api/concept/{concept_name}` | GET | `handleLoadTree()` | `backend/app/api/concept.py` 的 `get_concept_tree()` |

**说明:**
- 用户输入概念后，调用后端获取依赖树数据
- 成功后切换到树页面，失败显示错误

---

### 2. 加载页 (Loading Page)
**文件:** `frontend/src/components/LoadingStages.jsx`

**显示条件:** `page === 'loading'`

**功能:**
- 显示加载动画

**API调用:**
- 无

---

### 3. 依赖树页面 (Tree Page)
**文件:** `frontend/src/pages/TreePage.jsx`

**显示条件:** `page === 'tree'`

**功能:**
- 显示概念依赖树图谱
- 查看节点详情
- 标记已掌握概念
- 显示学习进度
- 阅读模式切换
- 用户退出

**API调用:**
- 无（使用首页获取的数据）

**说明:**
- 所有数据来自首页调用API返回的结果
- 进度保存在浏览器LocalStorage，不调用后端

---

## 后端状态

**⚠️ 后端仅返回mock数据，AI服务未实现**

### API端点

| 端点 | 方法 | 文件 | 状态 |
|-----|------|------|------|
| `/api/concept/{concept_name}` | GET | `backend/app/api/concept.py` | ⚠️ 仅返回mock数据 |
| `/health` | GET | `backend/app/main.py` | ✅ 已实现 |

### 当前实现

**文件:** `backend/app/api/concept.py`

- 接收概念名称参数
- 返回硬编码的mock数据
- AI服务未调用

**AI服务状态:**
- `backend/app/services/ai_service.py` - ❌ 空文件，未实现
