/**
 * Suggestions.jsx — Numbered list of backend improvement suggestions.
 *
 * Props:
 *   suggestions {string[]}  Array of suggestion strings from the API
 */
export default function Suggestions({ suggestions = [] }) {
  return (
    <div className="suggestions-section">
      <div className="suggestions-section__header">
        <i className="suggestions-section__icon" aria-hidden="true">&#128161;</i>
        <h3 className="suggestions-section__title">Improvement Suggestions</h3>
      </div>

      {suggestions.length === 0 ? (
        <p className="suggestions-empty">
          No specific suggestions — your resume looks well-aligned with this role.
        </p>
      ) : (
        <ol className="suggestions-list" aria-label="Improvement suggestions">
          {suggestions.map((text, i) => (
            <li key={i} className="suggestions-list__item">
              <span className="suggestions-list__bullet" aria-hidden="true">
                {i + 1}
              </span>
              <span>{text}</span>
            </li>
          ))}
        </ol>
      )}
    </div>
  )
}
