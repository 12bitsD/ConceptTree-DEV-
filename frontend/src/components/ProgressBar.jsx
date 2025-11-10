export default function ProgressBar({ mastered, total }) {
  const pct = total > 0 ? Math.round((mastered / total) * 100) : 0
  return (
    <div className="progress-wrap">
      <div className="progress-label">完成度 {pct}%</div>
      <div className="progress-bar">
        <div className="progress-inner" style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}