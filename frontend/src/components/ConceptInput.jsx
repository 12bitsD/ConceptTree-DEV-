import { useState } from 'react'

export default function ConceptInput({ onSubmit, error, loading }) {
  const [value, setValue] = useState('')

  function submit(e) {
    e.preventDefault()
    const concept = value.trim()
    if (!concept) return
    onSubmit(concept)
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
        <button className="primary" type="submit" disabled={!!loading}>
          生成依赖树
        </button>
      </form>
      {error && <div className="error-tip">{error}</div>}
    </div>
  )
}