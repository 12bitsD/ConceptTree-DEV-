import { useState } from 'react'

export default function ConceptInput({ onSubmit, error }) {
  const [value, setValue] = useState('')
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [focus, setFocus] = useState('')
  const [minWidth, setMinWidth] = useState('')
  const [priority, setPriority] = useState('')

  function submit(e) {
    e.preventDefault()
    const concept = value.trim()
    if (!concept) return
    onSubmit(concept, { focus, minWidth, priority })
  }

  return (
    <div className="concept-input">
      <form onSubmit={submit} className="concept-form">
        <input
          className="concept-input-box"
          placeholder="输入你想学的概念..."
          value={value}
          onChange={(e) => setValue(e.target.value)}
        />
        <button className="primary" type="submit">
          生成依赖树
        </button>
      </form>
      <div className="advanced-toggle">
        <button className="secondary" onClick={() => setShowAdvanced(v => !v)}>
          {showAdvanced ? '收起高级参数' : '展开高级参数'}
        </button>
      </div>
      {showAdvanced && (
        <div className="advanced-panel">
          <div className="row">
            <label>分支焦点</label>
            <input placeholder="逗号分隔的分支ID，例如: sorting,algorithms" value={focus} onChange={(e) => setFocus(e.target.value)} />
          </div>
          <div className="row">
            <label>分支最小宽度</label>
            <input placeholder="id:num 对，例如: sorting:4,python_basics:2" value={minWidth} onChange={(e) => setMinWidth(e.target.value)} />
          </div>
          <div className="row">
            <label>分支优先级</label>
            <input placeholder="id:num 对，数值越大越优先，例如: algorithms:3" value={priority} onChange={(e) => setPriority(e.target.value)} />
          </div>
        </div>
      )}
      {error && <div className="error-tip">{error}</div>}
    </div>
  )
}
