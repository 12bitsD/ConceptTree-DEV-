import PropTypes from 'prop-types'

/**
 * Icon Component - CodeMonkey Design System
 * 统一的图标组件，支持动态加载SVG图标
 */

const ICON_BASE_PATH = '/icons'

// 图标颜色映射
const COLOR_MAP = {
  primary: '#FF9538',    // 橙色
  secondary: '#16AA98',  // 青绿色
  text: '#2d2d2d',      // 深灰色
  white: '#ffffff',      // 白色
}

// 可用的图标名称列表（用于类型检查和文档）
export const AVAILABLE_ICONS = [
  // 核心品牌
  'monkey',
  
  // 加载阶段
  'search',
  'tree', 
  'target',
  'sparkles',
  
  // 功能性
  'user',
  'book-open',
  'edit',
  'checkmark',
  'clock',
  'chart',
  'books',
  'arrow-right',
  
  // 装饰性
  'code-brackets',
  'lightbulb',
]

export default function Icon({ 
  name, 
  size = 24, 
  color,
  className = '',
  style = {},
  ...props 
}) {
  // 如果指定了预设颜色名称，转换为实际颜色值
  const iconColor = COLOR_MAP[color] || color

  return (
    <img
      src={`${ICON_BASE_PATH}/${name}.svg`}
      alt={name}
      width={size}
      height={size}
      className={`icon icon-${name} ${className}`}
      style={{
        display: 'inline-block',
        verticalAlign: 'middle',
        filter: iconColor ? `var(--icon-color-filter)` : 'none',
        '--icon-color': iconColor,
        ...style
      }}
      {...props}
    />
  )
}

Icon.propTypes = {
  name: PropTypes.oneOf(AVAILABLE_ICONS).isRequired,
  size: PropTypes.number,
  color: PropTypes.oneOfType([
    PropTypes.oneOf(['primary', 'secondary', 'text', 'white']),
    PropTypes.string
  ]),
  className: PropTypes.string,
  style: PropTypes.object,
}

Icon.defaultProps = {
  size: 24,
  className: '',
  style: {},
}
