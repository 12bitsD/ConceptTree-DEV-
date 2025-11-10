# CodeMonkey Icon Design Prompts
## 图标设计规范与AI生成提示词

---

## 🎨 整体设计风格要求

**设计系统参考：** CodeMonkey Design System

**核心风格：**
- **极简线条**：简洁、现代的线条图标
- **品牌色彩**：橙色 (#FF9538) 和青绿色 (#16AA98)
- **边框特征**：1.5-2px 的描边，符合 CodeMonkey 手绘感
- **圆角处理**：轻微圆角，友好亲切
- **代码文化**：融入编程和技术元素
- **统一尺寸**：64x64px，SVG格式，可缩放

**技术规格：**
- 格式：SVG
- 尺寸：64x64px (viewBox="0 0 64 64")
- 描边宽度：2px
- 颜色：主要使用 #FF9538 (橙色) 和 #16AA98 (青绿色)
- 背景：透明
- 风格：扁平化、线条图标（line icon）

---

## 📋 所需图标清单

### 1. 核心品牌图标

#### monkey.svg - 猴子图标
**用途：** 品牌Logo、加载动画主视觉
**使用场景：** 首页Logo、加载页面中心
**Prompt：**
```
Create a minimalist line icon of a cute monkey face in CodeMonkey brand style.
- Style: Simple line art, geometric shapes
- Color: Orange (#FF9538) outline with 2px stroke
- Features: Round face, two dot eyes, curved smile, small ears
- Elements: Include subtle code brackets "{}" integrated into the design
- Size: 64x64px SVG, centered
- Mood: Friendly, approachable, tech-savvy
- Background: Transparent
```

---

### 2. 加载阶段图标（Loading Stages Icons）

#### search.svg - 搜索/分析图标
**用途：** 加载阶段 - "分析概念结构"
**替换：** 🔍
**Prompt：**
```
Create a minimalist magnifying glass icon with code elements.
- Style: Line art with 2px stroke
- Color: Teal (#16AA98)
- Features: Classic magnifying glass shape with code symbols "<>" visible in the lens
- Size: 64x64px SVG
- Details: Clean, geometric, slightly tilted angle (15 degrees)
- Background: Transparent
```

#### tree.svg - 树/依赖树图标
**用途：** 加载阶段 - "构建依赖树"
**替换：** 🌲
**Prompt：**
```
Create a minimalist tree diagram icon representing dependency tree structure.
- Style: Line art, node-and-edge diagram
- Color: Orange (#FF9538) for main lines, Teal (#16AA98) for nodes
- Features: 3 levels of nodes connected by lines, tree-like hierarchy
- Shape: Circles for nodes (6-8px diameter), clean connecting lines
- Size: 64x64px SVG
- Layout: Top-down tree structure, symmetrical
- Background: Transparent
```

#### target.svg - 目标/优化图标
**用途：** 加载阶段 - "优化学习路径"、空状态提示
**替换：** 🎯
**Prompt：**
```
Create a minimalist target/bullseye icon with path arrow.
- Style: Concentric circles with arrow
- Color: Orange (#FF9538) for target, Teal (#16AA98) for arrow
- Features: 3 concentric circles, curved arrow pointing to center
- Stroke: 2px for circles, slightly thicker (2.5px) for arrow
- Size: 64x64px SVG
- Mood: Goal-oriented, precise
- Background: Transparent
```

#### sparkles.svg - 完成/成功图标
**用途：** 加载阶段 - "准备就绪"
**替换：** ✨
**Prompt：**
```
Create a minimalist sparkle/star icon representing completion and success.
- Style: Multiple small stars/sparkles radiating outward
- Color: Orange (#FF9538) main stars, Teal (#16AA98) accent stars
- Features: 1 large central star (4-point), 3-4 smaller sparkles around it
- Stroke: 2px, clean geometric shapes
- Size: 64x64px SVG
- Mood: Celebratory, achievement
- Background: Transparent
```

---

### 3. 功能性图标（Functional Icons）

#### user.svg - 用户头像图标
**用途：** 用户登录、个人信息显示
**替换：** 👤
**Prompt：**
```
Create a minimalist user profile icon in CodeMonkey style.
- Style: Simple head and shoulders silhouette
- Color: Dark gray (#2d2d2d) outline with 2px stroke
- Features: Circular head, rounded shoulders, no facial details
- Optional: Tiny code bracket "{}" as decorative element
- Size: 64x64px SVG
- Mood: Professional, friendly
- Background: Transparent
```

#### book-open.svg - 阅读模式图标
**用途：** 阅读模式切换按钮
**替换：** 📖
**Prompt：**
```
Create a minimalist open book icon.
- Style: Line art, symmetrical open book
- Color: Orange (#FF9538) outline with 2px stroke
- Features: Two pages opened at center, slight page curve, 3-4 horizontal lines representing text
- Size: 64x64px SVG
- Mood: Educational, knowledge
- Background: Transparent
```

#### edit.svg - 编辑/专注模式图标
**用途：** 编辑模式、专注阅读切换
**替换：** 📝
**Prompt：**
```
Create a minimalist pencil or edit icon.
- Style: Simple pencil shape or notepad with pen
- Color: Teal (#16AA98) outline with 2px stroke
- Features: Diagonal pencil with sharp tip, or notepad with checkmark
- Size: 64x64px SVG
- Details: Clean lines, 45-degree angle if pencil
- Background: Transparent
```

#### checkmark.svg - 完成/已掌握图标
**用途：** 概念已掌握状态标识
**替换：** ✅
**Prompt：**
```
Create a minimalist checkmark icon with circle.
- Style: Rounded checkmark inside circle
- Color: Teal (#16AA98) for both elements
- Features: Circle border (2px), bold checkmark (2.5px stroke) inside
- Size: 64x64px SVG
- Mood: Success, completion, positive
- Background: Transparent
```

#### clock.svg - 进行中/待学习图标
**用途：** 概念进行中状态标识
**替换：** ⏳
**Prompt：**
```
Create a minimalist clock or hourglass icon.
- Style: Simple circular clock face with hands
- Color: Orange (#FF9538) outline with 2px stroke
- Features: Circle outline, hour and minute hands at 3 o'clock position
- Alternative: Simple hourglass shape
- Size: 64x64px SVG
- Mood: In progress, time-related
- Background: Transparent
```

#### chart.svg - 数据/统计图标
**用途：** 进度统计、数据展示区域
**替换：** 📊
**Prompt：**
```
Create a minimalist bar chart icon.
- Style: Simple column chart with 3-4 bars of varying heights
- Color: Orange (#FF9538) for bars, Teal (#16AA98) for axes
- Features: Horizontal baseline, 3 vertical bars (short, tall, medium)
- Stroke: 2px for all elements
- Size: 64x64px SVG
- Mood: Data, analytics, progress
- Background: Transparent
```

#### books.svg - 学习资源/关联概念图标
**用途：** 学习资源区域、关联概念标识
**替换：** 📚
**Prompt：**
```
Create a minimalist stack of books icon.
- Style: 3 books stacked at slight angles
- Color: Alternating Orange (#FF9538) and Teal (#16AA98)
- Features: Simple rectangles representing book spines, slight tilt for depth
- Stroke: 2px outlines
- Size: 64x64px SVG
- Mood: Learning, knowledge, resources
- Background: Transparent
```

#### arrow-right.svg - 下一步/继续图标
**用途：** 下一个概念、继续学习按钮
**替换：** ➡️
**Prompt：**
```
Create a minimalist right arrow icon.
- Style: Simple arrow pointing right
- Color: Orange (#FF9538)
- Features: Arrow head (triangle), straight shaft
- Stroke: 2.5px for bold visibility
- Size: 64x64px SVG
- Variants: Could include circle background for button version
- Background: Transparent
```

---

### 4. 装饰性图标（Decorative Icons）

#### code-brackets.svg - 代码括号图标
**用途：** 装饰元素、代码文化象征
**Prompt：**
```
Create a minimalist curly brackets icon pair "{ }".
- Style: Simple matching curly brackets
- Color: Dark gray (#2d2d2d) with 2px stroke
- Features: Clean curves, symmetrical, proper spacing
- Size: 64x64px SVG
- Usage: Decorative element throughout UI
- Background: Transparent
```

#### lightbulb.svg - 提示/灵感图标
**用途：** Tips、建议、灵感提示
**Prompt：**
```
Create a minimalist lightbulb icon.
- Style: Classic bulb shape with simple filament
- Color: Orange (#FF9538) for bulb, Teal (#16AA98) for base
- Features: Rounded bulb top, 2-3 filament lines inside, threaded base
- Stroke: 2px outline
- Size: 64x64px SVG
- Mood: Ideas, tips, inspiration
- Background: Transparent
```

---

## 🎨 设计一致性检查清单

在生成或使用图标前，请确认：

- [ ] 描边宽度：2px (或 2.5px for bold elements)
- [ ] 颜色：仅使用 #FF9538、#16AA98、#2d2d2d
- [ ] 尺寸：64x64px viewBox
- [ ] 格式：SVG，矢量可缩放
- [ ] 风格：线条图标，极简风格
- [ ] 背景：完全透明
- [ ] 圆角：统一使用 stroke-linecap="round" stroke-linejoin="round"
- [ ] 对齐：居中对齐，内部留有合理padding

---

## 📦 文件命名规范

所有图标文件命名遵循：
- 小写字母
- 连字符分隔 (kebab-case)
- .svg 扩展名

**示例：**
- ✅ `monkey.svg`
- ✅ `search.svg`
- ✅ `arrow-right.svg`
- ❌ `MonkeyIcon.svg`
- ❌ `search_icon.svg`

---

## 🔄 图标使用方式

### 方法1：直接使用 img 标签
```jsx
<img src="/icons/monkey.svg" alt="CodeMonkey" width="24" height="24" />
```

### 方法2：使用 Icon 组件（推荐）
```jsx
import Icon from './components/Icon'
<Icon name="monkey" size={24} color="primary" />
```

### 方法3：内联 SVG（适合需要动态样式）
```jsx
import MonkeyIcon from './icons/monkey.svg?react'
<MonkeyIcon className="icon" />
```

---

## 📝 备注

1. **优先级顺序：**
   - 高优先级：monkey, search, tree, target, sparkles, user
   - 中优先级：book-open, edit, checkmark, clock
   - 低优先级：chart, books, arrow-right, lightbulb

2. **可选扩展图标：**
   - `rocket.svg` - 启动/开始
   - `graduation-cap.svg` - 学习/教育
   - `connection.svg` - 连接/关联
   - `filter.svg` - 筛选/过滤

3. **AI生成建议：**
   - 推荐使用：Midjourney, DALL-E 3, Figma AI
   - 关键词：minimalist, line icon, flat design, 2px stroke
   - 后期处理：使用 SVGOMG 优化文件大小

4. **一致性提示：**
   所有图标应该感觉像是同一套设计系统的产物，保持视觉语言统一。

---

## 🎯 快速生成命令（批量生成）

如果使用 AI 工具批量生成，可以使用统一的前缀：

```
Create a set of 12 minimalist line icons for a coding education app called CodeMonkey:
- Style: Line art, 2px stroke, flat design
- Colors: Orange #FF9538 and Teal #16AA98
- Size: 64x64px SVG format
- Theme: Programming, learning, technology
- Icons needed: monkey, search, tree, target, sparkles, user, book, edit, checkmark, clock, chart, books
- Mood: Friendly, professional, geek-friendly
- Background: Transparent
- Requirements: Consistent stroke width, similar visual weight, cohesive design system
```

---

**文档版本：** v1.0  
**最后更新：** 2025-11-07  
**维护者：** CodeMonkey Design Team
