/**
 * Where Faridunhill exists outside this site.
 *
 * Supplied by Farid. None of these could be reached from the build environment
 * to verify, so if a link 404s, this is the one file to correct.
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
