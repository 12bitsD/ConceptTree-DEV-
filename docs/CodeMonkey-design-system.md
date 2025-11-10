# CodeMonkey Design System Guide
## 设计风格拆解与规范文档

---

## 🎨 核心设计哲学

### 品牌个性
**极客而有趣** - CodeMonkey的设计风格在专业的编程工具中融入代码文化和数学美学，营造出技术人员喜爱的氛围。

**关键词：**
- 极客友好（Geek-Friendly）
- 简洁现代（Clean & Modern）
- 代码文化（Code Culture）
- 技术专业（Technical）
- 富有创意（Creative）

---

## 🎨 色彩系统

### 主色调（Primary Colors）
```css
--primary-color: #FF9538;     /* 橙色 - 鸭子元素、CTA按钮、强调色 */
--secondary-color: #16AA98;   /* 青绿色 - 辅助装饰、图标 */
--text-color: #2d2d2d;        /* 深灰色 - 主文字颜色 */
--border-color: #2d2d2d;      /* 深灰色 - 边框线条 */
```

### 中性色（Neutral Colors）
```css
--white: #ffffff;              /* 纯白 - 背景、卡片 */
--bg-light: #ede6df;          /* 浅米色 - 次级背景 */
```

### 色彩使用原则

1. **橙色（#FF9538）**
   - **用途**：品牌识别、CTA按钮、鸭子图形、重要元素强调
   - **情感**：活力、创新、温暖
   - **禁忌**：不用于大面积背景，避免视觉疲劳

2. **青绿色（#16AA98）**
   - **用途**：装饰图形、次级按钮、图标
   - **情感**：科技感、可靠性、现代
   - **禁忌**：不与橙色同时大量使用

3. **深灰色（#2d2d2d）**
   - **用途**：文字、边框、图标
   - **特点**：比纯黑更柔和，更现代
   - **原则**：确保足够对比度（WCAG AA标准）

4. **浅米色（#ede6df）**
   - **用途**：区域分隔、背景变化
   - **特点**：温暖、舒适、不刺眼
   - **原则**：用于需要视觉休息的区域

### 色彩对比度标准
- 文字与背景对比度：≥ 4.5:1 (WCAG AA)
- 大文字与背景对比度：≥ 3:1
- 交互元素与背景对比度：≥ 3:1

---

## 📝 字体系统

### 字体族（Font Family）
```css
/* 主要字体 - 用于界面文字 */
font-family: 'Inter', sans-serif;

/* 次要字体 - 用于正文内容 */
font-family: 'Open Sans', sans-serif;

/* 等宽字体 - 用于代码、数据展示 */
font-family: 'Aeonik Mono', monospace;
```

### 字体权重（Font Weight）
```css
--font-light: 300;      /* 用于辅助文字 */
--font-regular: 400;    /* 用于正文 */
--font-semibold: 600;   /* 用于导航、标签 */
--font-bold: 700;       /* 用于标题、强调 */
```

### 字体大小规范

#### 标题（Headings）
```css
h1 {
    font-size: 48px;        /* Mobile */
    font-size: 72px;        /* Desktop */
    font-weight: 700;
    line-height: 1.2;
}

h2 {
    font-size: 36px;        /* Mobile */
    font-size: 48px;        /* Desktop */
    font-weight: 700;
    line-height: 1.3;
}

h3 {
    font-size: 24px;
    font-weight: 600;
    line-height: 1.4;
}
```

#### 正文（Body Text）
```css
body {
    font-size: 16px;        /* Mobile */
    font-size: 18px;        /* Desktop */
    font-weight: 400;
    line-height: 1.6-1.8;
}
```

#### 小字（Small Text）
```css
.small-text {
    font-size: 14px;
    font-weight: 400;
    line-height: 1.5;
}
```

### 字体使用原则
1. **层级分明**：使用大小和粗细建立清晰的视觉层级
2. **行高舒适**：正文行高保持在1.6-1.8之间
3. **字间距**：标题和按钮使用0.5px的字间距
4. **字母大写**：导航和按钮使用全大写（`text-transform: uppercase`）

---

## 🔲 边框与圆角

### 边框规范
```css
/* 标准边框 */
border: 1.5px solid var(--border-color);

/* 粗边框（强调） */
border: 2px solid var(--border-color);
```

### 圆角规范
```css
--radius-small: 4px;     /* 按钮、小卡片 */
--radius-medium: 8px;    /* 卡片、输入框 */
--radius-large: 24px;    /* Logo背景、大容器 */
--radius-full: 100px;    /* 云朵、圆形装饰 */
```

### 边框使用原则
1. **一致性**：所有可交互元素都有明显的边框
2. **手绘感**：1.5px的边框宽度营造轻盈感
3. **不用阴影**：主要依靠边框而非投影来区分层级

---

## 🧩 组件设计规范

### 1. 按钮（Buttons）

#### 主按钮（Primary Button）
```css
.btn-primary {
    background-color: #FF9538;
    color: #ffffff;
    border: 2px solid #FF9538;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s;
}

.btn-primary:hover {
    background-color: #e87f1a;
    border-color: #e87f1a;
    transform: translateY(-2px);
}
```

#### 次要按钮（Secondary Button）
```css
.btn-secondary {
    background-color: transparent;
    color: #2d2d2d;
    border: 2px solid #2d2d2d;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s;
}

.btn-secondary:hover {
    background-color: #2d2d2d;
    color: #ffffff;
}
```

#### 按钮设计原则
- **对比明显**：主按钮用橙色，次要按钮透明
- **状态清晰**：hover时有明显的颜色和位移变化
- **文字大写**：所有按钮文字全大写，增强点击感
- **最小尺寸**：触摸目标≥ 44px × 44px

### 2. 卡片（Cards）

```css
.card {
    background: #ffffff;
    border: 1.5px solid #2d2d2d;
    border-radius: 8px;
    padding: 40px 30px;
    transition: transform 0.3s, box-shadow 0.3s;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
}
```

#### 卡片设计原则
- **极简主义**：白色背景+简单边框
- **交互反馈**：hover时上浮+阴影
- **内容呼吸**：充足的内边距（40px）
- **图标优先**：使用图标代替纯文字

### 3. 导航（Navigation）

```css
header {
    position: fixed;
    top: 0;
    height: 70px;           /* Mobile */
    height: 90px;           /* Desktop */
    background: #ffffff;
    border-bottom: 1.5px solid #2d2d2d;
    z-index: 1000;
}

nav a {
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: #2d2d2d;
    transition: color 0.3s;
}

nav a:hover {
    color: #FF9538;
}
```

#### 导航设计原则
- **固定顶部**：始终可见，便于导航
- **清晰分隔**：底部边框区分内容区域
- **全大写文字**：增强品牌个性
- **响应式收起**：移动端使用汉堡菜单

### 4. 装饰元素（Decorative Elements）

#### 数学公式装饰
```css
.formula {
    position: absolute;
    background: #ffffff;
    border: 1.5px solid #2d2d2d;
    border-radius: 4px;
    padding: 12px 16px;
    opacity: 0.7;
    font-family: 'Courier New', monospace;
    font-size: 14px;
    color: #2d2d2d;
    font-weight: 600;
    transform: rotate(-5deg);
    animation: float 8s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-20px); }
}
```

#### 代码块装饰
```css
.code-block {
    position: absolute;
    background: #ffffff;
    border: 1.5px solid #2d2d2d;
    border-radius: 4px;
    padding: 10px 14px;
    opacity: 0.6;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    color: #2d2d2d;
    line-height: 1.4;
    transform: rotate(-3deg);
    animation: float 7s ease-in-out infinite;
}
```

#### 几何图形
```css
.shape-circle {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background-color: #16AA98;
    border: 1.5px solid #2d2d2d;
    opacity: 0.4;
    animation: rotate 10s linear infinite;
}

@keyframes rotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
```

#### 装饰元素原则
- **轻量级动画**：缓慢的浮动和旋转，不干扰内容
- **对称布局**：装饰元素左右对称分布，视觉平衡
- **简洁优雅**：总共6个装饰元素（2公式+2代码）
- **品牌色彩**：使用橙色和青绿色
- **代码文化**：通过代码和公式强化技术氛围
- **适度使用**：装饰元素少而精，保持页面简洁友好

---

## 📐 布局与间距

### 容器宽度
```css
.container {
    max-width: 1200px;     /* Desktop */
    margin: 0 auto;
    padding: 0 20px;       /* Mobile */
    padding: 0 40px;       /* Desktop */
}
```

### 间距系统（Spacing Scale）
```css
--space-xs: 8px;
--space-sm: 16px;
--space-md: 24px;
--space-lg: 40px;
--space-xl: 60px;
--space-xxl: 80px;
```

### 栅格系统
```css
/* 三列布局（常用于特性卡片） */
.grid-3 {
    display: grid;
    grid-template-columns: 1fr;              /* Mobile */
    grid-template-columns: repeat(3, 1fr);   /* Desktop */
    gap: 30px;
}
```

### 布局原则
1. **居中对齐**：内容区域始终居中
2. **呼吸空间**：section之间至少80px间距
3. **响应式**：移动端单列，桌面端多列
4. **8px基准**：所有间距都是8的倍数

---

## 🎭 视觉效果

### 阴影（Shadows）
```css
/* 轻微阴影 - 用于卡片悬停 */
box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);

/* 原则：不用于静态元素，仅用于交互反馈 */
```

### 过渡动画（Transitions）
```css
/* 标准过渡 */
transition: all 0.3s ease;

/* 位移过渡 */
transition: transform 0.3s ease;

/* 原则：快速响应（≤ 0.3s），流畅自然 */
```

### 悬停效果（Hover States）
1. **按钮**：颜色变深 + 上浮2px
2. **卡片**：上浮5px + 阴影
3. **链接**：文字颜色变为橙色
4. **图标**：轻微缩放（1.05倍）

---

## 🎨 品牌图形元素

### 猴子（Monkey Icon）
- **风格**：Emoji 风格，亲切友好
- **符号**：🐵
- **颜色**：橙色（#FF9538）背景圆形
- **用途**：Logo、品牌识别

### 数学公式装饰（Math Formulas）
- **风格**：手写等宽字体，轻微旋转
- **数量**：2个（对称布局）
- **位置**：页面左右两侧
- **示例**：
  - 左侧：`f(x) = x² + 2x + 1`
  - 右侧：`∫ e^x dx = e^x + C`
- **字体**：Courier New, monospace
- **字号**：14px
- **颜色**：深灰色（#2d2d2d）
- **旋转角度**：-5° 和 5°（对称）
- **动画**：缓慢浮动（8s 和 6s）
- **用途**：背景装饰、营造学术氛围

### 代码块装饰（Code Blocks）
- **风格**：多行代码片段，手写感
- **数量**：2个（对称布局）
- **位置**：页面左右两侧
- **示例**：
  - 左侧：
    ```javascript
    if (task.done) {
      celebrate();
    }
    ```
  - 右侧：
    ```javascript
    while (coding) {
      drink(coffee);
    }
    ```
- **字体**：Courier New, monospace
- **字号**：12px
- **颜色**：深灰色（#2d2d2d）
- **样式**：白色背景 + 1.5px 边框 + 小圆角
- **旋转角度**：-3° 和 4°（对称）
- **动画**：缓慢浮动（7s 和 9s）
- **用途**：背景装饰、强化编程主题

### 几何图形（Geometric Shapes）
- **类型**：圆形
- **数量**：2个（对称布局）
- **位置**：页面左右两侧中部
- **颜色**：青绿色（#16AA98）
- **尺寸**：60px × 60px
- **动画**：左侧顺时针旋转，右侧逆时针旋转
- **用途**：辅助装饰，平衡画面

---

## 📱 响应式设计

### 断点（Breakpoints）
```css
/* Mobile First 方法 */
@media (min-width: 728px)  { /* Tablet */ }
@media (min-width: 1024px) { /* Desktop */ }
@media (min-width: 1440px) { /* Large Desktop */ }
```

### 响应式原则
1. **移动优先**：从小屏幕开始设计
2. **渐进增强**：大屏幕增加功能，不是减少
3. **触摸友好**：最小点击目标44px
4. **灵活布局**：使用flexbox和grid

### 字体响应
```css
/* 示例 */
h1 {
    font-size: 36px;  /* Mobile */
}

@media (min-width: 728px) {
    h1 {
        font-size: 72px;  /* Desktop */
    }
}
```

---

## ✍️ 文案风格

### 语气与语调
- **极客友好**：像和同行对话
- **幽默风趣**：适当使用程序员梗和技术双关
- **简洁清晰**：直奔主题，避免冗余
- **技术精准**：专业术语使用准确

### 文案示例
✅ **推荐**：
- "Making Task Management Feel Simple"
- "Monkey Todos - Code Your Tasks"
- "while (coding) { drink(coffee); }"
- "return 42; // The Answer to Everything"

❌ **避免**：
- 过于正式的企业腔
- 冗长的技术描述
- 非技术人员无法理解的深度黑话

---

## 🚫 设计禁忌

### 不要做的事
1. ❌ 使用渐变背景（保持纯色）
2. ❌ 使用复杂阴影（仅用于hover）
3. ❌ 过度装饰（保持简洁）
4. ❌ 使用纯黑色（#000000）
5. ❌ 忽略边框（边框是品牌特征）
6. ❌ 使用斜体字（除非引用）
7. ❌ 过度动画（避免干扰阅读）

### 要坚持的事
1. ✅ 使用1.5px边框
2. ✅ 保持白色背景为主
3. ✅ 使用橙色作为强调色
4. ✅ 大量留白，呼吸空间
5. ✅ 全大写导航和按钮
6. ✅ 简洁的图标和图形
7. ✅ 一致的动画时长（0.3s）

---

## 📋 设计检查清单

在完成设计前，确认以下事项：

### 视觉一致性
- [ ] 所有颜色都来自设计系统
- [ ] 字体大小符合规范
- [ ] 间距使用8px倍数
- [ ] 边框宽度为1.5px或2px
- [ ] 圆角使用预定义值

### 可访问性
- [ ] 文字对比度 ≥ 4.5:1
- [ ] 交互元素对比度 ≥ 3:1
- [ ] 触摸目标 ≥ 44px × 44px
- [ ] 焦点状态清晰可见
- [ ] 不仅依赖颜色传达信息

### 响应式
- [ ] 移动端布局完整
- [ ] 平板端布局优化
- [ ] 桌面端布局充分利用空间
- [ ] 图片自适应大小
- [ ] 文字大小响应式调整

### 交互反馈
- [ ] 所有按钮有hover状态
- [ ] 链接有明显反馈
- [ ] 加载状态清晰
- [ ] 错误提示友好
- [ ] 成功反馈及时

---

## 🎯 应用示例

### 典型页面结构
```html
<!-- Eyebrow Banner -->
<div class="eyebrow">通知或活动信息</div>

<!-- Header -->
<header>
    <logo>品牌标识</logo>
    <nav>导航菜单</nav>
    <cta>主要行动按钮</cta>
</header>

<!-- Hero Section -->
<section class="hero">
    <h1>主标题</h1>
    <p>副标题描述</p>
    <buttons>CTA按钮组</buttons>
    <visual>视觉元素（图片/视频）</visual>
    <decorations>装饰元素（云朵、图形）</decorations>
</section>

<!-- Content Sections -->
<section>
    <h2>小节标题</h2>
    <content>内容区域</content>
</section>

<!-- Footer -->
<footer>
    <links>链接导航</links>
    <copyright>版权信息</copyright>
</footer>
```

### 关键视觉元素位置
1. **左上角**：Logo和品牌名称
2. **右上角**：CTA按钮（鲜明的橙色）
3. **页面四角**：装饰性几何图形
4. **背景**：浮动的云朵元素
5. **内容间隙**：鸭子图标或分隔线

---

## 🔄 设计演进原则

### 如何扩展设计系统
1. **保持一致性**：新元素必须符合现有风格
2. **记录变更**：更新设计系统文档
3. **团队评审**：重大变更需集体决策
4. **渐进实施**：分阶段推出新设计

### 避免设计漂移
1. 定期审查现有设计
2. 移除不符合规范的元素
3. 统一命名和分类
4. 建立设计组件库

---

## 📚 参考资源

### 设计工具
- Figma（推荐用于设计和协作）
- Adobe Illustrator（用于图标和插图）
- ColorBox（用于色彩搭配）

### 灵感来源
- 现代SaaS产品设计
- 插画风格的技术品牌
- 扁平化设计趋势

### 设计测试
- WebAIM Contrast Checker（对比度检查）
- WAVE（可访问性评估）
- Lighthouse（性能和SEO审计）

---

## 📄 总结

CodeMonkey的设计风格核心特征：

1. **视觉语言**：简洁、现代、代码感
2. **色彩方案**：橙色主导、青绿辅助、深灰文字
3. **字体系统**：Inter为主、等宽字体装饰
4. **边框风格**：1.5px细边框、明确的轮廓
5. **装饰元素**：数学公式、代码块、猴子、几何图形
6. **交互设计**：轻微动画、清晰反馈
7. **品牌个性**：极客、专业、有趣、友好

**最重要的原则：简洁、一致、技术感！**
