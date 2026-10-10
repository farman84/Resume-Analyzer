/**
 * LoadingSpinner.jsx — Centered spinner shown while the API call is in flight.
 */
export default function LoadingSpinner() {
  return (
    <div className="spinner-wrap" role="status" aria-live="polite">
      <div className="spinner" aria-hidden="true" />
      <span>Analyzing your resume&hellip;</span>
    </div>
  )
}
