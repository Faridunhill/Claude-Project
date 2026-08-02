/**
 * STAGE 2 — SCRIPT
 *
 * A cabinet fact becomes an episode: the Assistant makes the mistake the fact
 * warns about, the Professor corrects her, and he names his source at the end.
 *
 * This stage is deliberately a TEMPLATE, not a language model. Two reasons:
 *   1. It runs offline, free, and identically every time, so the rest of the
 *      engine can be tested without an API key or a bill.
 *   2. It proves the contract. Whatever writes the script later — Claude, in
 *      stage 2b — must emit exactly this shape, and everything downstream is
 *      already built against it.
 *
 * The narration never states a fact the cabinet did not carry. The caveat is
 * not decoration: it IS the episode.
 */

const WORDS_PER_SECOND = 2.5 // ~150 wpm, an unhurried presenter

const secondsFor = (line) =>
  Math.max(2.4, Math.round((line.trim().split(/\s+/).length / WORDS_PER_SECOND) * 10) / 10)

/** Strip a cabinet's shorthand into something a person would say aloud. */
function speakable(value) {
  return String(value)
    .replace(/\s*\([^)]*\)\s*/g, ' ')
    .replace(/["']/g, '')
    .replace(/\s{2,}/g, ' ')
    .trim()
}

export function writeEpisode(fact, { slug } = {}) {
  const mark = speakable(fact.reads)
  const era = String(fact.era).replace(/\s*—\s*/g, ' — ')
  const naive = naiveReading(fact)

  const beats = [
    {
      role: 'hook',
      speaker: 'assistant',
      background: 'bg-bench-a',
      characters: ['assistant-holding-pipe-3q'],
      object: { slot: 'stamp-macro', hint: 'macro photograph of the stamp being read' },
      overlays: [{ type: 'label', text: mark }],
      line: `Look — it says ${mark}. So that tells us exactly when it was made, doesn't it?`,
    },
    {
      role: 'mistake',
      speaker: 'assistant',
      background: 'bg-bench-a',
      characters: ['assistant-confident-front', 'prof-listening-3q'],
      object: null,
      overlays: [{ type: 'label', text: naive, tone: 'wrong' }],
      line: naiveLine(fact, naive),
    },
    {
      role: 'turn',
      speaker: 'professor',
      background: 'bg-bench-a',
      characters: ['prof-explaining-3q', 'assistant-listening-front'],
      object: null,
      overlays: [],
      line: `Nearly. And that is the trap almost everyone falls into.`,
    },
    {
      role: 'correction',
      speaker: 'professor',
      background: 'bg-bench-a',
      characters: ['prof-explaining-front'],
      object: { slot: 'stamp-macro', hint: 'the same stamp, larger' },
      overlays: [{ type: 'label', text: era, tone: 'right' }],
      line: `${mark} points to ${era}. That is the bracket — a window, not a birthday.`,
    },
    ...(fact.caveat
      ? [
          {
            role: 'caveat',
            speaker: 'professor',
            background: 'bg-shelf',
            characters: ['prof-stern-3q'],
            object: null,
            overlays: [{ type: 'label', text: 'why the obvious answer fails', tone: 'warn' }],
            line: plainCaveat(fact.caveat),
          },
        ]
      : []),
    {
      role: 'honesty',
      speaker: 'professor',
      background: 'bg-bench-a',
      characters: ['prof-warm-front', 'assistant-thinking-3q'],
      object: null,
      overlays: [{ type: 'label', text: `confidence: ${fact.confidence}`, tone: 'note' }],
      line: honestyLine(fact),
    },
    {
      role: 'source',
      speaker: 'professor',
      background: 'bg-shelf',
      characters: ['prof-closing-book-3q'],
      object: { slot: 'source-page', hint: 'the reference itself, on the shelf' },
      overlays: [{ type: 'citation', text: fact.sourceFull || fact.source }],
      line: `And that is not my opinion. It is ${String(fact.source).replace(/\.$/, '')}.`,
    },
  ]

  const panels = beats.map((b, i) => ({
    panel: i + 1,
    role: b.role,
    speaker: b.speaker,
    background: b.background,
    characters: b.characters,
    object: b.object,
    overlays: b.overlays,
    narration: b.line,
    duration: secondsFor(b.line),
    motion: i % 2 === 0 ? { zoom: [1.0, 1.06] } : { zoom: [1.05, 1.0] },
  }))

  return {
    slug: slug || slugify(`${fact.brand}-${fact.small}-${fact.era}`),
    title: episodeTitle(fact),
    brand: fact.brand,
    fact_id: fact.id,
    claim: { reads: fact.reads, era: fact.era, confidence: fact.confidence },
    caveat: fact.caveat || null,
    sources: [fact.sourceFull || fact.source],
    runtime: Number(panels.reduce((s, p) => s + p.duration, 0).toFixed(1)),
    panels,
  }
}

/**
 * What the assistant gets wrong.
 *
 * A cabinet caveat usually exists because a WRONG date is widely repeated —
 * "NOT used all the way to 1949". Where the caveat names a year the real era
 * does not contain, that year IS the popular mistake, so we put the popular
 * mistake in her mouth rather than inventing one. This is the difference
 * between an episode that corrects the internet and an episode that argues
 * with a straw man.
 */
function naiveReading(fact) {
  const eraYears = String(fact.era).match(/(1[5-9]\d{2}|20\d{2})/g) || []
  if (fact.caveat) {
    const caveatYears = (String(fact.caveat).match(/(1[5-9]\d{2}|20\d{2})/g) || []).filter(
      (y) => !eraYears.includes(y)
    )
    const wrong = caveatYears.sort().pop()
    if (wrong && eraYears.length) return `${eraYears[0]}–${wrong}, exactly`
  }
  if (!eraYears.length) return 'a single year'
  return eraYears.length > 1
    ? `${eraYears[0]}–${eraYears[eraYears.length - 1]}, exactly`
    : `${eraYears[0]}, exactly`
}

function naiveLine(fact, naive) {
  return `${naive}. The book says so, and the stamp is right there in front of me.`
}

/** Say the cabinet's caveat the way a person says it, without adding to it. */
function plainCaveat(caveat) {
  const first = String(caveat).replace(/\s+/g, ' ').split(/(?<=\.)\s/)[0].trim()
  return first.endsWith('.') ? first : `${first}.`
}

function honestyLine(fact) {
  const c = String(fact.confidence).toLowerCase()
  if (c === 'high') return `I would put that in writing. When the marks are this clear, we say so.`
  if (c === 'medium')
    return `Which is why we give you a window and not a year. A wide bracket you can trust beats a date you cannot.`
  return `And where the evidence is thin, we write nothing at all. A blank beats a lie.`
}

function episodeTitle(fact) {
  return `${fact.brand}: what "${speakable(fact.reads).slice(0, 48)}" really tells you`
}

function slugify(s) {
  return String(s)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 70)
}
