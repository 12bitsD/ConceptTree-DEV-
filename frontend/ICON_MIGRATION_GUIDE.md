# 🔄 图标迁移指南
## 从 Emoji 迁移到 SVG Icon 组件

---

## 📋 迁移清单

### LoadingStages.jsx
**文件路径：** `src/components/LoadingStages.jsx`

```jsx
// ❌ 修改前 - 使用 emoji
const LOADING_STAGES = [
  { id: 1, message: '// Initializing CodeMonkey...', icon: '🐵', duration: 800 },
  { id: 2, message: '// Analyzing concept structure...', icon: '🔍', duration: 1200 },
  { id: 3, message: '// Building dependency tree...', icon: '🌲', duration: 1500 },
  { id: 4, message: '// Optimizing learning path...', icon: '🎯', duration: 1000 },
  { id: 5, message: '// Ready to learn!', icon: '✨', duration: 500 }
]

// 使用
<span className="stage-icon">{currentStageData.icon}</span>
```

```jsx
// ✅ 修改后 - 使用 Icon 组件
import Icon from './Icon'

const LOADING_STAGES = [
  { id: 1, message: '// Initializing CodeMonkey...', icon: 'monkey', duration: 800 },
  { id: 2, message: '// Analyzing concept structure...', icon: 'search', duration: 1200 },
  { id: 3, message: '// Building dependency tree...', icon: 'tree', duration: 1500 },
  { id: 4, message: '// Optimizing learning path...', icon: 'target', duration: 1000 },
  { id: 5, message: '// Ready to learn!', icon: 'sparkles', duration: 500 }
]

// 使用
<Icon name={currentStageData.icon} size={48} className="stage-icon" />
```

---

### TreePage.jsx
**文件路径：** `src/pages/TreePage.jsx`

```jsx
// ❌ 修改前
<span>👤 {user.name}</span>
{isReadingMode ? '📖 退出阅读' : '📝 阅读模式'}
<div className="empty-icon">🎯</div>
```

```jsx
// ✅ 修改后
import Icon from '../components/Icon'

<Icon name="user" size={20} color="text" />
<span>{user.name}</span>

<Icon name={isReadingMode ? "book-open" : "edit"} size={18} />
<span>{isReadingMode ? ' 退出阅读' : ' 阅读模式'}</span>

<Icon name="target" size={64} className="empty-icon" />
```

---

### ConceptCard.jsx
**文件路径：** `src/components/ConceptCard.jsx`

```jsx
// ❌ 修改前
<span className="status-icon">{mastered ? '✅' : '⏳'}</span>
{isReadingMode ? '📖' : '📝'}
<div className="section-icon">🎯</div>
<div className="section-icon">📊</div>
<div className="section-icon">📚</div>
<div className="no-data-icon">📝</div>
<span className="action-icon">{mastered ? '✅' : '🎯'}</span>
<span className="action-icon">➡️</span>
```

```jsx
// ✅ 修改后
import Icon from './Icon'

<Icon name={mastered ? "checkmark" : "clock"} size={20} className="status-icon" />
<Icon name={isReadingMode ? "book-open" : "edit"} size={18} />
<Icon name="target" size={32} className="section-icon" />
<Icon name="chart" size={32} className="section-icon" />
<Icon name="books" size={32} className="section-icon" />
<Icon name="edit" size={48} className="no-data-icon" />
<Icon name={mastered ? "checkmark" : "target"} size={20} className="action-icon" />
<Icon name="arrow-right" size={20} className="action-icon" />
```

---

### Toolbar.jsx
**文件路径：** `src/components/Toolbar.jsx`

```jsx
// ❌ 修改前
🔍 搜索
{isReadingMode ? "📖 阅读模式" : "📝 专注阅读"}
<span className="user-avatar">👤</span>
```

```jsx
// ✅ 修改后
import Icon from './Icon'

<Icon name="search" size={16} /> 搜索
<Icon name={isReadingMode ? "book-open" : "edit"} size={16} />
<span>{isReadingMode ? " 阅读模式" : " 专注阅读"}</span>
<Icon name="user" size={24} className="user-avatar" />
```

---

## 🎨 CSS 样式调整建议

### 移除emoji特定样式

```css
/* ❌ 删除这些 - 不再需要 */
.stage-icon {
  font-size: 48px;
  display: block;
  margin-bottom: var(--space-sm);
  animation: bounce 1s ease-in-out infinite;
}
```

```css
/* ✅ 改为这些 - 适配SVG图标 */
.stage-icon {
  display: block;
  margin: 0 auto var(--space-sm);
  animation: bounce 1s ease-in-out infinite;
}

/* Icon组件会自动处理尺寸，无需font-size */
```

---

## 🔧 迁移步骤

### Step 1: 确保图标文件已生成
检查 `frontend/public/icons/` 文件夹中是否有所需的SVG文件。

### Step 2: 导入Icon组件
在需要使用图标的文件顶部添加：
```jsx
import Icon from './Icon' // 或 '../components/Icon'
```

### Step 3: 查找替换
使用编辑器的查找替换功能：

**查找模式（正则）：**
```regex
['"`]([🐵🔍🌲🎯✨👤📖📝✅⏳📊📚➡️])['"`]
```

**替换策略：**
- 🐵 → `<Icon name="monkey" size={SIZE} />`
- 🔍 → `<Icon name="search" size={SIZE} />`
- 🌲 → `<Icon name="tree" size={SIZE} />`
- 🎯 → `<Icon name="target" size={SIZE} />`
- ✨ → `<Icon name="sparkles" size={SIZE} />`
- 👤 → `<Icon name="user" size={SIZE} />`
- 📖 → `<Icon name="book-open" size={SIZE} />`
- 📝 → `<Icon name="edit" size={SIZE} />`
- ✅ → `<Icon name="checkmark" size={SIZE} />`
- ⏳ → `<Icon name="clock" size={SIZE} />`
- 📊 → `<Icon name="chart" size={SIZE} />`
- 📚 → `<Icon name="books" size={SIZE} />`
- ➡️ → `<Icon name="arrow-right" size={SIZE} />`

### Step 4: 调整尺寸
根据使用场景调整 `size` 属性：
- 装饰小图标：16-20px
- 常规图标：24-32px
- 大图标/特征图标：48-64px

### Step 5: 测试
- 运行开发服务器：`npm run dev`
- 检查所有图标是否正常显示
- 测试不同屏幕尺寸下的效果

---

## 🎯 Icon组件使用技巧

### 基础用法
```jsx
<Icon name="monkey" size={24} />
```

### 使用预设颜色
```jsx
<Icon name="search" size={24} color="primary" />    // 橙色
<Icon name="tree" size={24} color="secondary" />    // 青绿色
<Icon name="user" size={24} color="text" />         // 深灰色
```

### 自定义颜色
```jsx
<Icon name="target" size={24} color="#FF0000" />
```

### 添加CSS类
```jsx
<Icon name="sparkles" size={32} className="icon-animate" />
```

### 条件渲染
```jsx
<Icon name={isActive ? "checkmark" : "clock"} size={20} />
```

---

## ⚠️ 注意事项

1. **尺寸统一：** 同一场景的图标保持相同尺寸
2. **颜色一致：** 遵循设计系统的颜色规范
3. **语义化：** 确保图标名称语义清晰
4. **可访问性：** 重要图标添加 aria-label
5. **性能：** 避免在循环中使用过大的图标

---

## 📊 迁移进度追踪

- [ ] LoadingStages.jsx - 5个图标
- [ ] TreePage.jsx - 3个图标
- [ ] ConceptCard.jsx - 8个图标
- [ ] Toolbar.jsx - 3个图标
- [ ] 其他组件检查

---

## ✅ 迁移完成检查

- [ ] 所有emoji已替换为Icon组件
- [ ] 导入语句正确添加
- [ ] 图标尺寸合理
- [ ] 颜色符合设计系统
- [ ] 无控制台错误
- [ ] 移动端显示正常
- [ ] 更新README清单

---

**迁移完成后，你的应用将拥有：**
- ✨ 统一的视觉风格
- 🎨 更好的品牌一致性
- 📱 更清晰的图标显示
- 🔧 更灵活的定制能力
- ⚡ 更好的性能（SVG vs emoji）
