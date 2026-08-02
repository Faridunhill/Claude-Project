/**
 * THE PHOTO INDEX
 *
 * With no characters, the photograph IS the picture. This indexes the 264 real
 * pipes already in `content/products/` and finds one that belongs to the brand
 * an episode is about.
 *
 * THE HONESTY RULE THIS FILE OBEYS:
 *   A photograph illustrates the BRAND. It never illustrates the CLAIM.
 *   We show a real Charatan while explaining how Charatans are dated; we never
 *   suggest that this particular pipe carries the mark under discussion. Every
 *   caption says what the object actually is, and nothing more.
 */
import { readFileSync, readdirSync } from 'node:fs'
import { join } from 'node:path'
import yaml from 'js-yaml'

/** Words that appear in listing titles but say nothing about the maker. */
const NOISE =
  /\b(estate|pipe|pipes|briar|smooth|bent|straight|billiard|vintage|antique|smoking|tobacco|stem|vulcanite|acrylic|saddle|filter|mm|inch|shape|collection|made|italy|italian|danish|denmark|england|english|french|germany|german)\b/gi

export function buildPhotoIndex(productsDir) {
  const items = []
  for (const file of readdirSync(productsDir).filter((f) => f.endsWith('.yaml'))) {
    let d
    try {
      d = yaml.load(readFileSync(join(productsDir, file), 'utf8'))
    } catch {
      continue
    }
    const images = d?.images || []
    if (!images.length || !d?.name) continue
    items.push({
      name: String(d.name),
      brand: d.brand ? String(d.brand) : null,
      image: images[0],
      slug: file.replace(/\.yaml$/, ''),
      haystack: `${d.brand || ''} ${d.name}`.toLowerCase(),
    })
  }
  return items
}

/**
 * Find a photograph of this brand. Returns null rather than a wrong pipe —
 * an unrelated photograph beside a dating claim is a small lie.
 */
export function photoForBrand(index, brand) {
  if (!brand) return null
  const needle = String(brand).toLowerCase().replace(/[^a-z0-9 ]/g, '').trim()
  if (!needle || needle === 'generic') return null

  // Longest brand word wins: "ser jacopo" should not match on "ser".
  const words = needle.split(/\s+/).filter((w) => w.length > 3 && !NOISE.test(w))
  const key = words.length ? words.join(' ') : needle

  const exact = index.find((i) => i.haystack.includes(key))
  if (exact) return toPhoto(exact, brand)

  const loose = words.length
    ? index.find((i) => words.every((w) => i.haystack.includes(w)))
    : null
  return loose ? toPhoto(loose, brand) : null
}

function toPhoto(item, brand) {
  return {
    file: item.image,
    slug: item.slug,
    // The caption states the object, never the claim.
    citation: `${item.name} — Faridunhill archive`,
    brand,
  }
}
