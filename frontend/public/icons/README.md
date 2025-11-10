# CodeMonkey Icons

## 📁 图标文件夹

此文件夹存放 CodeMonkey 项目的所有 SVG 图标文件。

---

## 📋 图标清单

### ✅ 已添加的图标

_(请在生成图标后勾选对应项)_

- [x] `monkey.svg` - 猴子品牌图标
- [x] `search.svg` - 搜索/分析图标
- [ ] `tree.svg` - 依赖树图标
- [ ] `target.svg` - 目标/优化图标
- [ ] `sparkles.svg` - 完成/成功图标
- [ ] `user.svg` - 用户头像图标
- [ ] `book-open.svg` - 阅读模式图标
- [ ] `edit.svg` - 编辑模式图标
- [ ] `checkmark.svg` - 已完成图标
- [ ] `clock.svg` - 进行中图标
- [ ] `chart.svg` - 数据统计图标
- [ ] `books.svg` - 学习资源图标
- [ ] `arrow-right.svg` - 下一步图标
- [ ] `code-brackets.svg` - 代码括号图标
- [ ] `lightbulb.svg` - 提示/灵感图标

---

## 🎨 设计规范

**必须遵循的规范：**
- **格式：** SVG
- **尺寸：** 64x64px (viewBox="0 0 64 64")
- **描边：** 2px (或 2.5px for bold)
- **颜色：** 
  - 主色：#FF9538 (橙色)
  - 辅色：#16AA98 (青绿色)
  - 文字色：#2d2d2d (深灰色)
- **背景：** 透明
- **风格：** 极简线条图标

---

## 📝 使用说明

### 方法1：直接使用
```jsx
<img src="/icons/monkey.svg" alt="CodeMonkey" width="24" height="24" />
```

### 方法2：使用Icon组件（推荐）
```jsx
import Icon from '@/components/Icon'

<Icon name="monkey" size={32} color="primary" />
<Icon name="search" size={24} color="secondary" />
```

---

## 🔗 相关文档

- **设计Prompt：** 查看 `ICON_DESIGN_PROMPTS.md` 获取完整的AI生成提示词
- **设计系统：** 参考 `CodeMonkey-design-system.md` 了解整体设计规范
- **Icon组件：** 位于 `frontend/src/components/Icon.jsx`

---

## 🎯 快速开始

1. 根据 `ICON_DESIGN_PROMPTS.md` 使用AI工具生成图标
2. 将生成的SVG文件重命名为规定的文件名（如 `monkey.svg`）
3. 放入此文件夹 `/frontend/public/icons/`
4. 在代码中使用 `<Icon name="monkey" />` 调用
5. 更新本文件的清单，勾选已添加的图标

---

## ⚠️ 注意事项

- 所有SVG文件必须经过优化（推荐使用 SVGOMG）
- 保持文件大小在 5KB 以下
- 确保图标在小尺寸（16px）下仍清晰可辨
- 测试图标在亮色和暗色背景下的显示效果

---

**最后更新：** 2025-11-07
