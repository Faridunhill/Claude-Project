/**
 * Bulk Pipe Passport calibration runner.
 *
 * Runs every pipe in a cabinet folder through the identification engine —
 * one pipe per analysis (never mixed), several in parallel — and writes
 * results to CSV + JSON for comparison against known truth.
 *
 * Folder layout (one subfolder per pipe):
 *
 *   test-cabinet/
 *     001-dunhill-shell/
 *       left.jpg  right.jpg  top.jpg  bottom.jpg  stampA.jpg  [stampB.jpg]
 *       [info.json]   — optional: {"brandGuess": "...", "stampText": "...",
 *                       "length": "...", "notes": "...", "truth": "Dunhill Shell 1962"}
 *     002-peterson-system/
 *       ...
 *
 * Filename matching is forgiving: "left*", "right*", "top*", "bottom*",
 * "stampA*"/"stamp1*", "stampB*"/"stamp2*", any of .jpg/.jpeg/.png/.webp.
 * (iPhone users: export photos as JPEG, not HEIC.)
 *
 * Usage:
 *   ANTHROPIC_API_KEY=sk-... npx tsx scripts/bulk-test.ts [cabinet-dir]
 *
 * Resumable: already-completed pipes in results.json are skipped, so an
 * interrupted run continues where it left off.
 */

import fs from 'fs'
import path from 'path'
import sharp from 'sharp'
import { analyzePipe, REQUIRED_VIEWS, type PassportAssessment, type PassportMeta } from '../lib/passport-engine'

const CABINET_DIR = process.argv[2] || 'test-cabinet'
const OUT_DIR = path.join(CABINET_DIR, 'results')
const RESULTS_JSON = path.join(OUT_DIR, 'results.json')
const RESULTS_CSV = path.join(OUT_DIR, 'results.csv')

const CONCURRENCY = 3
const MAX_DIMENSION = 1600
const JPEG_QUALITY = 82
const MAX_RETRIES = 4

const VIEW_PATTERNS: Array<[string, RegExp]> = [
  ['left', /^left/i],
  ['right', /^right/i],
  ['top', /^top/i],
  ['bottom', /^bottom/i],
  ['stampA', /^(stampa|stamp1|stamp[^b2]|stamp$)/i],
  ['stampB', /^(stampb|stamp2)/i],
]

const IMAGE_EXTS = new Set(['.jpg', '.jpeg', '.png', '.webp'])

interface PipeResult {
  folder: string
  status: 'ok' | 'error' | 'skipped'
  error?: string
  truth?: string
  assessment?: PassportAssessment
  seconds?: number
}

function findPhotos(dir: string): Record<string, string> {
  const files = fs.readdirSync(dir).filter((f) => IMAGE_EXTS.has(path.extname(f).toLowerCase()))
  const found: Record<string, string> = {}
  for (const [view, pattern] of VIEW_PATTERNS) {
    if (found[view]) continue
    const match = files.find((f) => pattern.test(path.basename(f, path.extname(f))))
    if (match) found[view] = path.join(dir, match)
  }
  return found
}

async function compressToBase64(filePath: string): Promise<string> {
  const buf = await sharp(filePath)
    .rotate() // respect EXIF orientation
    .resize(MAX_DIMENSION, MAX_DIMENSION, { fit: 'inside', withoutEnlargement: true })
    .jpeg({ quality: JPEG_QUALITY })
    .toBuffer()
  return buf.toString('base64')
}

function readInfo(dir: string): PassportMeta & { truth?: string } {
  const infoPath = path.join(dir, 'info.json')
  if (!fs.existsSync(infoPath)) return {}
  try {
    return JSON.parse(fs.readFileSync(infoPath, 'utf8'))
  } catch {
    console.warn(`  ⚠ ${path.basename(dir)}: info.json is not valid JSON — ignoring it`)
    return {}
  }
}

async function withRetry<T>(fn: () => Promise<T>): Promise<T> {
  let lastErr: unknown
  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    try {
      return await fn()
    } catch (err: unknown) {
      lastErr = err
      const status = (err as { status?: number }).status
      const retryable = status === 429 || status === 529 || (status !== undefined && status >= 500)
      if (!retryable || attempt === MAX_RETRIES) throw err
      const delay = 2000 * 2 ** attempt
      console.warn(`  ⚠ transient error (${status}), retrying in ${delay / 1000}s...`)
      await new Promise((r) => setTimeout(r, delay))
    }
  }
  throw lastErr
}

async function processPipe(folder: string): Promise<PipeResult> {
  const dir = path.join(CABINET_DIR, folder)
  const info = readInfo(dir)
  const photoPaths = findPhotos(dir)

  const missing = REQUIRED_VIEWS.filter((v) => !photoPaths[v])
  if (missing.length > 0) {
    return {
      folder,
      status: 'skipped',
      truth: info.truth,
      error: `missing photos: ${missing.join(', ')}`,
    }
  }

  const started = Date.now()
  const photos: Array<{ view: string; base64: string }> = []
  for (const [view, filePath] of Object.entries(photoPaths)) {
    photos.push({ view, base64: await compressToBase64(filePath) })
  }

  const assessment = await withRetry(() =>
    analyzePipe(photos, {
      brandGuess: info.brandGuess,
      stampText: info.stampText,
      length: info.length,
      notes: info.notes,
    })
  )

  return {
    folder,
    status: 'ok',
    truth: info.truth,
    assessment,
    seconds: Math.round((Date.now() - started) / 1000),
  }
}

function csvField(value: unknown): string {
  const s = String(value ?? '')
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
}

function writeOutputs(results: PipeResult[]) {
  fs.mkdirSync(OUT_DIR, { recursive: true })
  fs.writeFileSync(RESULTS_JSON, JSON.stringify(results, null, 2))

  const header = [
    'folder', 'status', 'truth', 'brand', 'model_or_line', 'shape', 'estimated_era',
    'confidence', 'stamping_reading', 'dating_rationale', 'condition_notes', 'expert_summary',
    'seconds', 'error',
  ]
  const lines = [header.join(',')]
  for (const r of results) {
    lines.push(
      [
        r.folder, r.status, r.truth,
        r.assessment?.brand, r.assessment?.model_or_line, r.assessment?.shape,
        r.assessment?.estimated_era, r.assessment?.confidence, r.assessment?.stamping_reading,
        r.assessment?.dating_rationale, r.assessment?.condition_notes, r.assessment?.expert_summary,
        r.seconds, r.error,
      ]
        .map(csvField)
        .join(',')
    )
  }
  fs.writeFileSync(RESULTS_CSV, lines.join('\n'))
}

async function main() {
  if (!process.env.ANTHROPIC_API_KEY) {
    console.error('ANTHROPIC_API_KEY is not set. Run: ANTHROPIC_API_KEY=sk-... npx tsx scripts/bulk-test.ts')
    process.exit(1)
  }
  if (!fs.existsSync(CABINET_DIR)) {
    console.error(`Cabinet folder "${CABINET_DIR}" not found. Create it with one subfolder per pipe.`)
    process.exit(1)
  }

  const folders = fs
    .readdirSync(CABINET_DIR, { withFileTypes: true })
    .filter((d) => d.isDirectory() && d.name !== 'results')
    .map((d) => d.name)
    .sort()

  // Resume: keep prior ok/skipped results, redo errors
  const prior: PipeResult[] = fs.existsSync(RESULTS_JSON)
    ? JSON.parse(fs.readFileSync(RESULTS_JSON, 'utf8'))
    : []
  const done = new Map(prior.filter((r) => r.status === 'ok').map((r) => [r.folder, r]))

  const todo = folders.filter((f) => !done.has(f))
  console.log(`Cabinet: ${folders.length} pipes · ${done.size} already done · ${todo.length} to run · concurrency ${CONCURRENCY}`)

  const results: PipeResult[] = folders.map((f) => done.get(f)).filter((r): r is PipeResult => !!r)
  let index = 0

  async function worker() {
    while (index < todo.length) {
      const folder = todo[index++]
      process.stdout.write(`→ ${folder}...\n`)
      try {
        const result = await processPipe(folder)
        results.push(result)
        if (result.status === 'ok') {
          console.log(`  ✓ ${folder}: ${result.assessment!.brand} — ${result.assessment!.estimated_era} (${result.assessment!.confidence}, ${result.seconds}s)`)
        } else {
          console.log(`  ⊘ ${folder}: ${result.error}`)
        }
      } catch (err) {
        results.push({ folder, status: 'error', error: String(err) })
        console.error(`  ✗ ${folder}: ${err}`)
      }
      // Save progress after every pipe so interrupted runs resume cleanly
      writeOutputs([...results].sort((a, b) => a.folder.localeCompare(b.folder)))
    }
  }

  await Promise.all(Array.from({ length: CONCURRENCY }, worker))

  const ok = results.filter((r) => r.status === 'ok').length
  const skipped = results.filter((r) => r.status === 'skipped').length
  const errors = results.filter((r) => r.status === 'error').length
  console.log(`\nDone: ${ok} assessed · ${skipped} skipped (missing photos) · ${errors} errors`)
  console.log(`Results: ${RESULTS_CSV} (open in Excel/Numbers) and ${RESULTS_JSON}`)
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
