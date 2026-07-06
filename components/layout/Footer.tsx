import Link from 'next/link'
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
              Purveyors of fine pipes, tobaccos, and gentleman&apos;s accessories. Rooted in
              thirty years of collector knowledge and old-world craftsmanship.
            </p>
            {/* Social links */}
            <div className="flex items-center gap-3 mt-6">
              {[
                { label: 'Instagram', icon: 'IG' },
                { label: 'Facebook', icon: 'FB' },
                { label: 'X / Twitter', icon: 'X' },
                { label: 'Reddit', icon: 'R' },
              ].map((s) => (
                <a
                  key={s.label}
                  href="#"
                  aria-label={s.label}
                  className="w-8 h-8 rounded-sm border border-gold/20 flex items-center justify-center text-gold/50 hover:border-gold/50 hover:text-gold transition-colors font-playfair text-xs font-bold"
                >
                  {s.icon}
                </a>
              ))}
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
                <span className="text-gold/70">Hours</span><br />
                Mon–Fri: 9 AM – 6 PM EST<br />
                Sat: 10 AM – 4 PM EST
              </p>
            </div>

            {/* Trust badges */}
            <div className="mt-6 space-y-2">
              {[
                '🔒 Secure Checkout via Stripe',
                '✦ Age Verification Required',
                '📦 Free Shipping Over £75',
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
