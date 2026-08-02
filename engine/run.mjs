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
import { mkdirSync, existsSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { loadCabinet, harvestFacts, pickFact } from './subject.mjs'
import { harvestJsonFacts, loadJsonCabinet, harvestAll } from './cabinets-json.mjs'
import { writeEpisode } from './script.mjs'
import { loadLibrary, resolvePanels } from './panels.mjs'
import { writeStoryboard, writeLedger } from './assemble.mjs'
import { writeEvidenceEpisode } from './script-evidence.mjs'
import { writeEvidenceStoryboard } from './assemble-evidence.mjs'
import { buildPhotoIndex, photoForBrand } from './photos.mjs'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const arg = (k, d) => {
  const i = process.argv.indexOf(`--${k}`)
  return i > -1 && process.argv[i + 1] ? process.argv[i + 1] : d
}

const cabinetName = arg('cabinet', 'peterson')
const pick = Number(arg('pick', '0'))
const outRoot = join(ROOT, arg('out', 'engine/out'))
const builtAt = arg('at', '2026-07-31')   // passed in, never Date.now() — runs must be reproducible

// ── SURVEY MODE — read every cabinet, build nothing ─────────────────────────
if (process.argv.includes('--survey')) {
  const r = harvestAll(join(ROOT, 'dating/cabinets'))
  const noSource = r.refused.filter((x) => x.why.includes('NO SOURCE')).length
  console.log(`\n  CABINET SURVEY — ${r.perBrand.length} brands\n`)
  console.log(`  teachable facts   ${r.facts.length}`)
  console.log(`  with a caveat     ${r.facts.filter((f) => f.caveat).length}   (the strongest episodes)`)
  console.log(`  refused, no era   ${r.refused.length - noSource}`)
  console.log(`  refused, NO SOURCE ${noSource}\n`)
  const blocked = r.perBrand.filter((b) => b.facts === 0)
  if (blocked.length) {
    console.log(`  BLOCKED — these cabinets name no source the engine can read.`)
    console.log(`  One line, "SOURCES: <authority>", in each _doc unblocks them:`)
    for (const b of blocked) console.log(`    · ${b.brand}  (${b.key}.json)`)
    console.log()
  }
  console.log('  Top brands by teachable facts:')
  for (const b of r.perBrand.sort((a, b) => b.facts - a.facts).slice(0, 10))
    console.log(`    ${String(b.facts).padStart(4)}  ${b.brand}`)
  console.log()
  process.exit(0)
}

console.log(`\n  THE EPISODE ENGINE — cabinet: ${cabinetName}\n`)

// ── 1. SUBJECT ──────────────────────────────────────────────────────────────
// Two cabinet formats, one fact shape. JSON is the FaridOS engine format (55
// brands); YAML is the dating-directory format (Peterson only, richer drawers).
const jsonPath = join(ROOT, 'dating/cabinets', `${cabinetName}.json`)
const yamlPath = join(ROOT, 'dating/cabinets', `${cabinetName}.yaml`)
const useJson = existsSync(jsonPath)
const cab = useJson ? loadJsonCabinet(jsonPath) : loadCabinet(yamlPath)
const { facts, refused } = useJson ? harvestJsonFacts(cab, cabinetName) : harvestFacts(cab)
console.log(`  1 SUBJECT   ${facts.length} teachable facts · ${refused.length} refused`)
for (const r of refused.filter((r) => r.why.includes('NO SOURCE')))
  console.log(`              REFUSED ${r.id} — ${r.why}`)
const fact = pickFact(facts, pick)
console.log(`              picked ${fact.id}`)
console.log(`              "${String(fact.reads).slice(0, 68)}" → ${fact.era}`)

// EVIDENCE is the default format since 2026-08-02: no characters, no drawings,
// nothing to commission. Pass --format characters for the illustrated version.
const format = arg('format', 'evidence')

let episode, outDir, resolved

if (format === 'evidence') {
  // ── 2. SCRIPT ─────────────────────────────────────────────────────────────
  const index = buildPhotoIndex(join(ROOT, 'content/products'))
  const photo = photoForBrand(index, fact.brand)
  episode = writeEvidenceEpisode(fact, { photo })
  console.log(`  2 SCRIPT    ${episode.panels.length} panels · ${episode.runtime}s · one narrator`)

  // ── 3. PICTURE ────────────────────────────────────────────────────────────
  outDir = join(outRoot, episode.slug)
  mkdirSync(outDir, { recursive: true })
  console.log(
    photo
      ? `  3 PICTURE   real photograph · ${photo.slug}`
      : `  3 PICTURE   no ${fact.brand} photograph in the catalogue yet — slot left open`
  )

  // ── 4. VOICE ──────────────────────────────────────────────────────────────
  console.log(`  4 VOICE     narration written — awaiting an ElevenLabs voice id`)

  // ── 5. ASSEMBLE ───────────────────────────────────────────────────────────
  writeEvidenceStoryboard(episode, { outDir })
  console.log(`  5 ASSEMBLE  storyboard.html — the finished format, minus the voice`)

  resolved = { panels: episode.panels, missing: photo ? [] : [`photo:${fact.cabinet}`] }
} else {
  // ── 2. SCRIPT ─────────────────────────────────────────────────────────────
  episode = writeEpisode(fact)
  console.log(`  2 SCRIPT    ${episode.panels.length} panels · ${episode.runtime}s · ${episode.slug}`)

  // ── 3. PANELS ─────────────────────────────────────────────────────────────
  outDir = join(outRoot, episode.slug)
  mkdirSync(outDir, { recursive: true })
  const library = loadLibrary(join(ROOT, 'engine/assets/library.json'))
  resolved = resolvePanels(episode, library, { outDir })
  console.log(`  3 PANELS    ${resolved.panels.length} rendered · ${resolved.missing.length} asset ids unfilled`)

  // ── 4. VOICE ──────────────────────────────────────────────────────────────
  console.log(`  4 VOICE     skipped — narration written, awaiting the ElevenLabs step`)

  // ── 5. ASSEMBLE ───────────────────────────────────────────────────────────
  writeStoryboard(episode, resolved, { outDir, missing: resolved.missing })
  console.log(`  5 ASSEMBLE  storyboard.html (plays on its narration timings)`)
}

// ── 7. LEDGER ───────────────────────────────────────────────────────────────
writeLedger(episode, resolved, { outDir, missing: resolved.missing, refused, builtAt })
console.log(`  7 LEDGER    episode.json + ledger.json`)

console.log(`\n  → ${join(outDir, 'storyboard.html')}\n`)
