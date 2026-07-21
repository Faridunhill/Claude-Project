import type { jsPDF } from 'jspdf'

export interface PassportPdfData {
  referenceId: string
  ownerName: string
  brand: string
  model_or_line: string
  shape: string
  estimated_era: string
  confidence: string
  stamping_reading: string
  dating_rationale: string
  condition_notes: string
  expert_summary: string
  /** JPEG data URL of the left-profile photo, embedded on the passport */
  photoDataUrl?: string
}

const PARCHMENT = '#F5EDD6'
const MAHOGANY = '#2C1810'
const GOLD = '#A8842C'
const BROWN = '#6B5138'

const CONFIDENCE_LABELS: Record<string, string> = {
  high: 'High Confidence',
  medium: 'Medium Confidence',
  low: 'Low Confidence — Preliminary',
}

export async function generatePassportPdf(data: PassportPdfData): Promise<void> {
  const { jsPDF: JsPDF } = await import('jspdf')
  const doc: jsPDF = new JsPDF({ unit: 'mm', format: 'a4' })

  const W = 210
  const H = 297
  const M = 18 // page margin
  const CONTENT_W = W - M * 2

  // Parchment background
  doc.setFillColor(PARCHMENT)
  doc.rect(0, 0, W, H, 'F')

  // Diagonal watermark
  doc.setTextColor(232, 213, 163)
  doc.setFont('times', 'bold')
  doc.setFontSize(52)
  doc.text('FARIDUNHILL', W / 2, H / 2 + 30, { align: 'center', angle: 35 })

  // Border frame
  doc.setDrawColor(GOLD)
  doc.setLineWidth(0.8)
  doc.rect(M / 2, M / 2, W - M, H - M)
  doc.setLineWidth(0.25)
  doc.rect(M / 2 + 2, M / 2 + 2, W - M - 4, H - M - 4)

  let y = M + 8

  // Header
  doc.setTextColor(GOLD)
  doc.setFont('times', 'italic')
  doc.setFontSize(11)
  doc.text('~ Faridunhill · Est. 2015 ~', W / 2, y, { align: 'center' })
  y += 9
  doc.setTextColor(MAHOGANY)
  doc.setFont('times', 'bold')
  doc.setFontSize(26)
  doc.text('PIPE PASSPORT', W / 2, y, { align: 'center' })
  y += 7
  doc.setFont('times', 'normal')
  doc.setFontSize(12)
  doc.setTextColor(GOLD)
  doc.text(data.referenceId, W / 2, y, { align: 'center' })
  y += 4
  doc.setDrawColor(GOLD)
  doc.setLineWidth(0.5)
  doc.line(M + 20, y, W - M - 20, y)
  y += 8

  // Photo (left profile) — right-aligned box
  const photoW = 52
  const photoH = 39
  if (data.photoDataUrl) {
    try {
      doc.addImage(data.photoDataUrl, 'JPEG', W - M - photoW, y, photoW, photoH)
      doc.setLineWidth(0.4)
      doc.rect(W - M - photoW, y, photoW, photoH)
    } catch {
      // photo embedding is best-effort
    }
  }

  // Identity fields (left column beside the photo, then full width)
  const fields: Array<[string, string]> = [
    ['Owner', data.ownerName],
    ['Brand', data.brand],
    ['Model / Line', data.model_or_line],
    ['Shape', data.shape],
    ['Estimated Era', data.estimated_era],
    ['Assessment', CONFIDENCE_LABELS[data.confidence] ?? data.confidence],
  ]

  doc.setFontSize(10.5)
  for (const [label, value] of fields) {
    const colW = data.photoDataUrl && y < M + 25 + photoH ? CONTENT_W - photoW - 8 : CONTENT_W
    doc.setFont('times', 'bold')
    doc.setTextColor(BROWN)
    doc.text(label.toUpperCase(), M, y)
    doc.setFont('times', 'normal')
    doc.setTextColor(MAHOGANY)
    const lines = doc.splitTextToSize(value || '—', colW - 38)
    doc.text(lines, M + 38, y)
    y += Math.max(6.5, lines.length * 5 + 1.5)
  }

  y = Math.max(y, M + 30 + photoH + 6)

  // Long-form sections
  const sections: Array<[string, string]> = [
    ['Stamping', data.stamping_reading],
    ['Dating Rationale', data.dating_rationale],
    ['Condition', data.condition_notes],
    ["The Tobacconist's Summary", data.expert_summary],
  ]

  for (const [title, body] of sections) {
    doc.setFont('times', 'bold')
    doc.setFontSize(11)
    doc.setTextColor(GOLD)
    doc.text(title, M, y)
    y += 5.5
    doc.setFont('times', 'normal')
    doc.setFontSize(10)
    doc.setTextColor(MAHOGANY)
    const lines = doc.splitTextToSize(body || '—', CONTENT_W)
    doc.text(lines, M, y)
    y += lines.length * 4.6 + 6
  }

  // Footer disclaimer, pinned to the bottom inside the frame
  const disclaimer =
    'The Faridunhill Pipe Passport is an identification and dating assessment based on comparative visual ' +
    'analysis, historical catalogues, and market data. Results are professional opinions, not certificates ' +
    'of authenticity. Verify this passport by its reference number at faridunhill.com.'
  doc.setFont('times', 'italic')
  doc.setFontSize(8)
  doc.setTextColor(BROWN)
  const discLines = doc.splitTextToSize(disclaimer, CONTENT_W)
  const discY = H - M - discLines.length * 3.6 - 2
  doc.setDrawColor(GOLD)
  doc.setLineWidth(0.25)
  doc.line(M, discY - 4, W - M, discY - 4)
  doc.text(discLines, M, discY)

  doc.save(`Faridunhill-Pipe-Passport-${data.referenceId}.pdf`)
}
