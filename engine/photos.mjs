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
 * ★ THE FEATURE-MATCH RULE (added 2026-08-02, after Farid caught the engine out)
 *
 * The engine built an episode about a TAPERED Charatan bit and illustrated it
 * with a Charatan that has a SADDLE stem. Farid spotted it instantly — as any
 * level-3 collector would, which is the whole audience we are chasing.
 *
 * "The photograph illustrates the brand, never the claim" was too weak. When
 * the claim is about a visible FEATURE, a photograph showing a different
 * feature reads as evidence against us, however carefully it is captioned.
 *
 * The rule now: a feature claim may only be illustrated by a photograph
 * TAGGED with that feature. We have no such tags yet, so the engine returns
 * the shot that is needed instead of a picture that contradicts the words.
 * Same discipline as the source law — no matching photograph, no illustration.
 */
export function photoForFeature(index, brand, feature) {
  const want = String(feature || '').toLowerCase().trim()
  if (!want) return { photo: photoForBrand(index, brand), needed: null }

  // Only a photograph whose own description states the feature may be used.
  const hit = index.find(
    (i) => i.haystack.includes(want) && matchesBrand(i, brand)
  )
  if (hit) return { photo: toPhoto(hit, brand), needed: null }

  return {
    photo: null,
    needed: `a ${brand} showing: ${feature}`,
  }
}

function matchesBrand(item, brand) {
  const needle = String(brand || '').toLowerCase().replace(/[^a-z0-9 ]/g, '').trim()
  if (!needle || needle === 'generic') return false
  const words = needle.split(/\s+/).filter((w) => w.length > 3)
  return words.length ? words.every((w) => item.haystack.includes(w)) : item.haystack.includes(needle)
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
