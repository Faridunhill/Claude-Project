/**
 * STAGE 1 — SUBJECT
 *
 * Reads a dating cabinet and harvests every fact that is fit to teach.
 *
 * THE LAW THIS STAGE ENFORCES:
 *   Every claim traces to a cabinet source, or the episode is not made.
 *
 * A fact with no era says nothing. A fact with no source cannot be defended.
 * Both are refused here, loudly, so the refusal is visible in the run log
 * rather than discovered by a collector later.
 */
import { readFileSync } from 'node:fs'
import yaml from 'js-yaml'

export class MissingSource extends Error {}

export function loadCabinet(path) {
  const cab = yaml.load(readFileSync(path, 'utf8'))
  if (!cab?.cabinet) throw new Error(`${path}: not a cabinet (no 'cabinet:' key)`)
  return cab
}

/**
 * Walk drawers → small drawers → reads, and return teachable facts.
 * Returns { facts, refused } — refused is never silent (§ no lying by omission).
 */
export function harvestFacts(cab) {
  const facts = []
  const refused = []
  const cabinetSources = (cab.sources || []).map(sourceLine)

  for (const [drawerKey, drawer] of Object.entries(cab.drawers || {})) {
    const smalls = drawer.small_drawers || { [drawerKey]: drawer }

    for (const [smallKey, small] of Object.entries(smalls)) {
      const reads = small?.reads
      if (!Array.isArray(reads)) continue

      for (const [i, read] of reads.entries()) {
        const id = `${cab.cabinet}.${drawerKey}.${smallKey}.${i}`
        const source = small.source || drawer.source || cabinetSources[0] || null
        const era = read.era || null

        if (!era) {
          refused.push({ id, why: 'no era — the read identifies but does not date' })
          continue
        }
        if (!source) {
          refused.push({ id, why: 'NO SOURCE — refused by law' })
          continue
        }

        facts.push({
          id,
          cabinet: cab.cabinet,
          brand: cab.brand,
          drawer: drawerKey,
          drawerLabel: drawer.label || drawerKey,
          small: smallKey,
          reads: read.value,
          era,
          confidence: read.confidence || 'unstated',
          caveat: read.note || small.note || null,
          source,
          abstain: cab.abstain?.motto || null,
        })
      }
    }
  }
  return { facts, refused }
}

function sourceLine(s) {
  if (typeof s === 'string') return s
  if (!s || typeof s !== 'object') return null
  return [s.title || s.name, s.author, s.year].filter(Boolean).join(', ') || null
}

/**
 * Choose one fact. Deterministic on purpose — same pick argument, same episode,
 * so a run can be repeated and compared. No randomness anywhere in this engine.
 *
 * Preference order: facts that carry a caveat come first. A fact with a caveat
 * is a fact where the obvious reading is WRONG, which is exactly the shape of
 * an assistant's mistake — and exactly what nobody else on the internet says.
 */
export function pickFact(facts, index = 0) {
  if (!facts.length) throw new Error('no teachable facts in this cabinet')
  const withCaveat = facts.filter((f) => f.caveat)
  const pool = withCaveat.length ? withCaveat : facts
  return pool[index % pool.length]
}
