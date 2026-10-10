/**
 * analyzeApi.js — Fetch wrapper for POST /api/analyze.
 *
 * The Vite dev server proxies /api/* → http://localhost:8000,
 * so no hardcoded origin is needed here.
 *
 * Returns the parsed JSON body on success.
 * Throws an Error with a user-friendly `.message` on failure.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV ? 'http://localhost:8000' : 'https://resume-analyzer-nq0q.onrender.com')

const ANALYZE_URL = `${API_BASE_URL}/api/analyze`
/**
 * @typedef {Object} AnalyzeResult
 * @property {number}   coverage_score
 * @property {number}   overlap_score
 * @property {string[]} matched_skills
 * @property {string[]} missing_skills
 * @property {string[]} resume_skills
 * @property {string[]} job_skills
 * @property {string[]} extra_skills
 * @property {string[]} suggestions
 * @property {string|null} score_note
 * @property {string}   score_disclaimer
 */

/**
 * Send resume and job-description text to the backend for analysis.
 *
 * @param {string} resumeText
 * @param {string} jobDescription
 * @returns {Promise<AnalyzeResult>}
 * @throws {Error} with a user-readable message
 */
export async function analyzeResume(resumeText, jobDescription) {
  let response

  try {
    response = await fetch(ANALYZE_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        resume_text: resumeText,
        job_description: jobDescription,
      }),
    })
  } catch {
    // Network-level failure (backend not running, DNS, etc.)
    throw new Error(
      'Could not reach the analysis server. ' +
      'Make sure the backend is running on http://localhost:8000.'
    )
  }

  if (response.ok) {
    return response.json()
  }

  // HTTP 422 — Pydantic validation error from FastAPI
  if (response.status === 422) {
    let body
    try { body = await response.json() } catch { body = null }

    // FastAPI 422 bodies look like { detail: [ { msg, loc, type } ] }
    const detail = body?.detail
    let message = 'Please check your inputs and try again.'
    if (Array.isArray(detail) && detail.length > 0) {
      message = detail.map(d => d.msg ?? String(d)).join(' ')
    } else if (typeof detail === 'string') {
      message = detail
    }
    const err = new Error(message)
    err.status = 422
    throw err
  }

  // Any other HTTP error
  const err = new Error(
    `The server returned an unexpected error (HTTP ${response.status}). ` +
    'Please try again.'
  )
  err.status = response.status
  throw err
}
