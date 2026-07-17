#!/usr/bin/env node
/**
 * Checks the German (DDB API 2.0, keyless) and English (TNA Discovery,
 * keyless) archive APIs for maker-identification research.
 *
 * Usage:
 *   node scripts/check-archive-apis.mjs                 # run default maker queries
 *   node scripts/check-archive-apis.mjs "Offenbach Lederwaren" "Solingen Zigarrenabschneider"
 *
 * Requires Node 18+ (built-in fetch). No API keys needed.
 */

const DDB_BASE = 'https://api.deutsche-digitale-bibliothek.de/2'
const TNA_BASE = 'https://discovery.nationalarchives.gov.uk/API'

// Default research targets: the unidentified items in content/products/
const DEFAULT_QUERIES = [
  'Lederwarenfabrik Offenbach',      // anonymous-atelier hard leather cases
  'Solingen Zigarrenabschneider',    // unmarked Solingen V-cut cutter
  'Pfeifenfabrik',                   // German pipe works generally
  'Meerschaum Pfeife Wien',          // unsigned c.1900 meerschaum
  'Charatan tobacco pipe',           // English makers — TNA side
  'Comoy pipe London',
]

const queries = process.argv.slice(2).length ? process.argv.slice(2) : DEFAULT_QUERIES

async function getJson(url, headers = {}) {
  const res = await fetch(url, { headers: { Accept: 'application/json', ...headers } })
  if (!res.ok) throw new Error(`HTTP ${res.status} ${res.statusText}`)
  return res.json()
}

async function searchDdb(query) {
  const url = `${DDB_BASE}/search?query=${encodeURIComponent(query)}&rows=5`
  const data = await getJson(url)
  const docs = data?.results?.[0]?.docs ?? data?.docs ?? []
  return {
    total: data?.numberOfResults ?? data?.results?.[0]?.numberOfDocs ?? docs.length,
    titles: docs.slice(0, 3).map((d) => d.title ?? d.label ?? d.id),
  }
}

async function searchTna(query) {
  const url = `${TNA_BASE}/search/records?sps.searchQuery=${encodeURIComponent(query)}&sps.resultsPageSize=5`
  const data = await getJson(url)
  const records = data?.records ?? []
  return {
    total: data?.count ?? records.length,
    titles: records.slice(0, 3).map((r) => (r.title ?? r.description ?? r.id ?? '').toString().slice(0, 100)),
  }
}

let failures = 0

for (const query of queries) {
  console.log(`\n=== "${query}" ===`)
  for (const [name, fn] of [['DDB API 2.0 (DE)', searchDdb], ['TNA Discovery (UK)', searchTna]]) {
    try {
      const { total, titles } = await fn(query)
      console.log(`  ${name}: ${total} hits`)
      for (const t of titles) console.log(`    - ${t}`)
    } catch (err) {
      failures++
      console.log(`  ${name}: FAILED — ${err.message}`)
    }
  }
}

console.log(`\nDone. ${failures ? `${failures} request(s) failed.` : 'All requests succeeded — both archives reachable without API keys.'}`)
process.exitCode = failures ? 1 : 0
