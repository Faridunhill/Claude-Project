/**
 * STAGE 2 — SCRIPT, EVIDENCE FORMAT (no characters, one voice)
 *
 * Farid dropped the face on 2026-08-02. That removed the only blocked stage in
 * the whole engine, so this is now the default format.
 *
 * What changes: there is no professor and no assistant on screen, so there is
 * no dialogue. One narrator carries all seven beats.
 * What does NOT change: the beats themselves, the panel-list contract, and
 * every honesty rule. The "assistant's mistake" simply becomes "what most
 * people will tell you" — the correction still leads, and it still comes from
 * the cabinet's own caveat.
 *
 * The screen shows a real photograph and a text card. Nothing is drawn, so
 * nothing needs to be commissioned, and no fact is ever illustrated by art.
 */

const WORDS_PER_SECOND = 2.5

const secondsFor = (line) =>
  Math.max(2.6, Math.round((line.trim().split(/\s+/).length / WORDS_PER_SECOND) * 10) / 10)

function speakable(value) {
  return String(value)
    .replace(/\s*\([^)]*\)\s*/g, ' ')
    .replace(/["']/g, '')
    .replace(/\s{2,}/g, ' ')
    .trim()
}

export function writeEvidenceEpisode(fact, { photo = null, slug } = {}) {
  const read = describeRead(fact.reads)
  const era = String(fact.era).replace(/\s*—\s*/g, ' — ')
  const naive = naiveReading(fact)

  // Two honest episode shapes, and the data decides which one we get.
  //  · CORRECTION — the cabinet's caveat names a year the era excludes, so a
  //    wrong belief genuinely exists and we correct it.
  //  · OVERLOOKED — no such wrong belief exists. Inventing one would be a straw
  //    man, so the episode becomes "here is a clue most people never check".
  const hasWrongBelief = naive && naive !== stripEra(era)

  const beats = [
    {
      role: 'hook',
      card: { kind: 'mark', text: read.value },
      line: `${fact.brand}. ${read.sentence}`,
    },
    ...(hasWrongBelief
      ? [
          {
            role: 'belief',
            card: { kind: 'wrong', label: 'what you will usually be told', text: naive },
            line: `Ask around, and you will be told ${naive}.`,
          },
          {
            role: 'turn',
            card: { kind: 'plain', text: 'That is the trap.' },
            line: `That is the trap almost everyone falls into.`,
          },
        ]
      : [
          {
            role: 'overlooked',
            card: { kind: 'plain', label: 'the clue most people skip', text: read.value },
            line: `Most collectors never check it. It is one of the quieter clues on the pipe.`,
          },
        ]),
    {
      role: 'correction',
      card: { kind: 'right', label: 'what the evidence supports', text: era },
      line: `${read.subject} points to ${era}. A window, not a birthday.`,
    },
    ...(fact.caveat
      ? [
          {
            role: 'caveat',
            card: { kind: 'warn', label: 'why the obvious answer fails', text: shortCaveat(fact.caveat) },
            line: plainCaveat(fact.caveat),
          },
        ]
      : []),
    {
      role: 'honesty',
      card: { kind: 'note', label: 'our confidence', text: String(fact.confidence) },
      line: honestyLine(fact),
    },
    {
      role: 'source',
      card: { kind: 'citation', label: 'source', text: fact.sourceFull || fact.source },
      line: `This is not opinion. It is ${String(fact.source).replace(/\.$/, '')}.`,
    },
  ]

  const panels = beats.map((b, i) => ({
    panel: i + 1,
    role: b.role,
    speaker: 'narrator',
    // Layer 3 is always the same real photograph — the object we are discussing.
    object: photo
      ? { kind: 'photo', file: photo.file, citation: photo.citation, slug: photo.slug }
      : { kind: 'photo-slot', slot: `${fact.cabinet}-pipe`, status: 'awaiting photograph' },
    card: b.card,
    narration: b.line,
    duration: secondsFor(b.line),
    // Slow push in and out so consecutive panels on one still never feel static.
    motion: i % 2 === 0 ? { zoom: [1.0, 1.08], pan: [0, 0] } : { zoom: [1.08, 1.0], pan: [0, 0] },
  }))

  return {
    format: 'evidence',
    slug: slug || slugify(`${fact.brand}-${fact.small}-${fact.era}`),
    title: `${fact.brand}: what ${read.title} really tells you`,
    brand: fact.brand,
    fact_id: fact.id,
    claim: { reads: fact.reads, era: fact.era, confidence: fact.confidence },
    caveat: fact.caveat || null,
    sources: [fact.sourceFull || fact.source],
    photo: photo || null,
    runtime: Number(panels.reduce((s, p) => s + p.duration, 0).toFixed(1)),
    panels,
  }
}

/**
 * A cabinet read is either a STAMP ("made in eire") or a FEATURE
 * ("bit style: tapered"). They are not spoken the same way, and calling a
 * tapered mouthpiece a "mark" is simply wrong.
 */
function describeRead(reads) {
  const raw = String(reads)
  const m = raw.match(/^([^:]+):\s*(.+)$/)
  if (m) {
    const field = speakable(m[1]).toLowerCase()
    const value = speakable(m[2])
    return {
      value: `${field}: ${value}`,
      title: `a ${value} ${field.replace(/\s*style$/, '')}`.trim(),
      subject: `A ${value} ${field.replace(/\s*style$/, '')}`.trim(),
      sentence: `Look at the ${field.replace(/\s*style$/, '')} — this one is ${value}.`,
    }
  }
  const value = speakable(raw)
  return {
    value,
    title: `"${value.slice(0, 48)}"`,
    subject: value,
    sentence: `The mark reads ${value}.`,
  }
}

const stripEra = (era) => String(era).replace(/[a-z.\s]/gi, '').replace(/^–|–$/g, '')

/**
 * Where a cabinet's caveat names a year the real era excludes, that year is the
 * mistake people actually repeat — so it becomes the belief we correct, rather
 * than a straw man we invent.
 */
function naiveReading(fact) {
  const eraYears = String(fact.era).match(/(1[5-9]\d{2}|20\d{2})/g) || []
  if (fact.caveat) {
    const wrong = (String(fact.caveat).match(/(1[5-9]\d{2}|20\d{2})/g) || [])
      .filter((y) => !eraYears.includes(y))
      .sort()
      .pop()
    if (wrong && eraYears.length) return `${eraYears[0]}–${wrong}`
  }
  if (!eraYears.length) return 'one exact year'
  return eraYears.length > 1 ? `${eraYears[0]}–${eraYears[eraYears.length - 1]}` : eraYears[0]
}

function plainCaveat(caveat) {
  const first = String(caveat).replace(/\s+/g, ' ').split(/(?<=\.)\s/)[0].trim()
  return first.endsWith('.') ? first : `${first}.`
}

function shortCaveat(caveat) {
  const t = plainCaveat(caveat)
  return t.length > 150 ? t.slice(0, 147).replace(/[\s,]+\S*$/, '') + '…' : t
}

function honestyLine(fact) {
  const c = String(fact.confidence).toLowerCase()
  if (c === 'high') return `The evidence is clear, so we will put that in writing.`
  if (c === 'medium') return `Which is why we give a window and not a year. A wide bracket you can trust beats a date you cannot.`
  return `And where the evidence is thin, we write nothing at all. A blank beats a lie.`
}

function slugify(s) {
  return String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 70)
}
