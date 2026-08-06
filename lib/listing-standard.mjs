/**
 * THE FARIDUNHILL LISTING STANDARD — machine-readable spec + auditor.
 *
 * One source of truth for: the public standard page, the CMS validation, the
 * audit script, and any renderer that pushes the same record to a second or
 * third channel. Prose lives in docs/IDEA_A5_THE_STANDARD.md — if the two ever
 * disagree, this file is the one that runs, and the doc is the bug.
 *
 * STATUS: DRAFT v0.1. Not authorised for launch. Farid's gate.
 */

export const STANDARD_VERSION = '0.1-draft'
export const STANDARD_DATE = '2026-08-06'

/* ────────────────────────────────────────────────────────────────────────────
   1. CONDITION — the ladder
   Grades are defined by what is observable, not by how the pipe feels. Each
   grade lists the criteria a piece must satisfy; a piece that fails one drops
   to the next rung. RESTORATION is the seventh rung the six-grade ladder
   lacks: without it, "Fair" quietly absorbs cracked and burned-out pipes,
   which is where the category's dishonesty lives.
   ──────────────────────────────────────────────────────────────────────────── */

export const CONDITION_GRADES = [
  {
    code: 'NEW',
    label: 'New / NOS',
    rank: 7,
    short: 'Never smoked, never owned.',
    criteria: [
      'Never lit. No carbon, no ash residue, no rim heat marks.',
      'Chamber raw briar or factory pre-carbon, untouched.',
      'Stem free of tooth contact of any kind.',
      'Stamps as struck.',
      'Factory sock, box or papers noted if present — never implied.',
    ],
  },
  {
    code: 'MINT',
    label: 'Mint',
    rank: 6,
    short: 'Smoked a handful of times; indistinguishable from new to the eye.',
    criteria: [
      'Light carbon only, or chamber cleaned back to briar with no reaming marks.',
      'Rim clean — no darkening, no charring, no dents.',
      'No tooth chatter and no tooth dents under raking light.',
      'No oxidation on the stem.',
      'Stamps crisp and fully legible.',
    ],
  },
  {
    code: 'EXCELLENT',
    label: 'Excellent',
    rank: 5,
    short: 'Lightly smoked, properly cleaned, nothing to apologise for.',
    criteria: [
      'Chamber clean, round, no reaming damage, no heel cake.',
      'Rim clean or lightly darkened only — no charring, no dents.',
      'Briar free of dents; fills, if any, tight and flush.',
      'Stem de-oxidised; light chatter permitted, no dents.',
      'Stamps crisp.',
    ],
  },
  {
    code: 'VERY_GOOD',
    label: 'Very Good',
    rank: 4,
    short: 'Honestly used, restored well.',
    criteria: [
      'Chamber sound, cake removed, no burnout and no soft spots.',
      'Minor rim darkening or a light rim mark permitted.',
      'Small handling marks in the briar permitted.',
      'Stem chatter removed or light; no dents deeper than surface.',
      'Stamps fully readable.',
    ],
  },
  {
    code: 'GOOD',
    label: 'Good',
    rank: 3,
    short: 'Used, and it shows — everything visible is disclosed.',
    criteria: [
      'Chamber sound but with wear; no burnout.',
      'Rim wear, darkening or a small dent, photographed.',
      'Visible fills, handling marks or a small dent in the briar.',
      'Tooth dents present in the stem, photographed.',
      'Stamps soft but legible.',
    ],
  },
  {
    code: 'FAIR',
    label: 'Fair',
    rank: 2,
    short: 'Marked, smokable, and priced as what it is.',
    criteria: [
      'Chamber usable; out-of-round or over-reamed permitted and stated.',
      'Significant rim damage or charring, photographed.',
      'Deep tooth dents or button wear, photographed.',
      'Stamps faint.',
      'No crack, no burnout, no bite-through — those are RESTORATION.',
    ],
  },
  {
    code: 'RESTORATION',
    label: 'Restoration piece',
    rank: 1,
    short: 'Not smokable as it stands. Sold to be worked on.',
    criteria: [
      'Any of: shank or bowl crack, burnout or soft spot, bite-through, ' +
        'missing or wrong stem, rim burned past repair.',
      'The defect is named in words and shown in a photograph.',
      'Never listed as smokable and never priced as a smoker.',
    ],
  },
]

export const GRADE_CODES = CONDITION_GRADES.map((g) => g.code)
const GRADE_BY_CODE = Object.fromEntries(CONDITION_GRADES.map((g) => [g.code, g]))

/**
 * The four graded components. A pipe is not one object — it is four, and the
 * common lie in this trade is a chewed stem hidden under "excellent overall".
 * Stamps are graded because in this category the stamp is a large part of the
 * value, and nobody else grades it.
 */
export const COMPONENTS = [
  { key: 'briar', label: 'Bowl / briar', watches: 'fills, dents, cracks, scorch, finish wear' },
  { key: 'rim', label: 'Rim', watches: 'charring, darkening, dents, reaming damage' },
  { key: 'stem', label: 'Stem', watches: 'oxidation, chatter, tooth dents, button wear, bite-through' },
  { key: 'stamps', label: 'Stamps', watches: 'crisp / soft / faint / obliterated' },
]

/** Flags that are declared separately and are NEVER folded into a grade. */
export const DECLARATIONS = [
  { key: 'smoked', label: 'Smoked / unsmoked', values: ['UNSMOKED', 'LIGHTLY_SMOKED', 'SMOKED', 'UNKNOWN'] },
  { key: 'sanitised', label: 'Sanitised', values: ['YES_METHOD_STATED', 'NO', 'UNKNOWN'] },
  { key: 'refurbished', label: 'Refurbished', values: ['NONE', 'CLEANED', 'REFINISHED', 'UNKNOWN'] },
  { key: 'repaired', label: 'Repaired', values: ['NONE', 'RESTEMMED', 'BANDED', 'CRACK_PINNED', 'OTHER', 'UNKNOWN'] },
]

/**
 * THE LOWEST-COMPONENT RULE.
 * The headline grade is the lowest of the four component grades. It is not an
 * average and it is not the seller's overall impression. One rule, and the
 * single most common dishonesty in estate pipe selling stops working.
 */
export function headlineGrade(components) {
  const ranks = COMPONENTS.map((c) => GRADE_BY_CODE[components?.[c.key]]?.rank).filter(
    (r) => typeof r === 'number'
  )
  if (ranks.length !== COMPONENTS.length) return null
  const low = Math.min(...ranks)
  return CONDITION_GRADES.find((g) => g.rank === low)?.code ?? null
}

/* ────────────────────────────────────────────────────────────────────────────
   2. MEASUREMENT — the six numbers, plus the fittings
   Measured, never estimated from a photograph. Metric primary. A measurement
   that was not taken is recorded as not measured; it is never simply absent.
   ──────────────────────────────────────────────────────────────────────────── */

export const MEASUREMENTS = [
  { key: 'lengthMm', label: 'Length', unit: 'mm', required: true },
  { key: 'heightMm', label: 'Height', unit: 'mm', required: true },
  { key: 'bowlOuterMm', label: 'Bowl outside diameter', unit: 'mm', required: true },
  { key: 'chamberDiameterMm', label: 'Chamber diameter', unit: 'mm', required: true },
  { key: 'chamberDepthMm', label: 'Chamber depth', unit: 'mm', required: true },
  { key: 'weightG', label: 'Weight', unit: 'g', required: true },
]

export const FITTINGS = [
  { key: 'filter', label: 'Filter', values: ['NONE', '9MM', '6MM', 'ADAPTER', 'OTHER'] },
  { key: 'stemMaterial', label: 'Stem material', values: ['VULCANITE', 'ACRYLIC', 'AMBER', 'HORN', 'BAKELITE', 'OTHER'] },
  { key: 'mount', label: 'Mount / band', values: ['NONE', 'SILVER', 'GOLD', 'NICKEL', 'BRASS', 'OTHER'] },
]

/* ────────────────────────────────────────────────────────────────────────────
   3. PHOTOGRAPHY — the pose sequence
   Eight is the floor, and it is the standing museum law restated: six poses
   plus two stamp close-ups. Fixed roles, fixed order, never reordered
   silently. A declared flaw must carry its own photograph.
   ──────────────────────────────────────────────────────────────────────────── */

export const PHOTO_ROLES = [
  { n: 1, key: 'left', label: 'Left profile', required: true, note: 'Whole pipe, stem to the right.' },
  { n: 2, key: 'right', label: 'Right profile', required: true, note: 'Whole pipe, stem to the left.' },
  { n: 3, key: 'rim', label: 'Rim & chamber from above', required: true, note: 'The shot sellers hide.' },
  { n: 4, key: 'underside', label: 'Underside / shank', required: true, note: 'Shows fills and repairs.' },
  { n: 5, key: 'stem', label: 'Stem & button, both faces', required: true, note: 'Tooth surface visible.' },
  { n: 6, key: 'grain', label: 'Three-quarter / grain', required: true, note: 'How the pipe actually reads.' },
  { n: 7, key: 'stampA', label: 'Stamp close-up A', required: true, note: 'Nomenclature, legible at 100%.' },
  { n: 8, key: 'stampB', label: 'Stamp close-up B', required: true, note: 'Reverse shank / model / country / date code.' },
  { n: 9, key: 'defect', label: 'Defect close-up', required: false, note: 'Mandatory if any component grades below VERY_GOOD.' },
  { n: 10, key: 'extras', label: 'Box, sock, papers or scale', required: false, note: 'Only if they ship with the pipe.' },
]

export const PHOTO_MIN = 8
export const PHOTO_MAX = 10

export const PHOTO_RULES = [
  'The photographs are of the exact item that ships. No stock images, ever.',
  'One light setup, one neutral ground, across the whole sequence.',
  'No filter, no colour grade, no shadow used to hide a mark.',
  'The order is the sequence above. Poses are never dropped or reordered silently.',
]

/* ────────────────────────────────────────────────────────────────────────────
   4. ATTRIBUTION — and the honest escape hatch
   The requirement is not that every pipe carries a famous name. It is that
   the field is ANSWERED. UNMARKED and UNATTRIBUTED are valid answers; a
   title stuffed with four brand names is not.
   ──────────────────────────────────────────────────────────────────────────── */

export const ATTRIBUTION_FIELDS = [
  { key: 'brand', label: 'Brand', required: true, note: 'A maker, or UNMARKED, or UNATTRIBUTED. Never blank, never a guess.' },
  { key: 'model', label: 'Model / shape number', required: true, note: 'As stamped, or UNSTAMPED.' },
  { key: 'countryStamped', label: 'Country as stamped', required: true, note: 'What the pipe says, not what you believe.' },
  { key: 'stampTranscription', label: 'Stamp transcription', required: true, note: 'Literal, line by line, including what makes no sense.' },
  { key: 'dateBracket', label: 'Date bracket', required: true, note: 'From the dating engine. UNDATED is an honest answer; a single year needs a cliff.' },
  { key: 'attributionEvidence', label: 'Evidence', required: true, note: 'Which stamp, which rule. Fact and judgment kept visibly apart.' },
]

export const UNATTRIBUTED_VALUES = ['UNMARKED', 'UNATTRIBUTED', 'UNSTAMPED', 'UNDATED']

/* ────────────────────────────────────────────────────────────────────────────
   5. THE DESCRIPTION IS DERIVED
   The fact block is generated from the record. Nobody types it, so nobody can
   contradict the fields in it, and the same record renders to every channel
   without being retyped. Opinion is welcome — below the line, and signed.
   ──────────────────────────────────────────────────────────────────────────── */

export const BANNED_IN_FACT_BLOCK = [
  'rare', 'stunning', 'gorgeous', 'beautiful', 'must-have', 'investment',
  'grail', 'unicorn', 'incredible', 'amazing', 'perfect', 'flawless',
]

export function renderFactBlock(r) {
  const g = headlineGrade(r.components)
  const lines = []
  const maker = r.brand && !UNATTRIBUTED_VALUES.includes(r.brand) ? r.brand : 'Unattributed'
  const model = r.model && r.model !== 'UNSTAMPED' ? ` ${r.model}` : ''
  lines.push(`${maker}${model}${r.shape ? `, ${r.shape}` : ''}${r.countryStamped ? `, stamped ${r.countryStamped}` : ''}.`)
  if (r.dateBracket) lines.push(`Dating: ${r.dateBracket}${r.attributionEvidence ? ` — ${r.attributionEvidence}` : ''}.`)
  if (r.stampTranscription) lines.push(`Stamps read: ${r.stampTranscription}`)
  const dims = MEASUREMENTS.filter((m) => r[m.key] != null).map((m) => `${m.label} ${r[m.key]}${m.unit}`)
  if (dims.length) lines.push(`${dims.join(' · ')}.`)
  const fit = FITTINGS.filter((f) => r[f.key]).map((f) => `${f.label}: ${r[f.key]}`)
  if (fit.length) lines.push(`${fit.join(' · ')}.`)
  if (g) {
    const parts = COMPONENTS.map((c) => `${c.label} ${GRADE_BY_CODE[r.components[c.key]]?.label ?? '—'}`)
    lines.push(`Condition ${GRADE_BY_CODE[g]?.label ?? g} — the lowest of: ${parts.join(', ')}.`)
  }
  const decl = DECLARATIONS.filter((d) => r[d.key]).map((d) => `${d.label}: ${r[d.key]}`)
  if (decl.length) lines.push(`${decl.join(' · ')}.`)
  return lines.join('\n')
}

/* ────────────────────────────────────────────────────────────────────────────
   6. THE AUDIT
   Every rule is worth points and some are blocking. A listing that fails a
   blocking rule does not publish. The score is shown on the listing — ours
   included, and ours especially.
   ──────────────────────────────────────────────────────────────────────────── */

const has = (v) => v != null && String(v).trim() !== ''
const num = (v) => typeof v === 'number' || (has(v) && !Number.isNaN(Number(v)))

export const RULES = [
  // ATTRIBUTION
  { id: 'A1', section: 'Attribution', weight: 10, blocking: true, label: 'Brand answered (a maker, or UNMARKED/UNATTRIBUTED)', test: (r) => has(r.brand) },
  { id: 'A2', section: 'Attribution', weight: 4, blocking: false, label: 'Model or shape number, as stamped or UNSTAMPED', test: (r) => has(r.model) },
  { id: 'A3', section: 'Attribution', weight: 4, blocking: false, label: 'Country as stamped', test: (r) => has(r.countryStamped) },
  { id: 'A4', section: 'Attribution', weight: 8, blocking: false, label: 'Stamps transcribed literally', test: (r) => has(r.stampTranscription) },
  { id: 'A5', section: 'Attribution', weight: 6, blocking: false, label: 'Date bracket present (UNDATED counts)', test: (r) => has(r.dateBracket) },
  { id: 'A6', section: 'Attribution', weight: 4, blocking: false, label: 'Attribution evidence given', test: (r) => has(r.attributionEvidence) },

  // CONDITION
  { id: 'C1', section: 'Condition', weight: 10, blocking: true, label: 'All four components graded', test: (r) => COMPONENTS.every((c) => GRADE_CODES.includes(r.components?.[c.key])) },
  { id: 'C2', section: 'Condition', weight: 6, blocking: true, label: 'Headline grade equals the lowest component', test: (r) => { const g = headlineGrade(r.components); return g != null && (!has(r.conditionGrade) || r.conditionGrade === g) } },
  { id: 'C3', section: 'Condition', weight: 4, blocking: false, label: 'Smoked / sanitised / refurbished / repaired declared', test: (r) => DECLARATIONS.every((d) => has(r[d.key])) },

  // MEASUREMENT
  { id: 'M1', section: 'Measurement', weight: 8, blocking: true, label: 'Length, height, bowl diameter, weight', test: (r) => ['lengthMm', 'heightMm', 'bowlOuterMm', 'weightG'].every((k) => num(r[k])) },
  { id: 'M2', section: 'Measurement', weight: 8, blocking: false, label: 'Chamber diameter and depth — the two nobody publishes', test: (r) => num(r.chamberDiameterMm) && num(r.chamberDepthMm) },
  { id: 'M3', section: 'Measurement', weight: 4, blocking: false, label: 'Filter, stem material and mount stated', test: (r) => FITTINGS.every((f) => has(r[f.key])) },

  // PHOTOGRAPHY
  { id: 'P1', section: 'Photography', weight: 12, blocking: true, label: `At least ${PHOTO_MIN} photographs`, test: (r) => (r.images?.length ?? 0) >= PHOTO_MIN },
  { id: 'P2', section: 'Photography', weight: 6, blocking: false, label: `No more than ${PHOTO_MAX} photographs`, test: (r) => (r.images?.length ?? 0) <= PHOTO_MAX },
  { id: 'P3', section: 'Photography', weight: 6, blocking: false, label: 'Every required pose role filled, in order', test: (r) => PHOTO_ROLES.filter((p) => p.required).every((p) => has(r.photoRoles?.[p.key])) },
  { id: 'P4', section: 'Photography', weight: 6, blocking: true, label: 'A component below VERY_GOOD carries a defect photograph', test: (r) => { const low = COMPONENTS.some((c) => (GRADE_BY_CODE[r.components?.[c.key]]?.rank ?? 9) < 4); return !low || has(r.photoRoles?.defect) } },

  // DESCRIPTION
  { id: 'D1', section: 'Description', weight: 8, blocking: true, label: 'Fact block generated from the record, not typed', test: (r) => r.descriptionSource === 'generated' },
  { id: 'D2', section: 'Description', weight: 4, blocking: false, label: 'No marketing adjective inside the fact block', test: (r) => { const t = String(r.description ?? '').toLowerCase(); return !BANNED_IN_FACT_BLOCK.some((w) => t.includes(w)) } },
  { id: 'D3', section: 'Description', weight: 4, blocking: false, label: 'Opinion, if any, is separated and signed', test: (r) => !has(r.note) || has(r.noteAuthor) },

  // PROVENANCE
  { id: 'V1', section: 'Provenance', weight: 4, blocking: false, label: 'Source class stated (estate lot / single owner / trade / new stock)', test: (r) => has(r.sourceClass) },
  { id: 'V2', section: 'Provenance', weight: 4, blocking: false, label: 'Work done in our hands is listed', test: (r) => has(r.workDone) },
]

export const MAX_SCORE = RULES.reduce((s, r) => s + r.weight, 0)
/** Below this, a listing is not publishable even with no blocking failure. */
export const PUBLISH_THRESHOLD = 80

export function auditListing(record) {
  const r = record ?? {}
  const results = RULES.map((rule) => {
    let pass = false
    try {
      pass = Boolean(rule.test(r))
    } catch {
      pass = false
    }
    return { id: rule.id, section: rule.section, label: rule.label, weight: rule.weight, blocking: rule.blocking, pass }
  })
  const earned = results.filter((x) => x.pass).reduce((s, x) => s + x.weight, 0)
  const blocked = results.filter((x) => !x.pass && x.blocking)
  const score = Math.round((earned / MAX_SCORE) * 100)
  return {
    score,
    earned,
    max: MAX_SCORE,
    results,
    failed: results.filter((x) => !x.pass),
    blocking: blocked,
    publishable: blocked.length === 0 && score >= PUBLISH_THRESHOLD,
  }
}

/** Section totals, for the standard page and the audit report. */
export const SECTIONS = [...new Set(RULES.map((r) => r.section))].map((name) => ({
  name,
  weight: RULES.filter((r) => r.section === name).reduce((s, r) => s + r.weight, 0),
  rules: RULES.filter((r) => r.section === name).map(({ id, label, weight, blocking }) => ({ id, label, weight, blocking })),
}))
