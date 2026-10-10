import assert from 'node:assert/strict'
import test from 'node:test'
import {
  createResultsPdf,
  createResultsSummary,
  copyTextToClipboard,
  shareResults,
} from './resultsActions.js'

const result = {
  coverage_score: 72,
  overlap_score: 48,
  matched_skills: ['JavaScript', 'React'],
  missing_skills: ['Docker'],
  extra_skills: ['Figma'],
  suggestions: ['Add a project showing Docker experience.'],
  score_note: 'A small set of skills was identified.',
  score_disclaimer: 'This score is an estimate based on listed skills.',
}

test('summary contains all result fields and excludes source documents', () => {
  const summary = createResultsSummary(result)
  for (const field of ['72%', '48%', 'JavaScript', 'Docker', 'Figma', 'Docker experience', result.score_note, result.score_disclaimer]) {
    assert.ok(summary.includes(field), `summary should contain ${field}`)
  }
  assert.ok(!summary.includes('resume_text'))
  assert.ok(!summary.includes('job_description'))
})

test('copy uses the clipboard and reports clipboard errors', async () => {
  let copied = ''
  await copyTextToClipboard('safe summary', { clipboard: { writeText: async text => { copied = text } } })
  assert.equal(copied, 'safe summary')
  await assert.rejects(
    copyTextToClipboard('summary', { clipboard: { writeText: async () => { throw new Error('denied') } } }),
    /denied/,
  )
})

test('copy uses the legacy clipboard fallback when needed', async () => {
  let command = ''
  let removed = false
  const field = {
    style: {},
    setAttribute() {},
    select() {},
    remove() { removed = true },
  }
  const documentRef = {
    body: { appendChild() {} },
    createElement: () => field,
    execCommand: value => { command = value; return true },
  }
  await copyTextToClipboard('summary', { clipboard: null, documentRef })
  assert.equal(command, 'copy')
  assert.equal(removed, true)
})

test('native share sends only the readable result summary', async () => {
  let payload
  const outcome = await shareResults(result, { share: async data => { payload = data } })
  assert.equal(outcome, 'shared')
  assert.equal(payload.title, 'AI Resume Analyzer Results')
  assert.ok(payload.text.includes('JavaScript'))
  assert.ok(!('resume_text' in payload))
  assert.ok(!('job_description' in payload))
})

test('share cancellation is quiet and unsupported sharing copies instead', async () => {
  const cancelled = await shareResults(result, { share: async () => { throw new DOMException('cancelled', 'AbortError') } })
  assert.equal(cancelled, 'cancelled')

  let copied = ''
  const fallback = await shareResults(result, { share: null, copy: async text => { copied = text } })
  assert.equal(fallback, 'copied')
  assert.ok(copied.includes('72%'))
})

test('share and copy failures are surfaced to the caller', async () => {
  await assert.rejects(shareResults(result, { share: async () => { throw new Error('share failed') } }), /share failed/)
  await assert.rejects(shareResults(result, { share: null, copy: async () => { throw new Error('copy failed') } }), /copy failed/)
})

test('PDF includes all sections and paginates long lists with a report date', () => {
  const longResult = {
    ...result,
    matched_skills: Array.from({ length: 110 }, (_, index) => `Matched skill ${index + 1}`),
  }
  const pdf = createResultsPdf(longResult, new Date(2026, 0, 2))
  assert.ok(pdf.startsWith('%PDF-1.4'))
  assert.ok(pdf.includes('January 2, 2026'))
  for (const heading of ['Score Summary', 'Matched Skills', 'Missing Job Skills', 'Additional Resume Skills', 'Improvement Suggestions']) {
    assert.ok(pdf.includes(heading))
  }
  assert.ok(pdf.includes('Matched skill 110'))
  assert.match(pdf, /\/Count [2-9]\d*\s*>>/)
})
