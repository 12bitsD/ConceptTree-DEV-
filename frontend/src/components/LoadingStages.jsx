import { useState, useEffect } from 'react'
import '../styles/LoadingStages.css'

const DEFAULT_STAGES = [
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

export default function LoadingStages({ onComplete, stages, current, progress, message }) {
  const stageList = stages && stages.length ? stages : DEFAULT_STAGES
  const [currentStageIdx, setCurrentStageIdx] = useState(0)
  const [completedStages, setCompletedStages] = useState([])

  useEffect(() => {
    // 将后端阶段ID(1..N)映射为前端索引(0..len-1)
    if (typeof current === 'number') {
      const idx = Math.max(0, Math.min(stageList.length - 1, (current - 1)))
      setCurrentStageIdx(idx)
      setCompletedStages(stageList.filter((s) => s.id < current).map((s) => s.id))
      return
    }
    if (currentStageIdx >= stageList.length) {
      const timer = setTimeout(() => { onComplete?.() }, 300)
      return () => clearTimeout(timer)
    }
    const stage = stageList[currentStageIdx]
    const timer = setTimeout(() => {
      setCompletedStages(prev => [...prev, stage.id])
      setCurrentStageIdx(prev => prev + 1)
    }, stage.duration)
    return () => clearTimeout(timer)
  }, [currentStageIdx, onComplete, current, stageList])

  const currentStageData = stageList[currentStageIdx]
  const prog = typeof progress === 'number' ? progress : (((currentStageIdx + 1) / stageList.length) * 100)

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
            <p className="stage-message">{message || currentStageData.message}</p>
          </div>
        )}

        {/* 进度条 */}
        <div className="loading-progress-bar">
          <div className="loading-progress-fill" style={{ width: `${prog}%` }} />
        </div>
        <div className="loading-progress-text">
          {Math.round(prog)}% Complete
        </div>

        {/* 已完成阶段列表 */}
        <div className="completed-stages">
          {stageList.map((stage, index) => {
            const isCompleted = completedStages.includes(stage.id)
            const isCurrent = index === currentStageIdx
            
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
