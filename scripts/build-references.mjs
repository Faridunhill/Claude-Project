#!/usr/bin/env node
/**
 * Build the public reference list from the ark manifest.
 *
 * LAW 2: we publish WHAT WE HOLD, never the pages themselves. This script reads
 * `channel/NEW_UPLOADS/ark_manifest.csv` (a file listing — no content) and emits
 * `content/references/holdings.json`, a bibliography. No file is ever copied,
 * linked or exposed by this script or by the page it feeds.
 *
 * Re-run whenever a new manifest lands:  node scripts/build-references.mjs
 */
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const MANIFEST = join(ROOT, 'channel/NEW_UPLOADS/ark_manifest.csv')
const OUT = join(ROOT, 'content/references/holdings.json')

/** Split a CSV line that uses quoted fields. */
function parseLine(line) {
  const out = []
  let cur = ''
  let inQuotes = false
  for (let i = 0; i < line.length; i++) {
    const ch = line[i]
    if (ch === '"') {
      if (inQuotes && line[i + 1] === '"') { cur += '"'; i++ } else { inQuotes = !inQuotes }
    } else if (ch === ',' && !inQuotes) {
      out.push(cur); cur = ''
    } else {
      cur += ch
    }
  }
  out.push(cur)
  return out
}

/** Turn a filename into something a human would read on a shelf. */
function cleanTitle(basename) {
  let t = basename.replace(/\.[a-z0-9]+$/i, '')
  t = t.replace(/^\d{6,}[-_]/, '')            // Scribd-style numeric ids
  t = t.split('__').pop()                      // "slug__Real Title"
  t = t.replace(/[-_]+/g, ' ')
  t = t.replace(/\s+text$/i, '')
  t = t.replace(/\bpdf\b/gi, '')
  t = t.replace(/\s{2,}/g, ' ').trim()
  return t
}

/**
 * A file whose name carries no bibliographic information — a bare page scan, a
 * uuid, a Europeana hash. These are not holdings; they are pages OF a holding,
 * so they get folded into a folder-level entry instead of listed individually.
 */
function isOpaque(title) {
  const compact = title.replace(/[\s-]/g, '')
  if (compact.length < 4) return true
  if (/^page\s*\d+$/i.test(title.trim())) return true
  if (/^(img|scan|image|dsc|p)\s*\d+$/i.test(title.trim())) return true
  if (/[0-9a-f]{24,}/i.test(compact)) return true
  const hexish = compact.replace(/[^0-9a-f]/gi, '').length / compact.length
  return hexish > 0.9 && compact.length > 16
}

/** Folders whose contents are pages/plates of one body of material. */
const FOLDER_TITLES = {
  'social history photos': 'Europeana & Mass-Observation — pipe smokers photographed, 1900s–1950s',
  'museum catalogue pages': 'Gothenburg ethnographic collection — catalogue pages',
  'wilke ads 1950s': 'Wilke of Washington — original advertisements, 1950s',
  'archive org': 'Archive.org — scanned trade material',
}

/** Turn a folder path into the title of the work its pages belong to. */
function folderTitle(rel) {
  const parts = rel.split(/[\\/]/).slice(0, -1)
  const named = [...parts].reverse().find((p) => p && !/^\d[_\s]/.test(p))
  const t = cleanTitle(named || parts[parts.length - 1] || 'Uncatalogued folder')
  const mapped = FOLDER_TITLES[t.toLowerCase()]
  if (mapped) return mapped
  // Processing scratch directories are not holdings — the source PDFs already are.
  if (/^(blanks?|tmp|temp|out|output|work)$/i.test(t)) return null
  if (/\b(all|test|run\d*|ch\d+|v\d+)$/i.test(t)) return null
  return t
}

function extractYear(title) {
  const m = title.match(/\b(1[5-9]\d{2}|20[0-2]\d)\b/)
  return m ? Number(m[1]) : null
}

/** Which shelf does this item sit on? */
function classify(rel, title) {
  const p = rel.toLowerCase()
  if (p.includes('social_history_photos')) return 'social'
  if (p.includes('museum_catalogue_pages')) return 'museum'
  if (p.includes('_ads_') || p.includes('/ads/') || /\bad\b/.test(title.toLowerCase())) return 'advertising'
  if (p.includes('trade_lists') || /price list|trade price/i.test(title)) return 'trade'
  if (p.includes('catalogue_hunter_finds') || /catalog|catalogue/i.test(title)) return 'catalogue'
  if (/magazine|pipe lovers|tobacco world|pipes and tobaccos|pipecollector/i.test(title)) return 'magazine'
  return 'book'
}

const SHELVES = [
  { key: 'catalogue',   title: 'Manufacturers’ catalogues & shape charts', blurb: 'The documents that decide a dating question at level two. Where a catalogue exists, a guess is not needed.' },
  { key: 'trade',       title: 'Trade price lists',                        blurb: 'Dated dealer and trade lists — often the only surviving record of a model year.' },
  { key: 'book',        title: 'Books, monographs & papers',               blurb: 'Scholarship on pipes, clay-pipe chronology and the briar trade, including archaeological dating literature.' },
  { key: 'magazine',    title: 'Periodicals',                              blurb: 'Trade and collector magazines, read for maker news, advertisements and dated announcements.' },
  { key: 'advertising', title: 'Period advertising',                       blurb: 'Original advertisements — frequently the earliest dated appearance of a shape or a finish.' },
  { key: 'museum',      title: 'Museum & institutional catalogue pages',   blurb: 'Pages from institutional collection catalogues, used as dated third-party anchors.' },
  { key: 'social',      title: 'Social-history photography',               blurb: 'Photographs of pipes in daily use — dated evidence of what was carried, and when.' },
]

const rows = readFileSync(MANIFEST, 'utf8').split(/\r?\n/).filter(Boolean).slice(1)

const mirrors = new Map()   // ark -> {files, bytes}
const items = new Map()     // title -> item
let totalBytes = 0
let totalFiles = 0

for (const line of rows) {
  const [ark, rel, bytesRaw, ext] = parseLine(line)
  if (!ark || !rel) continue
  const bytes = Number(bytesRaw) || 0
  totalBytes += bytes
  totalFiles++

  // Mirrored websites are counted, never enumerated — they are one holding each.
  if (ark === 'pipephil_mirror' || ark === 'pipedia') {
    const m = mirrors.get(ark) || { files: 0, bytes: 0 }
    m.files++; m.bytes += bytes
    mirrors.set(ark, m)
    continue
  }

  // Skip the machinery of a mirror and our own notes.
  if (/\.(json|js|css|ico|md|txt)$/i.test(ext || '')) continue

  const basename = rel.split(/[\\/]/).pop()
  let title = cleanTitle(basename)
  let pages = 0

  // Page scans and hash-named images are pages OF a work, not works. Fold them
  // into one entry for the folder that holds them, and count the sheets.
  if (!title || isOpaque(title)) {
    title = folderTitle(rel)
    if (!title || isOpaque(title)) continue
    pages = 1
  }

  const key = title.toLowerCase()
  if (items.has(key)) {
    const it = items.get(key)
    it.copies++
    if (pages) it.pages = (it.pages || 0) + 1
    continue
  }

  items.set(key, {
    title,
    year: extractYear(title) ?? extractYear(rel),
    shelf: classify(rel, title),
    format: pages ? 'SCAN' : (ext || '').replace('.', '').toUpperCase() || 'FILE',
    copies: 1,
    ...(pages ? { pages: 1 } : {}),
  })
}

const all = [...items.values()].sort((a, b) => {
  if (a.year && b.year) return a.year - b.year
  if (a.year) return -1
  if (b.year) return 1
  return a.title.localeCompare(b.title)
})

const shelves = SHELVES.map((s) => ({
  ...s,
  items: all.filter((i) => i.shelf === s.key).map(({ shelf, copies, ...rest }) => rest),
})).filter((s) => s.items.length > 0)

const MIRROR_LABELS = {
  pipephil_mirror: {
    title: 'pipephil.eu — complete mirror',
    note: 'Mirrored in full when the site announced its closure, so the knowledge survives the source. Held for reference only.',
  },
  pipedia: {
    title: 'Pipedia — reference capture',
    note: 'Held for reference and cross-checking. Pipedia is live-lookup first; we cite it, we never republish it.',
  },
}

const payload = {
  generated_from: 'channel/NEW_UPLOADS/ark_manifest.csv',
  totals: {
    files: totalFiles,
    gigabytes: Number((totalBytes / 1073741824).toFixed(2)),
    catalogued_items: all.length,
    dated_span: (() => {
      const years = all.map((i) => i.year).filter(Boolean)
      return years.length ? [Math.min(...years), Math.max(...years)] : null
    })(),
  },
  mirrors: [...mirrors.entries()].map(([key, m]) => ({
    key,
    title: MIRROR_LABELS[key]?.title || key,
    note: MIRROR_LABELS[key]?.note || '',
    files: m.files,
    gigabytes: Number((m.bytes / 1073741824).toFixed(2)),
  })),
  shelves,
}

mkdirSync(dirname(OUT), { recursive: true })
writeFileSync(OUT, JSON.stringify(payload, null, 2) + '\n')

console.log(`references: ${totalFiles} files → ${all.length} catalogued items across ${shelves.length} shelves`)
for (const s of shelves) console.log(`  ${s.items.length.toString().padStart(4)}  ${s.title}`)
