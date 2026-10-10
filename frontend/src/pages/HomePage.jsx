/**
 * HomePage.jsx — Landing page with hero copy and the input form.
 *
 * Props:
 *   onSubmit  {(resumeText: string, jobDescription: string) => void}
 *   isLoading {boolean}
 *   error     {{ title: string, detail: string } | null}
 *   onDismissError {() => void}
 */
import InputForm from '../components/InputForm'
import ErrorMessage from '../components/ErrorMessage'

export default function HomePage({ onSubmit, isLoading, error, onDismissError }) {
  return (
    <main className="page">
      <div className="container">
        <div className="hero">
          <h1 className="hero__title">AI Resume Analyzer</h1>
          <p className="hero__subtitle">
            Paste your resume and a job description below. We&rsquo;ll extract the skills
            mentioned in each, calculate how well your resume covers the role&rsquo;s
            requirements, and suggest where to focus next.
          </p>
        </div>

        {error && (
          <div style={{ marginBottom: '1.5rem' }}>
            <ErrorMessage
              title={error.title}
              detail={error.detail}
              onDismiss={onDismissError}
            />
          </div>
        )}

        <div className="card">
          <InputForm onSubmit={onSubmit} isLoading={isLoading} />
        </div>
      </div>
    </main>
  )
}
