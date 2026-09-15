import Link from 'next/link'
import { externalLinks } from '@/lib/links'
import Logo from '@/components/ui/Logo'

const shopLinks = [
  { label: 'Estate Pipes', href: '/shop/estate-pipes' },
  { label: 'New Pipes', href: '/shop/new-pipes' },
  { label: 'Meerschaum', href: '/shop/meerschaum' },
  { label: 'Rare & Collectible', href: '/shop/rare-collectible' },
  { label: 'Leather Bags & Cases', href: '/shop/leather-bags' },
  { label: 'Cigar & Smoking Accessories', href: '/shop/cigar-smoking-accessories' },
  { label: 'Lighters & Matches', href: '/shop/lighters' },
  { label: 'Sale & Clearance', href: '/shop/sale' },
]

const infoLinks = [
  { label: 'About Us', href: '/about' },
  { label: 'The Journal', href: '/blog' },
  { label: 'Shipping Policy', href: '/shipping' },
  { label: 'Return Policy', href: '/returns' },
  { label: 'Privacy Policy', href: '/privacy' },
  { label: 'Contact Us', href: '/contact' },
]

export default function Footer() {
  const year = new Date().getFullYear()

  return (
    <footer className="bg-mahogany-dark border-t border-gold/15">
      {/* Main footer content */}
      <div className="max-w-screen-xl mx-auto px-6 lg:px-12 py-16">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-10">
          {/* Brand column */}
          <div className="lg:col-span-1">
            <Logo size="sm" variant="light" />
            <p className="font-lora text-parchment/55 text-sm leading-relaxed mt-5">
              Estate pipes, vintage leather, and gentleman&apos;s smoking accessories. Rooted in
              thirty years of collecting. Est. 2015.
            </p>

            {/* Real destinations only. Four dead href="#" icons used to sit
                here, implying a social presence that went nowhere. */}
            <div className="mt-6">
              <p className="font-playfair text-parchment/70 text-xs uppercase tracking-widest mb-2.5">
                Find Us Elsewhere
              </p>
              <ul className="space-y-1.5">
                {Object.values(externalLinks).map((link) => (
                  <li key={link.href}>
                    <a
                      href={link.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-lora text-parchment/55 text-sm hover:text-gold transition-colors nav-link-underline"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Shop links */}
          <div>
            <h3 className="font-playfair font-semibold text-parchment text-sm uppercase tracking-widest mb-5">
              Shop
            </h3>
            <ul className="space-y-2.5">
              {shopLinks.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="font-lora text-parchment/55 text-sm hover:text-gold transition-colors nav-link-underline"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Info links */}
          <div>
            <h3 className="font-playfair font-semibold text-parchment text-sm uppercase tracking-widest mb-5">
              Information
            </h3>
            <ul className="space-y-2.5">
              {infoLinks.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="font-lora text-parchment/55 text-sm hover:text-gold transition-colors nav-link-underline"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact & badges */}
          <div>
            <h3 className="font-playfair font-semibold text-parchment text-sm uppercase tracking-widest mb-5">
              Contact Us
            </h3>
            <div className="space-y-3 font-lora text-parchment/55 text-sm">
              <p>
                <span className="text-gold/70">Email</span><br />
                <a href="mailto:contact@faridunhill.com" className="hover:text-gold transition-colors">
                  contact@faridunhill.com
                </a>
              </p>
              <p>
                <span className="text-gold/70">Location</span><br />
                New Jersey, United States<br />
                Online only — no walk-in premises
              </p>
            </div>

            {/* Trust badges */}
            <div className="mt-6 space-y-2">
              {[
                '🔒 Secure Checkout via Stripe',
                '✦ Age Verification Required',
                '📦 Free Shipping, Every Order',
              ].map((badge) => (
                <div key={badge} className="flex items-center gap-2 text-xs font-lora text-parchment/40">
                  <span>{badge}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Gold ornamental divider */}
      <div className="h-px bg-gradient-to-r from-transparent via-gold/30 to-transparent" />

      {/* Bottom bar */}
      <div className="max-w-screen-xl mx-auto px-6 lg:px-12 py-5 flex flex-col sm:flex-row items-center justify-between gap-3">
        <p className="font-lora text-parchment/35 text-xs text-center sm:text-left">
          &copy; {year} Faridunhill. All rights reserved. Must be 21+ to purchase tobacco products.
        </p>
        <p className="font-fell italic text-gold/30 text-xs">
          &ldquo;Where Every Pipe Tells a Story&rdquo;
        </p>
      </div>
    </footer>
  )
}
