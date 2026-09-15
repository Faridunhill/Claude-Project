/**
 * Where Faridunhill exists outside this site.
 *
 * Supplied by Farid. This build environment's egress policy refuses eBay, Etsy
 * and Linktree outright (403 at the proxy), so none was fetched directly. The
 * Etsy shop was corroborated by search — it exists, ships from Millstone
 * Township, NJ, and its shop id 34479460 matches the i.etsystatic.com image
 * host on all 264 products. The eBay and Linktree URLs remain unconfirmed.
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
    // Canonical shop URL. faridunhill.etsy.com is a legacy subdomain redirect
    // to this same page; the /shop/ form is the one Etsy itself publishes.
    href: 'https://www.etsy.com/shop/Faridunhill',
    description: 'Our Etsy shop',
  },
  linktree: {
    label: 'All our links',
    href: 'https://linktr.ee/vintagepipevault',
    description: 'Every storefront and social account in one place',
  },
} as const

export type ExternalLink = (typeof externalLinks)[keyof typeof externalLinks]
