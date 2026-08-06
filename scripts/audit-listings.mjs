#!/usr/bin/env node
/**
 * Audit every listing in content/products against the Faridunhill Listing
 * Standard and write a report. We publish our own score before we ask anyone
 * else to keep one.
 *
 *   node scripts/audit-listings.mjs                  # print the scoreboard
 *   node scripts/audit-listings.mjs --write docs/LISTING_AUDIT.md
 *
 * The YAML reader below handles the flat scalar/list shape these files use.
 * It is deliberately dependency-free so the audit runs on any machine, on
 * either front, without an install step.
 */

import { readFileSync, readdirSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import {
  auditListing, RULES, SECTIONS, MAX_SCORE, PUBLISH_THRESHOLD,
  STANDARD_VERSION, PHOTO_MIN,
} from '../lib/listing-standard.mjs'

const DIR = join(process.cwd(), 'content', 'products')

function unquote(s) {
  const t = s.trim()
  if ((t.startsWith("'") && t.endsWith("'")) || (t.startsWith('"') && t.endsWith('"'))) {
    return t.slice(1, -1)
  }
  return t
}

/** Flat YAML subset: `key: value`, `key:` + `- item` lists, `#` comments. */
function parseFlatYaml(text) {
  const out = {}
  let listKey = null
  for (const raw of text.split(/\r?\n/)) {
    if (!raw.trim() || raw.trimStart().startsWith('#')) continue
    if (/^\s*-\s/.test(raw)) {
      if (listKey) (out[listKey] ||= []).push(unquote(raw.replace(/^\s*-\s/, '')))
      continue
    }
    const m = raw.match(/^([A-Za-z0-9_]+):(.*)$/)
    if (!m) continue
    const [, key, rest] = m
    if (rest.trim() === '') {
      listKey = key
      out[key] = []
    } else {
      listKey = null
      const v = unquote(rest)
      out[key] = v === 'true' ? true : v === 'false' ? false : v
    }
  }
  return out
}

/** Map a stored product record onto the shape the auditor expects. */
function toRecord(y) {
  return {
    ...y,
    images: Array.isArray(y.images) ? y.images : [],
    components: y.components ?? {},
    photoRoles: y.photoRoles ?? {},
    descriptionSource: y.descriptionSource ?? 'typed',
  }
}

const files = readdirSync(DIR).filter((f) => /\.ya?ml$/.test(f)).sort()
const rows = files.map((f) => {
  const y = parseFlatYaml(readFileSync(join(DIR, f), 'utf8'))
  const audit = auditListing(toRecord(y))
  return { file: f, name: y.name ?? f, department: y.department ?? '—', images: (y.images ?? []).length, audit }
})

const total = rows.length
const avg = total ? Math.round(rows.reduce((s, r) => s + r.audit.score, 0) / total) : 0
const publishable = rows.filter((r) => r.audit.publishable).length
const best = [...rows].sort((a, b) => b.audit.score - a.audit.score)[0]

// How often each rule fails across the catalogue — the repair list, ordered.
const failCounts = RULES.map((rule) => ({
  ...rule,
  fails: rows.filter((r) => r.audit.results.find((x) => x.id === rule.id && !x.pass)).length,
})).sort((a, b) => b.fails - a.fails || b.weight - a.weight)

const photoHistogram = rows.reduce((m, r) => ((m[r.images] = (m[r.images] ?? 0) + 1), m), {})

const lines = []
const P = (s = '') => lines.push(s)

P(`# LISTING AUDIT — content/products against the Faridunhill Listing Standard`)
P(`Standard v${STANDARD_VERSION} · ${total} listings audited · max score ${MAX_SCORE} pts, normalised to 100`)
P('')
P(`> **Read this before drawing a conclusion from it.** This audits the records`)
P(`> *in this repository*, not the photographs Farid actually took. These entries`)
P(`> were imported from the Etsy catalogue and the import kept one image URL per`)
P(`> item and one boilerplate description. So a low score here is first evidence`)
P(`> of a thin import pipeline, and only second evidence about the listings`)
P(`> themselves. Fixing the importer is a different and much cheaper job than`)
P(`> re-photographing anything — and it must be done before this number means`)
P(`> what it appears to mean. Regenerate with \`node scripts/audit-listings.mjs\`.`)
P('')
P(`## Scoreboard`)
P('')
P(`| | |`)
P(`|---|---|`)
P(`| Listings audited | **${total}** |`)
P(`| Average score | **${avg} / 100** |`)
P(`| Publishable under the standard (no blocking failure, ≥ ${PUBLISH_THRESHOLD}) | **${publishable} / ${total}** |`)
P(`| Best single listing | **${best ? best.audit.score : 0} / 100** |`)
P(`| Listings with ${PHOTO_MIN}+ photographs | **${rows.filter((r) => r.images >= PHOTO_MIN).length} / ${total}** |`)
P('')
P(`## Where the points are lost — the repair list, in order`)
P('')
P(`| Rule | Section | Fails | Weight | Blocking |`)
P(`|---|---|---:|---:|---|`)
for (const r of failCounts) {
  P(`| **${r.id}** ${r.label} | ${r.section} | ${r.fails} | ${r.weight} | ${r.blocking ? '⛔' : '' } |`)
}
P('')
P(`## Photographs per listing`)
P('')
P(`| Photographs | Listings |`)
P(`|---:|---:|`)
for (const k of Object.keys(photoHistogram).map(Number).sort((a, b) => a - b)) {
  P(`| ${k} | ${photoHistogram[k]} |`)
}
P('')
P(`## Section weights`)
P('')
P(`| Section | Points available |`)
P(`|---|---:|`)
for (const s of SECTIONS) P(`| ${s.name} | ${s.weight} |`)
P('')

const report = lines.join('\n')
const writeIdx = process.argv.indexOf('--write')
if (writeIdx !== -1 && process.argv[writeIdx + 1]) {
  writeFileSync(process.argv[writeIdx + 1], report + '\n')
  console.log(`wrote ${process.argv[writeIdx + 1]}`)
}
console.log(report)
