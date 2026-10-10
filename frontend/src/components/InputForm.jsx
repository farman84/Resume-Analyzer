/**
 * InputForm.jsx — Two-textarea form for resume + job-description input.
 *
 * Props:
 *   onSubmit  {(resumeText: string, jobDescription: string) => void}
 *   isLoading {boolean}
 */
import { useState } from 'react'

const MAX_CHARS = 20_000

export default function InputForm({ onSubmit, isLoading }) {
  const [resumeText, setResumeText]       = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [errors, setErrors]               = useState({})

  function validate() {
    const next = {}
    if (!resumeText.trim())
      next.resume = 'Please paste your resume text.'
    if (!jobDescription.trim())
      next.job = 'Please paste a job description.'
    if (resumeText.length > MAX_CHARS)
      next.resume = `Resume must be at most ${MAX_CHARS.toLocaleString()} characters.`
    if (jobDescription.length > MAX_CHARS)
      next.job = `Job description must be at most ${MAX_CHARS.toLocaleString()} characters.`
    return next
  }

  function handleSubmit(e) {
    e.preventDefault()
    const errs = validate()
    if (Object.keys(errs).length > 0) {
      setErrors(errs)
      return
    }
    setErrors({})
    onSubmit(resumeText, jobDescription)
  }

  const resumeOver = resumeText.length > MAX_CHARS
  const jobOver    = jobDescription.length > MAX_CHARS

  return (
    <form className="form" onSubmit={handleSubmit} noValidate>
      {/* Resume textarea */}
      <div className="field">
        <label
          htmlFor="resume-text"
          className="field__label field__label--required"
        >
          Resume Text
        </label>
        <textarea
          id="resume-text"
          className={`field__textarea${errors.resume ? ' field__textarea--error' : ''}`}
          value={resumeText}
          onChange={e => { setResumeText(e.target.value); setErrors(p => ({ ...p, resume: undefined })) }}
          placeholder="Paste the full text of your resume here…"
          aria-describedby={errors.resume ? 'resume-error' : undefined}
          aria-invalid={!!errors.resume}
          disabled={isLoading}
        />
        <div className="field__footer">
          {errors.resume
            ? <span id="resume-error" className="field__error" role="alert">{errors.resume}</span>
            : <span />}
          <span className={`field__count${resumeOver ? ' field__count--over' : ''}`}>
            {resumeText.length.toLocaleString()} / {MAX_CHARS.toLocaleString()}
          </span>
        </div>
      </div>

      {/* Job description textarea */}
      <div className="field">
        <label
          htmlFor="job-description"
          className="field__label field__label--required"
        >
          Job Description
        </label>
        <textarea
          id="job-description"
          className={`field__textarea${errors.job ? ' field__textarea--error' : ''}`}
          value={jobDescription}
          onChange={e => { setJobDescription(e.target.value); setErrors(p => ({ ...p, job: undefined })) }}
          placeholder="Paste the job description you are applying for here…"
          aria-describedby={errors.job ? 'job-error' : undefined}
          aria-invalid={!!errors.job}
          disabled={isLoading}
        />
        <div className="field__footer">
          {errors.job
            ? <span id="job-error" className="field__error" role="alert">{errors.job}</span>
            : <span />}
          <span className={`field__count${jobOver ? ' field__count--over' : ''}`}>
            {jobDescription.length.toLocaleString()} / {MAX_CHARS.toLocaleString()}
          </span>
        </div>
      </div>

      <div className="form__actions">
        <button
          type="submit"
          className="btn btn--primary"
          disabled={isLoading || resumeOver || jobOver}
          aria-busy={isLoading}
        >
          {isLoading ? 'Analyzing…' : 'Analyze Resume'}
        </button>
      </div>
    </form>
  )
}
