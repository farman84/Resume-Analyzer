/**
 * ErrorMessage.jsx — Dismissable error banner.
 *
 * Props:
 *   title   {string}   Bold heading (e.g. "Analysis failed")
 *   detail  {string}   Longer explanation
 *   onDismiss {() => void}  Called when the × button is clicked
 */
export default function ErrorMessage({ title, detail, onDismiss }) {
  return (
    <div className="error-banner" role="alert">
      <span className="error-banner__icon" aria-hidden="true">&#9888;</span>
      <div className="error-banner__body">
        {title && <p className="error-banner__title">{title}</p>}
        {detail && <p className="error-banner__detail">{detail}</p>}
      </div>
      {onDismiss && (
        <button
          className="error-banner__dismiss"
          onClick={onDismiss}
          aria-label="Dismiss error"
          type="button"
        >
          &times;
        </button>
      )}
    </div>
  )
}
