/**
 * ResultsPage.jsx — Displays the full analysis from the backend.
 *
 * Props:
 *   result  {AnalyzeResult}   Parsed API response object
 *   onReset {() => void}      Called when "Analyze Again" is clicked
 */
import { useState } from 'react'
import ScoreCard from '../components/ScoreCard'
import SkillList from '../components/SkillList'
import Suggestions from '../components/Suggestions'
import {
  COVERAGE_EXPLANATION,
  OVERLAP_EXPLANATION,
  createResultsSummary,
  copyTextToClipboard,
  downloadResultsPdf,
  shareResults,
} from '../utils/resultsActions'

const NO_SKILLS_MESSAGE =
  "We couldn't identify specific skills in this text. " +
  "Try adding more detail or specific technology names."

export default function ResultsPage({ result, onReset }) {
  const [actionMessage, setActionMessage] = useState('')
  const {
    coverage_score,
    overlap_score,
    matched_skills,
    missing_skills,
    extra_skills,
    suggestions,
    score_note,
    score_disclaimer,
  } = result

  const noSkillsFound =
    matched_skills.length === 0 &&
    missing_skills.length === 0 &&
    extra_skills.length === 0

  async function handleCopy() {
    setActionMessage('')
    try {
      await copyTextToClipboard(createResultsSummary(result))
      setActionMessage('Results copied to clipboard.')
    } catch {
      setActionMessage('Could not copy results. Please check clipboard access and try again.')
    }
  }

  async function handleShare() {
    setActionMessage('')
    try {
      const outcome = await shareResults(result)
      if (outcome === 'shared') setActionMessage('Share sheet opened with your results.')
      if (outcome === 'copied') setActionMessage('Sharing is unavailable; results copied to clipboard.')
    } catch {
      setActionMessage('Could not share results. Please try copying them instead.')
    }
  }

  function handleDownload() {
    setActionMessage('')
    try {
      downloadResultsPdf(result)
      setActionMessage('PDF report downloaded.')
    } catch {
      setActionMessage('Could not create the PDF report. Please try again.')
    }
  }

  return (
    <main className="page">
      <div className="container">

        {/* Page header */}
        <div className="results-header">
          <h2 className="results-header__title">Analysis Results</h2>
          <button
            type="button"
            className="btn btn--secondary btn--sm"
            onClick={onReset}
          >
            &#8592; Analyze Again
          </button>
        </div>

        <div className="results-actions" aria-label="Result actions">
          <button type="button" className="btn btn--secondary" onClick={handleDownload} aria-label="Download results as PDF">
            Download PDF
          </button>
          <button type="button" className="btn btn--secondary" onClick={handleShare} aria-label="Share results summary">
            Share Results
          </button>
          <button type="button" className="btn btn--secondary" onClick={handleCopy} aria-label="Copy results summary">
            Copy Results
          </button>
        </div>
        <p className="results-actions__feedback" role="status" aria-live="polite">{actionMessage}</p>

        {/* Score disclaimer */}
        <div className="disclaimer">
          <i className="disclaimer__icon" aria-hidden="true">&#8505;</i>
          <span>{score_disclaimer}</span>
        </div>

        {/* Score note (only shown for edge-case responses) */}
        {score_note && (
          <div className="score-note" role="note">
            {score_note}
          </div>
        )}

        {/* Two score cards */}
        <div className="score-grid">
          <ScoreCard
            label="Job Requirement Coverage"
            score={coverage_score}
            explanation={COVERAGE_EXPLANATION}
          />
          <ScoreCard
            label="Overall Skill Overlap"
            score={overlap_score}
            explanation={OVERLAP_EXPLANATION}
          />
        </div>

        {/* Empty-results message */}
        {noSkillsFound && (
          <div className="empty-state">
            <div className="empty-state__icon" aria-hidden="true">&#128269;</div>
            <p className="empty-state__text">{NO_SKILLS_MESSAGE}</p>
          </div>
        )}

        {/* Skill sections */}
        {!noSkillsFound && (
          <div className="results-sections">
            <SkillList
              title="Matched Skills"
              skills={matched_skills}
              variant="matched"
              icon="✓"
              emptyMessage="No skills matched between your resume and the job description."
            />
            <SkillList
              title="Missing Job Skills"
              skills={missing_skills}
              variant="missing"
              icon="✗"
              emptyMessage="Great — your resume covers all skills mentioned in the job description."
            />
            <SkillList
              title="Additional Resume Skills"
              skills={extra_skills}
              variant="extra"
              icon="+"
              emptyMessage="No additional skills found in your resume beyond the job requirements."
            />
          </div>
        )}

        {/* Suggestions */}
        <div style={{ marginTop: '1.25rem' }}>
          <Suggestions suggestions={suggestions} />
        </div>

      </div>
    </main>
  )
}
