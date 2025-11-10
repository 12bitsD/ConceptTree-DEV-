import { useState, useEffect } from 'react'
import '../styles/LoadingStages.css'

const LOADING_STAGES = [
  {
    id: 1,
    message: '// Initializing CodeMonkey...',
    icon: 'monkey',
    duration: 800
  },
  {
    id: 2,
    message: '// Analyzing concept structure...',
    icon: 'search',
    duration: 1200
  },
  {
    id: 3,
    message: '// Building dependency tree...',
    icon: 'tree',
    duration: 1500
  },
  {
    id: 4,
    message: '// Optimizing learning path...',
    icon: 'target',
    duration: 1000
  },
  {
    id: 5,
    message: '// Ready to learn!',
    icon: 'sparkles',
    duration: 500
  }
]

export default function LoadingStages() {
  const [currentStage, setCurrentStage] = useState(0)
  const [completedStages, setCompletedStages] = useState([])

  useEffect(() => {
    if (currentStage >= LOADING_STAGES.length) {
      // 所有阶段完成，延迟一点再回调
      const timer = setTimeout(() => {
        onComplete?.()
      }, 300)
      return () => clearTimeout(timer)
    }

    const stage = LOADING_STAGES[currentStage]
    const timer = setTimeout(() => {
      setCompletedStages(prev => [...prev, stage.id])
      setCurrentStage(prev => prev + 1)
    }, stage.duration)

    return () => clearTimeout(timer)
  }, [currentStage, onComplete])

  const currentStageData = LOADING_STAGES[currentStage]
  const progress = ((currentStage + 1) / LOADING_STAGES.length) * 100

  return (
    <div className="loading-stages-container">
      {/* 装饰元素 - 对称布局 */}
      <div className="loading-decoration decoration-left">
        <div className="code-snippet">
          while (learning) {'{'}
          <br />&nbsp;&nbsp;grow();
          <br />{'}'}
        </div>
      </div>
      <div className="loading-decoration decoration-right">
        <div className="code-snippet">
          if (concept) {'{'}
          <br />&nbsp;&nbsp;master();
          <br />{'}'}
        </div>
      </div>

      {/* 主加载区域 */}
      <div className="loading-main">
        {/* Logo 动画 */}
        <div className="loading-logo">
          <img src="/logo.png" alt="CodeMonkey" className="logo-spin" />
        </div>

        {/* 当前阶段 */}
        {currentStageData && (
          <div className="current-stage">
            <img 
              src={`/icons/${currentStageData.icon}.svg`} 
              alt={currentStageData.icon}
              className="stage-icon"
              width="48"
              height="48"
            />
            <p className="stage-message">{currentStageData.message}</p>
          </div>
        )}

        {/* 进度条 */}
        <div className="loading-progress-bar">
          <div 
            className="loading-progress-fill" 
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="loading-progress-text">
          {Math.round(progress)}% Complete
        </div>

        {/* 已完成阶段列表 */}
        <div className="completed-stages">
          {LOADING_STAGES.map((stage, index) => {
            const isCompleted = completedStages.includes(stage.id)
            const isCurrent = index === currentStage
            
            return (
              <div 
                key={stage.id}
                className={`stage-item ${isCompleted ? 'completed' : ''} ${isCurrent ? 'current' : ''}`}
              >
                <span className="stage-check">
                  {isCompleted ? '✓' : isCurrent ? '⟳' : '○'}
                </span>
                <span className="stage-text">{stage.message}</span>
              </div>
            )
          })}
        </div>
      </div>

      {/* 底部提示 */}
      <div className="loading-footer">
        <p className="loading-tip">
          💡 Tip: CodeMonkey breaks down complex concepts into manageable chunks
        </p>
      </div>
    </div>
  )
}
