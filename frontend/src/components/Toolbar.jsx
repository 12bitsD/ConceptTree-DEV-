import { useState } from 'react'

export default function Toolbar({ 
  concept, 
  progress, 
  suggestions, 
  onReset, 
  tree, 
  user, 
  onLogout,
  isReadingMode,
  onToggleReadingMode,
  theme,
  onThemeChange,
  onSearchToggle
}) {
  const [showPath, setShowPath] = useState(false)
  const idToLabel = new Map(tree?.nodes?.map((n) => [n.id, n.label]))
  const progressPercent = progress.total > 0 ? (progress.mastered / progress.total) * 100 : 0
  
  return (
    <div className="modern-toolbar">
      {/* 左侧信息 */}
      <div className="toolbar-left">
        <div className="concept-title">
          <h2>{concept}</h2>
          <div className="progress-summary">
            <span className="progress-text">进度: {progress.mastered}/{progress.total}</span>
            <div className="mini-progress">
              <div 
                className="mini-progress-fill" 
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>
        </div>
      </div>
      
      {/* 中间操作区 */}
      <div className="toolbar-center">
        <button 
          className={`toolbar-btn ${showPath ? 'active' : ''}`}
          onClick={() => setShowPath((v) => !v)}
          title="查看学习顺序"
        >
          🗺️ 学习顺序
        </button>
        <button 
          className="toolbar-btn search-toggle"
          onClick={onSearchToggle}
          title="搜索概念 (Ctrl+/)"
        >
          🔍 搜索
        </button>
        <button 
          className="toolbar-btn reading-toggle"
          onClick={onToggleReadingMode}
          title={isReadingMode ? "退出阅读模式 (Ctrl+F)" : "进入阅读模式 (Ctrl+F)"}
        >
          {isReadingMode ? "📖 阅读模式" : "📝 专注阅读"}
        </button>
      </div>
      
      {/* 右侧操作 */}
      <div className="toolbar-right">
        {user ? (
          <div className="user-section">
            <span className="user-chip">
              <span className="user-avatar">👤</span>
              {user.name}
            </span>
            <button className="toolbar-btn danger" onClick={onLogout}>
              退出
            </button>
          </div>
        ) : (
          <button className="toolbar-btn primary">登录</button>
        )}
        
        {/* 主题切换 */}
        <div className="theme-switcher">
          <button 
            className={`toolbar-btn theme-btn ${theme === 'light' ? 'active' : ''}`}
            onClick={() => onThemeChange('light')}
            title="浅色主题"
          >
            ☀️
          </button>
          <button 
            className={`toolbar-btn theme-btn ${theme === 'auto' ? 'active' : ''}`}
            onClick={() => onThemeChange('auto')}
            title="跟随系统"
          >
            🌓
          </button>
          <button 
            className={`toolbar-btn theme-btn ${theme === 'dark' ? 'active' : ''}`}
            onClick={() => onThemeChange('dark')}
            title="深色主题"
          >
            🌙
          </button>
        </div>
        
        <button className="toolbar-btn secondary" onClick={onReset} title="重置进度 (Ctrl+Shift+R)">
          🔄 重置
        </button>
      </div>
      
      {/* 学习顺序弹出层 */}
      {showPath && (
        <div className="path-overlay">
          <div className="path-popup">
            <div className="path-header">
              <h3>📚 推荐学习路径</h3>
              <button 
                className="close-btn"
                onClick={() => setShowPath(false)}
              >
                ✕
              </button>
            </div>
            <div className="path-content">
              <div className="path-description">
                建议按照以下顺序学习，从基础到高级：
              </div>
              <ol className="path-list">
                {suggestions.map((id, index) => (
                  <li key={id} className="path-item">
                    <span className="path-number">{index + 1}</span>
                    <span className="path-label">{idToLabel.get(id) || id}</span>
                  </li>
                ))}
              </ol>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}