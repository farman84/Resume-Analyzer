export const COVERAGE_EXPLANATION = "Percentage of the job's required skills found in your resume."
export const OVERLAP_EXPLANATION = 'Percentage of all skills mentioned across both documents that you share.'

const sections = [
  ['Matched Skills', 'matched_skills'],
  ['Missing Job Skills', 'missing_skills'],
  ['Additional Resume Skills', 'extra_skills'],
]

export function createResultsSummary(result) {
  const lines = [
    'AI Resume Analyzer — Results',
    `Job Requirement Coverage: ${result.coverage_score}%`,
    COVERAGE_EXPLANATION,
    `Overall Skill Overlap: ${result.overlap_score}%`,
    OVERLAP_EXPLANATION,
  ]

  if (result.score_note) lines.push('', `Score note: ${result.score_note}`)
  if (result.score_disclaimer) lines.push('', result.score_disclaimer)

  for (const [title, key] of sections) {
    lines.push('', `${title}:`)
    const skills = result[key] ?? []
    lines.push(...(skills.length ? skills.map(skill => `• ${skill}`) : ['• None identified']))
  }

  lines.push('', 'Improvement Suggestions:')
  const suggestions = result.suggestions ?? []
  lines.push(...(suggestions.length
    ? suggestions.map((suggestion, index) => `${index + 1}. ${suggestion}`)
    : ['No specific suggestions.']))

  return lines.join('\n')
}

export async function copyTextToClipboard(text, {
  clipboard = globalThis.navigator?.clipboard,
  documentRef = globalThis.document,
} = {}) {
  if (clipboard?.writeText) {
    await clipboard.writeText(text)
    return
  }

  if (!documentRef?.body || !documentRef.execCommand) {
    throw new Error('Clipboard access is unavailable in this browser.')
  }

  const field = documentRef.createElement('textarea')
  field.value = text
  field.setAttribute('readonly', '')
  field.style.position = 'fixed'
  field.style.opacity = '0'
  documentRef.body.appendChild(field)
  field.select()

  try {
    if (!documentRef.execCommand('copy')) {
      throw new Error('The browser could not copy the results.')
    }
  } finally {
    field.remove()
  }
}

export async function shareResults(result, {
  share = globalThis.navigator?.share?.bind(globalThis.navigator),
  copy = copyTextToClipboard,
} = {}) {
  const text = createResultsSummary(result)

  if (!share) {
    await copy(text)
    return 'copied'
  }

  try {
    await share({ title: 'AI Resume Analyzer Results', text })
    return 'shared'
  } catch (error) {
    if (error?.name === 'AbortError') return 'cancelled'
    throw error
  }
}

const PAGE_WIDTH = 595
const PAGE_HEIGHT = 842
const LEFT = 48
const RIGHT = 48
const BOTTOM = 54
const BODY_WIDTH = PAGE_WIDTH - LEFT - RIGHT

function pdfSafe(value) {
  return String(value)
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[—–−]/g, '-')
    .replace(/[‘’]/g, "'")
    .replace(/[“”]/g, '"')
    .replace(/•/g, '-')
    .replace(/[^\x20-\x7E]/g, '?')
}

function escapePdfText(value) {
  return pdfSafe(value).replaceAll('\\', '\\\\').replaceAll('(', '\\(').replaceAll(')', '\\)')
}

function makePdfPages(result, reportDate) {
  const pages = [[]]
  let pageIndex = 0
  let y = 132

  function command(value) { pages[pageIndex].push(value) }
  function newPage() {
    pages.push([])
    pageIndex += 1
    y = 58
  }
  function ensureSpace(height) {
    if (y + height > PAGE_HEIGHT - BOTTOM) newPage()
  }
  function drawText(text, x, top, size, color, bold = false) {
    const [red, green, blue] = color
    command(`BT /${bold ? 'F2' : 'F1'} ${size} Tf ${red} ${green} ${blue} rg 1 0 0 1 ${x} ${PAGE_HEIGHT - top} Tm (${escapePdfText(text)}) Tj ET`)
  }
  function wrap(text, maxChars) {
    const words = pdfSafe(text).split(/\s+/)
    const lines = []
    let line = ''
    for (const word of words) {
      if (!line) line = word
      else if (`${line} ${word}`.length <= maxChars) line += ` ${word}`
      else {
        lines.push(line)
        line = word
      }
      while (line.length > maxChars) {
        lines.push(line.slice(0, maxChars))
        line = line.slice(maxChars)
      }
    }
    if (line) lines.push(line)
    return lines.length ? lines : ['']
  }
  function paragraph(text, { indent = 0, size = 10, color = [0.16, 0.2, 0.27], gap = 3 } = {}) {
    const maxChars = Math.floor((BODY_WIDTH - indent) / (size * 0.52))
    const lines = wrap(text, maxChars)
    ensureSpace(lines.length * (size + 4) + gap)
    for (const line of lines) {
      drawText(line, LEFT + indent, y, size, color)
      y += size + 4
    }
    y += gap
  }
  function heading(title) {
    ensureSpace(38)
    y += 10
    drawText(title, LEFT, y, 13, [0.1, 0.24, 0.43], true)
    y += 7
    command(`0.84 0.88 0.92 RG 0.7 w ${LEFT} ${PAGE_HEIGHT - y} m ${PAGE_WIDTH - RIGHT} ${PAGE_HEIGHT - y} l S`)
    y += 16
  }
  function listSection(title, values) {
    const items = values.length ? values : ['None identified']
    const firstItemLines = wrap(`${values.length ? '1.' : '-'} ${items[0]}`, Math.floor((BODY_WIDTH - 8) / (10 * 0.52))).length
    ensureSpace(38 + firstItemLines * 14 + 2)
    heading(title)
    items.forEach((item, index) => paragraph(`${values.length ? `${index + 1}.` : '-'} ${item}`, { indent: 8, gap: 2 }))
  }

  command('0.12 0.29 0.52 rg 0 750 595 92 re f')
  drawText('AI RESUME ANALYZER', LEFT, 777, 10, [0.82, 0.89, 0.98], true)
  drawText('Resume Analysis Report', LEFT, 808, 23, [1, 1, 1], true)
  drawText(`Generated ${reportDate}`, LEFT, 826, 9, [0.88, 0.92, 0.97])

  heading('Score Summary')
  paragraph(`Job Requirement Coverage: ${result.coverage_score}%`, { size: 12, color: [0.08, 0.31, 0.62], gap: 1 })
  paragraph(COVERAGE_EXPLANATION, { indent: 4, size: 9, color: [0.32, 0.38, 0.45], gap: 5 })
  paragraph(`Overall Skill Overlap: ${result.overlap_score}%`, { size: 12, color: [0.08, 0.31, 0.62], gap: 1 })
  paragraph(OVERLAP_EXPLANATION, { indent: 4, size: 9, color: [0.32, 0.38, 0.45], gap: 5 })
  if (result.score_note) paragraph(`Score note: ${result.score_note}`, { size: 9 })
  if (result.score_disclaimer) paragraph(`Score explanation: ${result.score_disclaimer}`, { size: 9 })

  listSection('Matched Skills', result.matched_skills ?? [])
  listSection('Missing Job Skills', result.missing_skills ?? [])
  listSection('Additional Resume Skills', result.extra_skills ?? [])
  listSection('Improvement Suggestions', result.suggestions ?? [])

  return pages
}

export function createResultsPdf(result, generatedAt = new Date()) {
  const reportDate = generatedAt.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })
  const pages = makePdfPages(result, reportDate)
  const objects = []
  const addObject = body => { objects.push(body); return objects.length }
  const catalogId = addObject('')
  const pagesId = addObject('')
  const regularFontId = addObject('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>')
  const boldFontId = addObject('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>')
  const pageIds = []

  for (const page of pages) {
    const pageContent = [...page]
    const pageId = objects.length + 1
    const contentId = pageId + 1
    const pageNumber = pageIds.length + 1
    pageContent.push(`0.84 0.88 0.92 RG 0.6 w ${LEFT} 42 m ${PAGE_WIDTH - RIGHT} 42 l S`)
    pageContent.push(`BT /F1 8 Tf 0.38 0.43 0.5 rg 1 0 0 1 ${LEFT} 27 Tm (AI Resume Analyzer - Private report) Tj ET`)
    pageContent.push(`BT /F1 8 Tf 0.38 0.43 0.5 rg 1 0 0 1 ${PAGE_WIDTH - RIGHT - 65} 27 Tm (Page ${pageNumber} of ${pages.length}) Tj ET`)
    const stream = pageContent.join('\n')
    addObject(`<< /Type /Page /Parent ${pagesId} 0 R /MediaBox [0 0 ${PAGE_WIDTH} ${PAGE_HEIGHT}] /Resources << /Font << /F1 ${regularFontId} 0 R /F2 ${boldFontId} 0 R >> >> /Contents ${contentId} 0 R >>`)
    addObject(`<< /Length ${stream.length} >>\nstream\n${stream}\nendstream`)
    pageIds.push(pageId)
  }

  objects[catalogId - 1] = `<< /Type /Catalog /Pages ${pagesId} 0 R >>`
  objects[pagesId - 1] = `<< /Type /Pages /Kids [${pageIds.map(id => `${id} 0 R`).join(' ')}] /Count ${pageIds.length} >>`

  let pdf = '%PDF-1.4\n'
  const offsets = [0]
  objects.forEach((object, index) => {
    offsets.push(pdf.length)
    pdf += `${index + 1} 0 obj\n${object}\nendobj\n`
  })
  const xrefOffset = pdf.length
  pdf += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`
  for (const offset of offsets.slice(1)) pdf += `${String(offset).padStart(10, '0')} 00000 n \n`
  pdf += `trailer\n<< /Size ${objects.length + 1} /Root ${catalogId} 0 R >>\nstartxref\n${xrefOffset}\n%%EOF`
  return pdf
}

export function downloadResultsPdf(result, generatedAt = new Date(), documentRef = globalThis.document) {
  const pdf = createResultsPdf(result, generatedAt)
  const blob = new Blob([pdf], { type: 'application/pdf' })
  const url = URL.createObjectURL(blob)
  const link = documentRef.createElement('a')
  link.href = url
  link.download = `resume-analysis-${generatedAt.toISOString().slice(0, 10)}.pdf`
  documentRef.body.appendChild(link)
  link.click()
  link.remove()
  globalThis.setTimeout(() => URL.revokeObjectURL(url), 1000)
}
