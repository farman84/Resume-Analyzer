/**
 * App.jsx — Root component and application state machine.
 *
 * States:
 *   idle      → shows HomePage with InputForm
 *   loading   → shows HomePage with spinner in the submit button
 *   results   → shows ResultsPage
 *   error     → shows HomePage with ErrorMessage banner
 *
 * No React Router — the app has two views and a single back action.
 */
import { useState } from 'react'
import './styles/index.css'

import HomePage    from './pages/HomePage'
import ResultsPage from './pages/ResultsPage'
import LoadingSpinner from './components/LoadingSpinner'
import { analyzeResume } from './api/analyzeApi'

export default function App() {
  const [status, setStatus]   = useState('idle')   // 'idle' | 'loading' | 'results' | 'error'
  const [result, setResult]   = useState(null)
  const [error,  setError]    = useState(null)      // { title, detail }

  async function handleSubmit(resumeText, jobDescription) {
    setStatus('loading')
    setError(null)
    try {
      const data = await analyzeResume(resumeText, jobDescription)
      setResult(data)
      setStatus('results')
    } catch (err) {
      setError({
        title:  'Analysis failed',
        detail: err.message ?? 'An unexpected error occurred. Please try again.',
      })
      setStatus('error')
    }
  }

  function handleReset() {
    setStatus('idle')
    setResult(null)
    setError(null)
  }

  function handleDismissError() {
    setError(null)
    setStatus('idle')
  }

  if (status === 'results' && result) {
    return (
      <>
        <Header />
        <ResultsPage result={result} onReset={handleReset} />
      </>
    )
  }

  return (
    <>
      <Header />
      {status === 'loading' && <LoadingSpinner />}
      {status !== 'loading' && (
        <HomePage
          onSubmit={handleSubmit}
          isLoading={status === 'loading'}
          error={status === 'error' ? error : null}
          onDismissError={handleDismissError}
        />
      )}
    </>
  )
}

function Header() {
  return (
    <header className="site-header">
      <div className="container">
        <div className="site-header__inner">
          <span className="site-header__logo">AI Resume Analyzer</span>
        </div>
      </div>
    </header>
  )
}
