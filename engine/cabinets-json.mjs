/**
 * STAGE 1b — THE JSON CABINETS
 *
 * The 55 cabinets Farid built on FaridOS use a different shape from the single
 * YAML dating-directory file: facts live in `channels`, each channel holding a
 * table of readings.
 *
 *   channels.<name>.table[] → { match[], era_start, era_end, confidence, note|label }
 *   channels.line_years.years → { "line name": [start, end] }
 *
 * This reader turns both into the SAME fact shape `subject.mjs` already emits,
 * so every downstream stage — script, panels, assembly, ledger — works on all
 * 55 brands without a single change. One fact shape, two cabinet formats.
 *
 * THE LAW IS UNCHANGED: no source, no episode.
 * A JSON cabinet carries its sources in the channel's `_doc`, or in the
 * cabinet's own `_doc` after the word SOURCES. If neither names one, the fact
 * is refused — exactly as a missing `source:` key is refused in the YAML.
 */
import { readFileSync, readdirSync } from 'node:fs'
import { join } from 'node:path'

export function listCabinets(dir) {
  return readdirSync(dir)
    .filter((f) => f.endsWith('.json'))
    .sort()
}

export function loadJsonCabinet(path) {
  const cab = JSON.parse(readFileSync(path, 'utf8'))
  if (!cab?.brand) throw new Error(`${path}: not a cabinet (no 'brand')`)
  return cab
}

/** Pull the sources clause out of a cabinet's or channel's prose `_doc`. */
function sourceFrom(doc) {
  if (!doc) return null
  // Cabinets phrase it several ways: "SOURCES:", "SOURCES (local-first):",
  // "SOURCE —". Match the label with an optional parenthetical or dash.
  const m = String(doc).match(/SOURCES?\s*(?:\([^)]*\))?\s*[:—-]\s*([^]*)$/i)
  const text = (m ? m[1] : '').replace(/\s+/g, ' ').trim()
  if (!text) return null
  // Keep the first sentence — enough to name the authority.
  return text.split(/(?<=\.)\s(?=[A-Z])/)[0].replace(/\.$/, '').trim() || null
}

/**
 * The professor must never read our filesystem aloud. The full citation stays
 * in the ledger and on screen; the SPOKEN line names the authority only.
 */
function spokenSource(full) {
  if (!full) return null
  let t = String(full)
    .replace(/\b[\w./-]*\.json\b/g, '')            // internal file names
    .replace(/\b(staging|mirror|local-first)\b/gi, '')
    .replace(/\bpipedia mirror\b/gi, 'Pipedia')
    .replace(/\s*[+;]\s*$/, '')
    .replace(/\(\s*\)/g, '')
    .replace(/\s{2,}/g, ' ')
    .replace(/^[\s,:+-]+/, '')
    .trim()
  // Prefer the first named authority inside a parenthetical, e.g. "(Fabio
  // Ferrara study of 2000+ pipes …)" — that is what a collector recognises.
  const named = t.match(/\(([^)]*(?:study|guide|system|chart|article|book|survey|census)[^)]*)\)/i)
  if (named) t = named[1]
  t = t.split(/\s*--\s*|\s*;\s*/)[0].trim()
  if (t.length > 120) t = t.slice(0, 117).replace(/[\s,]+\S*$/, '') + '…'
  return t || null
}

/** A readable era string from a start/end pair, honest about open ends. */
function eraLabel(start, end, maxYear) {
  if (!start && !end) return null
  if (start && end) {
    if (end >= (maxYear || 2026)) return `${start}–present`
    return start === end ? `${start}` : `${start}–${end}`
  }
  return start ? `${start} or later` : `up to ${end}`
}

export function harvestJsonFacts(cab, fileKey) {
  const facts = []
  const refused = []
  const cabinetSource = sourceFrom(cab._doc)

  const push = ({ id, reads, start, end, confidence, caveat, channel, channelSource }) => {
    const era = eraLabel(start, end, cab.max_year)
    if (!era) {
      refused.push({ id, why: 'no era — the read identifies but does not date' })
      return
    }
    const source = channelSource || cabinetSource
    if (!source) {
      refused.push({ id, why: 'NO SOURCE — refused by law' })
      return
    }
    facts.push({
      id,
      cabinet: fileKey,
      sourceFull: source,
      brand: cab.brand,
      drawer: channel,
      drawerLabel: channel.replace(/_/g, ' '),
      small: channel,
      reads,
      era,
      confidence: confidence || 'unstated',
      caveat: caveat || null,
      source: spokenSource(source) || source,
    })
  }

  for (const [channel, ch] of Object.entries(cab.channels || {})) {
    if (!ch || typeof ch !== 'object') continue
    const channelSource = sourceFrom(ch._doc)

    // Shape A — a table of readings.
    for (const [i, e] of (ch.table || []).entries()) {
      const reads = Array.isArray(e.match) ? e.match[0] : e.match || e.series || e.regex
      if (!reads) continue
      push({
        id: `${fileKey}.${channel}.${i}`,
        reads: e.field ? `${String(e.field).replace(/_/g, ' ')}: ${reads}` : reads,
        start: e.era_start,
        end: e.era_end,
        confidence: e.confidence,
        caveat: e.note || e.label || null,
        channel,
        channelSource,
      })
    }

    // Shape B — named lines with a production span.
    for (const [line, span] of Object.entries(ch.years || {})) {
      if (!Array.isArray(span)) continue
      push({
        id: `${fileKey}.${channel}.${line.replace(/\s+/g, '-')}`,
        reads: line,
        start: span[0],
        end: span[1],
        confidence: 'high',
        caveat: ch._doc && !/SOURCES?:/i.test(ch._doc) ? String(ch._doc).split('. ')[0] : null,
        channel,
        channelSource,
      })
    }
  }

  return { facts, refused }
}

/** Harvest every cabinet in a directory. Returns facts from all brands at once. */
export function harvestAll(dir) {
  const all = []
  const refusedAll = []
  const perBrand = []

  for (const file of listCabinets(dir)) {
    const key = file.replace(/\.json$/, '')
    const cab = loadJsonCabinet(join(dir, file))
    const { facts, refused } = harvestJsonFacts(cab, key)
    all.push(...facts)
    refusedAll.push(...refused)
    perBrand.push({ brand: cab.brand, key, facts: facts.length, refused: refused.length })
  }

  return { facts: all, refused: refusedAll, perBrand }
}
