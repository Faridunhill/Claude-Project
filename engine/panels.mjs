/**
 * STAGE 3 — PANELS
 *
 * A panel is never a generated picture. It is a stack of layers resolved from
 * the asset library BY ID:
 *
 *   5  captions + brand frame
 *   4  overlays        — labels, citations, arrows
 *   3  the object      — a real photograph, or a library prop
 *   2  the characters
 *   1  the background
 *
 * Because every layer is an id, the art behind an id can be replaced — ink
 * today, a 3D render later — without touching a single other stage. That is
 * the whole reason this file resolves ids instead of paths.
 *
 * THE LAW THIS STAGE ENFORCES:
 *   An object layer that carries a FACT must be a photograph with a citation.
 *   Drawn art carries the story; it never carries evidence.
 */
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { join } from 'node:path'

const PALETTE = {
  bg: '#2b1a12',
  panel: '#3a2418',
  ink: '#120a06',
  gold: '#c9a227',
  parchment: '#efe3cf',
  wrong: '#a8443a',
  right: '#4f7a4a',
  warn: '#b0762a',
}

export class EvidenceWithoutCitation extends Error {}

export function loadLibrary(path) {
  return JSON.parse(readFileSync(path, 'utf8'))
}

/**
 * Resolve every id in the episode. Missing ids are not an error — they are the
 * expected state before the design lands, and each one becomes a placeholder
 * that names itself on screen so nothing is silently absent.
 */
export function resolvePanels(episode, library, { outDir }) {
  mkdirSync(join(outDir, 'panels'), { recursive: true })
  const missing = new Set()

  const resolveId = (id, kind) => {
    const asset = library.assets[id]
    if (asset?.file) return { id, kind, status: asset.status || 'final', file: asset.file }
    missing.add(id)
    return { id, kind, status: 'placeholder', file: null }
  }

  const resolved = episode.panels.map((p) => {
    // Evidence rule: a photograph slot may only be filled by a cited photograph.
    let object = null
    if (p.object) {
      const photo = library.photos?.[p.object.slot] || null
      if (photo && !photo.citation) {
        throw new EvidenceWithoutCitation(
          `panel ${p.panel}: photo "${p.object.slot}" has no citation — refused`
        )
      }
      object = photo
        ? { kind: 'photo', slot: p.object.slot, file: photo.file, citation: photo.citation }
        : { kind: 'photo-slot', slot: p.object.slot, hint: p.object.hint, status: 'awaiting photograph' }
    }

    return {
      ...p,
      layers: {
        background: resolveId(p.background, 'background'),
        characters: p.characters.map((c) => resolveId(c, 'character')),
        object,
        overlays: p.overlays,
      },
    }
  })

  // Render a placeholder sheet per panel so the episode is watchable today.
  for (const p of resolved) {
    const svg = placeholderPanel(p, episode)
    writeFileSync(join(outDir, 'panels', `panel-${String(p.panel).padStart(2, '0')}.svg`), svg)
  }

  return { panels: resolved, missing: [...missing].sort() }
}

/** A placeholder that is honest about being one, and names every slot it stands in for. */
function placeholderPanel(p, episode) {
  const W = 1280
  const H = 720
  const chars = p.layers.characters
  const charBoxes = chars
    .map((c, i) => {
      const boxW = 300
      const gap = 60
      const totalW = chars.length * boxW + (chars.length - 1) * gap
      const x = (W - totalW) / 2 + i * (boxW + gap)
      return `
    <g>
      <rect x="${x}" y="${H - 430}" width="${boxW}" height="360" rx="6"
            fill="none" stroke="${PALETTE.gold}" stroke-opacity="0.5" stroke-dasharray="8 6"/>
      <text x="${x + boxW / 2}" y="${H - 250}" text-anchor="middle"
            font-family="Georgia, serif" font-size="19" fill="${PALETTE.parchment}" fill-opacity="0.85">${esc(c.id)}</text>
      <text x="${x + boxW / 2}" y="${H - 222}" text-anchor="middle"
            font-family="Georgia, serif" font-size="14" fill="${PALETTE.gold}" fill-opacity="0.7">${c.status}</text>
    </g>`
    })
    .join('')

  const obj = p.layers.object
  const objBox = obj
    ? `
    <g>
      <rect x="${W - 360}" y="70" width="290" height="200" rx="6"
            fill="#000" fill-opacity="0.25" stroke="${obj.kind === 'photo' ? PALETTE.right : PALETTE.gold}"
            stroke-opacity="0.6" stroke-dasharray="${obj.kind === 'photo' ? '0' : '8 6'}"/>
      <text x="${W - 215}" y="150" text-anchor="middle" font-family="Georgia, serif" font-size="16"
            fill="${PALETTE.parchment}" fill-opacity="0.9">${esc(obj.slot)}</text>
      <text x="${W - 215}" y="176" text-anchor="middle" font-family="Georgia, serif" font-size="13"
            fill="${PALETTE.gold}" fill-opacity="0.75">${esc(obj.kind === 'photo' ? 'PHOTOGRAPH — cited' : 'awaiting photograph')}</text>
      <text x="${W - 215}" y="200" text-anchor="middle" font-family="Georgia, serif" font-size="11"
            fill="${PALETTE.parchment}" fill-opacity="0.5">${esc((obj.hint || obj.citation || '').slice(0, 40))}</text>
    </g>`
    : ''

  const overlays = p.layers.overlays
    .map((o, i) => {
      const color =
        o.tone === 'wrong' ? PALETTE.wrong : o.tone === 'right' ? PALETTE.right : o.tone === 'warn' ? PALETTE.warn : PALETTE.gold
      return `
    <g>
      <rect x="70" y="${100 + i * 54}" width="${Math.min(760, 26 + esc(o.text).length * 11)}" height="40" rx="4"
            fill="${color}" fill-opacity="0.16" stroke="${color}" stroke-opacity="0.75"/>
      <text x="86" y="${127 + i * 54}" font-family="Georgia, serif" font-size="18" fill="${PALETTE.parchment}">${esc(o.text)}</text>
    </g>`
    })
    .join('')

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <rect width="${W}" height="${H}" fill="${PALETTE.bg}"/>
  <rect x="26" y="26" width="${W - 52}" height="${H - 52}" fill="${PALETTE.panel}" stroke="${PALETTE.gold}" stroke-opacity="0.55" stroke-width="2"/>
  <text x="${W / 2}" y="62" text-anchor="middle" font-family="Georgia, serif" font-size="15"
        letter-spacing="5" fill="${PALETTE.gold}" fill-opacity="0.85">F A R I D U N H I L L</text>
  <text x="70" y="${H - 470}" font-family="Georgia, serif" font-size="13" fill="${PALETTE.parchment}" fill-opacity="0.4">
    background: ${esc(p.layers.background.id)} · ${p.layers.background.status}
  </text>
  ${charBoxes}
  ${objBox}
  ${overlays}
  <rect x="26" y="${H - 118}" width="${W - 52}" height="92" fill="#000" fill-opacity="0.45"/>
  ${wrapText(p.narration, 96)
    .map(
      (line, i) =>
        `<text x="${W / 2}" y="${H - 78 + i * 28}" text-anchor="middle" font-family="Georgia, serif" font-size="21" fill="${PALETTE.parchment}">${esc(line)}</text>`
    )
    .join('')}
  <text x="${W - 44}" y="${H - 36}" text-anchor="end" font-family="Georgia, serif" font-size="12"
        fill="${PALETTE.gold}" fill-opacity="0.6">panel ${p.panel} · ${p.role} · ${p.duration}s</text>
  <text x="44" y="${H - 36}" font-family="Georgia, serif" font-size="12" fill="${PALETTE.parchment}" fill-opacity="0.35">PLACEHOLDER ART — awaiting the design commission</text>
</svg>
`
}

function wrapText(text, max) {
  const words = String(text).split(/\s+/)
  const lines = []
  let cur = ''
  for (const w of words) {
    if ((cur + ' ' + w).trim().length > max) {
      lines.push(cur.trim())
      cur = w
    } else cur += ' ' + w
  }
  if (cur.trim()) lines.push(cur.trim())
  return lines.slice(0, 2)
}

function esc(s) {
  return String(s ?? '').replace(/[<>&]/g, (c) => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;' })[c])
}
