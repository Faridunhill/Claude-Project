#!/usr/bin/env node
/**
 * THE EPISODE ENGINE — run one episode end to end.
 *
 *   node engine/run.mjs --cabinet peterson [--pick 0] [--out engine/out]
 *
 * Stages: 1 subject → 2 script → 3 panels → 5 assemble → 7 ledger.
 * Stage 4 (voice) and the finished render are the only pieces still outside
 * this file; both consume the panel list it writes, unchanged.
 */
import { mkdirSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { loadCabinet, harvestFacts, pickFact } from './subject.mjs'
import { writeEpisode } from './script.mjs'
import { loadLibrary, resolvePanels } from './panels.mjs'
import { writeStoryboard, writeLedger } from './assemble.mjs'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const arg = (k, d) => {
  const i = process.argv.indexOf(`--${k}`)
  return i > -1 && process.argv[i + 1] ? process.argv[i + 1] : d
}

const cabinetName = arg('cabinet', 'peterson')
const pick = Number(arg('pick', '0'))
const outRoot = join(ROOT, arg('out', 'engine/out'))
const builtAt = arg('at', '2026-07-31')   // passed in, never Date.now() — runs must be reproducible

console.log(`\n  THE EPISODE ENGINE — cabinet: ${cabinetName}\n`)

// ── 1. SUBJECT ──────────────────────────────────────────────────────────────
const cab = loadCabinet(join(ROOT, 'dating/cabinets', `${cabinetName}.yaml`))
const { facts, refused } = harvestFacts(cab)
console.log(`  1 SUBJECT   ${facts.length} teachable facts · ${refused.length} refused`)
for (const r of refused.filter((r) => r.why.includes('NO SOURCE')))
  console.log(`              REFUSED ${r.id} — ${r.why}`)
const fact = pickFact(facts, pick)
console.log(`              picked ${fact.id}`)
console.log(`              "${String(fact.reads).slice(0, 68)}" → ${fact.era}`)

// ── 2. SCRIPT ───────────────────────────────────────────────────────────────
const episode = writeEpisode(fact)
console.log(`  2 SCRIPT    ${episode.panels.length} panels · ${episode.runtime}s · ${episode.slug}`)

// ── 3. PANELS ───────────────────────────────────────────────────────────────
const outDir = join(outRoot, episode.slug)
mkdirSync(outDir, { recursive: true })
const library = loadLibrary(join(ROOT, 'engine/assets/library.json'))
const resolved = resolvePanels(episode, library, { outDir })
console.log(`  3 PANELS    ${resolved.panels.length} rendered · ${resolved.missing.length} asset ids unfilled`)

// ── 4. VOICE ────────────────────────────────────────────────────────────────
console.log(`  4 VOICE     skipped — narration written, awaiting the ElevenLabs step`)

// ── 5. ASSEMBLE ─────────────────────────────────────────────────────────────
writeStoryboard(episode, resolved, { outDir, missing: resolved.missing })
console.log(`  5 ASSEMBLE  storyboard.html (plays on its narration timings)`)

// ── 7. LEDGER ───────────────────────────────────────────────────────────────
writeLedger(episode, resolved, { outDir, missing: resolved.missing, refused, builtAt })
console.log(`  7 LEDGER    episode.json + ledger.json`)

console.log(`\n  → ${join(outDir, 'storyboard.html')}\n`)
