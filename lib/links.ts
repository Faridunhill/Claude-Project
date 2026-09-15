/**
 * Where Faridunhill exists outside this site.
 *
 * Supplied by Farid. This build environment's egress policy refuses eBay, Etsy
 * and Linktree outright (403 at the proxy), so none was fetched here — all
 * three were confirmed by Farid opening them and sending screenshots.
 * If a link 404s, this is the one file to correct.
 *
 * The eBay link carries weight beyond convenience: it is the public record
 * behind the "more than five thousand pieces sold" line on /about. A claim a
 * customer can check in one click is worth more than any amount of prose.
 */
export const externalLinks = {
  ebay: {
    label: 'eBay',
    href: 'https://ebay.us/m/aA3qNi',
    description: 'Our eBay storefront and feedback record',
  },
  etsy: {
    label: 'Etsy',
    // Farid's own URL, given twice. The subdomain form redirects to
    // www.etsy.com/shop/Faridunhill, which is the equivalent canonical if this
    // one ever stops resolving.
    href: 'https://faridunhill.etsy.com',
    description: 'Our Etsy shop',
  },
  linktree: {
    label: 'All our links',
    href: 'https://linktr.ee/vintagepipevault',
    description: 'Every storefront and social account in one place',
  },
} as const

export type ExternalLink = (typeof externalLinks)[keyof typeof externalLinks]

/**
 * The marketplace record — the shop's only third-party-verifiable trust signal.
 *
 * These are NOT invented social proof, and they are not reviews of anything
 * sold on this site. They are public seller statistics from eBay and Etsy,
 * each shown next to a link to the page it came from, so a visitor can check
 * every number in one click. That is the whole point: a figure nobody can
 * verify is worth less than no figure at all.
 *
 * Read from screenshots of the live pages on 2026-09-15:
 *   eBay  — 5,688 sold · 98.4% positive · 1,162 followers · 310 listings
 *   Etsy  — 2,500 sales · 4.8 from 1.1k reviews · 4 years · 316 listings
 *
 * Every figure below is rounded DOWN from what was seen, so it stays true as
 * the real numbers grow. Never round up, and never edit a number here without
 * looking at the live page first — a stale boast is the same problem as an
 * invented one. `verifiedOn` is what makes going stale visible.
 */
export const marketplaceRecord = {
  verifiedOn: 'September 2026',
  platforms: [
    {
      name: 'eBay',
      href: externalLinks.ebay.href,
      stats: [
        { value: '5,600+', label: 'items sold' },
        { value: '98.4%', label: 'positive feedback' },
      ],
    },
    {
      name: 'Etsy',
      href: externalLinks.etsy.href,
      stats: [
        { value: '2,500+', label: 'sales' },
        { value: '4.8 / 5', label: 'from 1,100+ reviews' },
      ],
    },
  ],
} as const
