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
import { useEffect, useState } from 'react'
import './styles/index.css'

import HomePage    from './pages/HomePage'
import ResultsPage from './pages/ResultsPage'
import LoadingSpinner from './components/LoadingSpinner'
import { analyzeResume } from './api/analyzeApi'

export default function App() {
  const [theme, setTheme] = useState(() => {
    try {
      return localStorage.getItem('theme') === 'dark' ? 'dark' : 'light'
    } catch {
      return 'light'
    }
  })
  const [status, setStatus]   = useState('idle')   // 'idle' | 'loading' | 'results' | 'error'
  const [result, setResult]   = useState(null)
  const [error,  setError]    = useState(null)      // { title, detail }

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    try {
      localStorage.setItem('theme', theme)
    } catch {
      // The selected theme still works when browser storage is unavailable.
    }
  }, [theme])

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
        <Header theme={theme} onToggleTheme={() => setTheme(current => current === 'light' ? 'dark' : 'light')} />
        <ResultsPage result={result} onReset={handleReset} />
      </>
    )
  }

  return (
    <>
      <Header theme={theme} onToggleTheme={() => setTheme(current => current === 'light' ? 'dark' : 'light')} />
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

function Header({ theme, onToggleTheme }) {
  return (
    <header className="site-header">
      <div className="container">
        <div className="site-header__inner">
          <span className="site-header__logo">AI Resume Analyzer</span>
          <button
            type="button"
            className="theme-toggle"
            onClick={onToggleTheme}
            aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
            title={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
          >
            {theme === 'light' ? (
              <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="4" />
                <path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42" />
              </svg>
            ) : (
              <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d="M20.2 15.3A8.5 8.5 0 0 1 8.7 3.8 8.5 8.5 0 1 0 20.2 15.3Z" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </header>
  )
}
