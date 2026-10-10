/**
 * ScoreCard.jsx — Renders a single score card with label, value, progress bar,
 * and a one-line explanation.
 *
 * Props:
 *   label       {string}  Card title (e.g. "Job Requirement Coverage")
 *   score       {number}  Integer 0–100
 *   explanation {string}  One-sentence description of what the score means
 */
function scoreLevel(score) {
  if (score >= 70) return 'high'
  if (score >= 40) return 'medium'
  return 'low'
}

export default function ScoreCard({ label, score, explanation }) {
  const level = scoreLevel(score)

  return (
    <div className="score-card">
      <span className="score-card__label">{label}</span>
      <span className={`score-card__value score-card__value--${level}`}>
        {score}%
      </span>
      <div className="score-card__bar-track" aria-hidden="true">
        <div
          className={`score-card__bar-fill score-card__bar-fill--${level}`}
          style={{ width: `${score}%` }}
        />
      </div>
      <p className="score-card__explanation">{explanation}</p>
    </div>
  )
}
