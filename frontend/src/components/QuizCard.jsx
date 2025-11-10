import { useState } from 'react'

export default function QuizCard({ quiz }) {
  const [choice, setChoice] = useState(null)
  const [submitted, setSubmitted] = useState(false)
  const [isCorrect, setIsCorrect] = useState(null)

  function submit() {
    if (submitted) return
    let ok = false
    if (Array.isArray(quiz.options) && typeof quiz.answer === 'number') {
      ok = choice === quiz.answer
    } else if (typeof quiz.answer === 'string') {
      ok = String(choice).trim().toLowerCase() === quiz.answer.trim().toLowerCase()
    }
    setIsCorrect(ok)
    setSubmitted(true)
  }

  return (
    <div className="quiz-card">
      <div className="quiz-q">题目：{quiz.question}</div>
      {Array.isArray(quiz.options) ? (
        <div className="quiz-opts">
          {quiz.options.map((opt, idx) => (
            <label key={idx} className={`quiz-opt ${choice === idx ? 'chosen' : ''}`}>
              <input
                type="radio"
                name="quiz"
                checked={choice === idx}
                onChange={() => setChoice(idx)}
              />
              {opt}
            </label>
          ))}
        </div>
      ) : (
        <input
          className="quiz-input"
          placeholder="请输入答案"
          value={choice ?? ''}
          onChange={(e) => setChoice(e.target.value)}
        />
      )}
      <button className="secondary" onClick={submit} disabled={submitted || choice === null}>
        提交
      </button>
      {submitted && (
        <div className={`quiz-result ${isCorrect ? 'ok' : 'bad'}`}>
          {isCorrect ? '正确 ✅' : '错误 ❌'}
          {quiz.explanation ? <div className="quiz-exp">{quiz.explanation}</div> : null}
        </div>
      )}
    </div>
  )
}