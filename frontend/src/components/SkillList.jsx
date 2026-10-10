/**
 * SkillList.jsx — Renders a titled section of skill chips.
 *
 * Props:
 *   title    {string}   Section heading
 *   skills   {string[]} Array of canonical skill names
 *   variant  {'matched'|'missing'|'extra'}  Controls chip colour
 *   icon     {string}   Decorative character (e.g. "✓", "✗", "+")
 *   emptyMessage {string}  Text shown when skills array is empty
 */
export default function SkillList({ title, skills = [], variant = 'matched', icon, emptyMessage }) {
  return (
    <div className="skill-section">
      <div className="skill-section__header">
        {icon && <i className="skill-section__icon" aria-hidden="true">{icon}</i>}
        <h3 className="skill-section__title">{title}</h3>
        <span className="skill-section__count">{skills.length}</span>
      </div>

      {skills.length === 0 ? (
        <p className="skill-empty">
          {emptyMessage ?? 'None identified.'}
        </p>
      ) : (
        <div className="skill-chips" aria-label={title}>
          {skills.map(skill => (
            <span key={skill} className={`chip chip--${variant}`}>
              {skill}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}
