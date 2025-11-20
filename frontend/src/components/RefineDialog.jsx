import { useMemo, useState } from 'react'

export default function RefineDialog({ concept, options, onConfirm, onSkip, onClose }) {
  const init = useMemo(() => {
    const obj = {}
    for (const o of options || []) {
      if (o.type === 'multi-select') obj[o.id] = o.defaultChecked ? (o.suggested || []) : []
      else obj[o.id] = ''
    }
    if (!options || options.length === 0) obj.freeform = ''
    return obj
  }, [options])
  const [values, setValues] = useState(init)

  function toggleChip(id, val) {
    const list = Array.isArray(values[id]) ? values[id].slice() : []
    const idx = list.indexOf(val)
    if (idx >= 0) list.splice(idx, 1)
    else list.push(val)
    setValues({ ...values, [id]: list })
  }

  function changeText(id, v) {
    setValues({ ...values, [id]: v })
  }

  function selectAll() {
    const next = { ...values }
    for (const o of options || []) {
      if (o.type === 'multi-select') next[o.id] = o.suggested || []
    }
    setValues(next)
  }

  function clearAll() {
    const next = { ...values }
    for (const o of options || []) {
      if (o.type === 'multi-select') next[o.id] = []
    }
    setValues(next)
  }

  function confirm() {
    const details = {}
    for (const o of options || []) {
      const v = values[o.id]
      if (o.type === 'multi-select') {
        if (Array.isArray(v) && v.length) details[o.id] = v
      } else if (typeof v === 'string' && v.trim()) {
        details[o.id] = v.trim()
      }
    }
    if ((!options || options.length === 0) && typeof values.freeform === 'string' && values.freeform.trim()) {
      details.freeform = values.freeform.trim()
    }
    onConfirm(details)
  }

  return (
    <div className="refine-pop">
      <div className="modern-toolbar">
        <span className="chip">{concept}</span>
        <button className="toolbar-btn secondary" onClick={selectAll}>全选</button>
        <button className="toolbar-btn secondary" onClick={clearAll}>全不选</button>
        <button className="toolbar-btn" onClick={onClose}>关闭</button>
      </div>
      <div className="refine-content">
        {(!options || options.length === 0) ? (
          <div className="refine-item">
            <div className="section-title">自由补充</div>
            <input
              className="concept-input-box"
              placeholder={"请填写你希望补充的细节"}
              value={values.freeform || ''}
              onChange={(e) => changeText('freeform', e.target.value)}
            />
          </div>
        ) : ( (options || []).map((o) => (
          <div key={o.id} className="refine-item">
            <div className="section-title">{o.title}</div>
            {o.type === 'multi-select' ? (
              <div className="chips">
                {(o.suggested || []).map((s) => (
                  <span
                    key={s}
                    className={`chip ${Array.isArray(values[o.id]) && values[o.id].includes(s) ? 'active' : ''}`}
                    onClick={() => toggleChip(o.id, s)}
                  >{s}</span>
                ))}
              </div>
            ) : (
              <input
                className="concept-input-box"
                placeholder={o.description || ''}
                value={values[o.id] || ''}
                onChange={(e) => changeText(o.id, e.target.value)}
              />
            )}
            {o.description ? <div className="muted">{o.description}</div> : null}
          </div>
        )) )}
      </div>
      <div className="refine-actions">
        <button className="secondary" onClick={onSkip}>直接生成</button>
        <button className="primary" onClick={confirm}>确认细化</button>
      </div>
    </div>
  )
}