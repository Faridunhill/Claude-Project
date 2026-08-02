'use client'

import { useState, useEffect, useRef } from 'react'
import Link from 'next/link'
import { useCart } from '@/context/CartContext'
import Logo from '@/components/ui/Logo'
import CartDrawer from '@/components/layout/CartDrawer'

const departments = [
  {
    name: 'Estate Pipes',
    slug: 'estate-pipes',
    subcategories: ['English & Danish', 'German & Austrian', 'Italian & French', 'Freehand & Figural'],
    desc: 'Seasoned companions with history in the grain.',
  },
  {
    name: 'New Pipes',
    slug: 'new-pipes',
    subcategories: ['New Old Stock', 'Contemporary Makers'],
    desc: 'Unsmoked and ready for the first bowl.',
  },
  {
    name: 'Meerschaum',
    slug: 'meerschaum',
    subcategories: ['Figural & Sultan', 'Classic Shapes'],
    desc: 'Hand-carved sea foam that colors with every smoke.',
  },
  {
    name: 'Rare & Collectible',
    slug: 'rare-collectible',
    subcategories: ['Complete Sets', 'Museum Grade'],
    desc: 'Rarities and complete sets for the serious collector.',
  },
  {
    name: 'Leather Bags & Cases',
    slug: 'leather-bags',
    subcategories: ['Pipe Bags', 'Tobacco Pouches', 'Cigar Cases', 'Travel Sets'],
    desc: 'Handcrafted leather — built to accompany a lifetime of smoke.',
  },
  {
    name: 'Cigar & Smoking Accessories',
    slug: 'cigar-smoking-accessories',
    subcategories: ['Cigar Cutters', 'Humidors', 'Ashtrays', 'Pipe Tools & Stands'],
    desc: 'The proper accoutrements of the smoking life.',
  },
  {
    name: 'Lighters & Matches',
    slug: 'lighters',
    subcategories: ['Pipe Lighters', 'Petrol & Jet', 'Table Lighters'],
    desc: 'Strike the proper flame — every time.',
  },
  {
    name: 'Sale & Clearance',
    slug: 'sale',
    subcategories: [],
    desc: 'Exceptional value on fine stock.',
  },
]

export default function Navigation() {
  const { itemCount, openCart } = useCart()
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const [searchOpen, setSearchOpen] = useState(false)
  const [activeMenu, setActiveMenu] = useState<string | null>(null)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const searchRef = useRef<HTMLInputElement>(null)
  const menuTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  useEffect(() => {
    if (searchOpen) searchRef.current?.focus()
  }, [searchOpen])

  function handleMenuEnter(slug: string) {
    if (menuTimerRef.current) clearTimeout(menuTimerRef.current)
    setActiveMenu(slug)
  }

  function handleMenuLeave() {
    menuTimerRef.current = setTimeout(() => setActiveMenu(null), 150)
  }

  return (
    <>
      <header
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          scrolled
            ? 'bg-mahogany-dark shadow-mahogany border-b border-gold/20'
            : 'bg-mahogany/95 backdrop-blur-sm'
        }`}
      >
        {/* Top bar */}
        <div className="border-b border-gold/10 bg-mahogany-dark/80 text-center py-1.5 text-xs font-lora text-gold-pale/70 tracking-widest">
          FREE SHIPPING ON ORDERS OVER $75 &nbsp;·&nbsp; AGE VERIFICATION REQUIRED &nbsp;·&nbsp; EST. 2015
        </div>

        <div className="max-w-screen-xl mx-auto px-4 lg:px-8">
          <div className="flex items-center justify-between h-20 gap-4">
            {/* Logo */}
            <div className="flex-shrink-0">
              <Logo size="md" variant="light" />
            </div>

            {/* Desktop nav — Department mega menu trigger */}
            <nav className="hidden lg:flex items-center gap-6" aria-label="Main navigation">
              <div
                className="relative nav-item"
                onMouseEnter={() => handleMenuEnter('all')}
                onMouseLeave={handleMenuLeave}
              >
                <button className="nav-link-underline flex items-center gap-1.5 text-parchment/90 hover:text-gold font-lora text-sm tracking-wide transition-colors py-2">
                  Shop All Departments
                  <ChevronDown className="w-3.5 h-3.5 opacity-60" />
                </button>

                {/* Mega Menu */}
                {activeMenu === 'all' && (
                  <div
                    className="mega-menu open absolute top-full left-1/2 -translate-x-1/2 mt-2 w-[780px] bg-mahogany-light border border-gold/20 shadow-mahogany rounded-sm overflow-hidden"
                    onMouseEnter={() => handleMenuEnter('all')}
                    onMouseLeave={handleMenuLeave}
                  >
                    <div className="p-6">
                      <div className="grid grid-cols-3 gap-4">
                        {departments.map((dept) => (
                          <Link
                            key={dept.slug}
                            href={`/shop/${dept.slug}`}
                            className="group p-3 rounded-sm hover:bg-gold/10 transition-colors border border-transparent hover:border-gold/20"
                            onClick={() => setActiveMenu(null)}
                          >
                            <p className="font-playfair font-semibold text-parchment group-hover:text-gold text-sm transition-colors">
                              {dept.name}
                            </p>
                            <p className="text-xs text-parchment/50 font-lora mt-0.5 line-clamp-1">
                              {dept.desc}
                            </p>
                          </Link>
                        ))}
                      </div>
                      <div className="mt-4 pt-4 border-t border-gold/15 flex items-center justify-between">
                        <p className="text-xs text-parchment/40 font-fell italic">
                          &ldquo;The pipe is the refuge of the solitary, and the companion of the meditative.&rdquo;
                        </p>
                        <Link
                          href="/shop"
                          className="btn-ghost text-xs px-4 py-1.5 rounded-sm"
                          onClick={() => setActiveMenu(null)}
                        >
                          View All →
                        </Link>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <Link href="/blog" className="nav-link-underline text-parchment/80 hover:text-gold font-lora text-sm tracking-wide transition-colors">
                The Journal
              </Link>
              <Link href="/references" className="nav-link-underline text-parchment/80 hover:text-gold font-lora text-sm tracking-wide transition-colors">
                References
              </Link>
              <Link href="/about" className="nav-link-underline text-parchment/80 hover:text-gold font-lora text-sm tracking-wide transition-colors">
                Our Story
              </Link>
            </nav>

            {/* Right controls */}
            <div className="flex items-center gap-3">
              {/* Search */}
              <div className="relative hidden md:block">
                {searchOpen ? (
                  <div className="flex items-center gap-2 bg-mahogany-light border border-gold/30 rounded-sm px-3 py-1.5">
                    <SearchIcon className="w-4 h-4 text-gold/60 flex-shrink-0" />
                    <input
                      ref={searchRef}
                      type="text"
                      placeholder="Search pipes, tobacco, cigars..."
                      className="bg-transparent text-parchment text-sm font-lora placeholder-parchment/30 outline-none w-48"
                      onBlur={() => setSearchOpen(false)}
                    />
                  </div>
                ) : (
                  <button
                    onClick={() => setSearchOpen(true)}
                    className="p-2 text-parchment/70 hover:text-gold transition-colors"
                    aria-label="Open search"
                  >
                    <SearchIcon className="w-5 h-5" />
                  </button>
                )}
              </div>

              {/* Cart */}
              <button
                onClick={openCart}
                className="relative p-2 text-parchment/70 hover:text-gold transition-colors"
                aria-label={`Open cart — ${itemCount} items`}
              >
                <ShoppingBagIcon className="w-5 h-5" />
                {itemCount > 0 && (
                  <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-gold text-mahogany text-[10px] font-bold rounded-full flex items-center justify-center">
                    {itemCount > 9 ? '9+' : itemCount}
                  </span>
                )}
              </button>

              {/* Mobile hamburger */}
              <button
                className="lg:hidden p-2 text-parchment/70 hover:text-gold transition-colors"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                aria-label="Toggle mobile menu"
              >
                {mobileMenuOpen ? <XIcon className="w-5 h-5" /> : <MenuIcon className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden bg-mahogany-dark border-t border-gold/15 max-h-[75vh] overflow-y-auto">
            <nav className="divide-y divide-gold/10">
              {departments.map((dept) => (
                <Link
                  key={dept.slug}
                  href={`/shop/${dept.slug}`}
                  className="block px-6 py-3.5 font-playfair text-parchment/90 hover:text-gold hover:bg-gold/5 transition-colors text-sm"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {dept.name}
                </Link>
              ))}
              <Link
                href="/blog"
                className="block px-6 py-3.5 font-lora text-parchment/70 hover:text-gold hover:bg-gold/5 transition-colors text-sm"
                onClick={() => setMobileMenuOpen(false)}
              >
                The Journal
              </Link>
              <Link
                href="/references"
                className="block px-6 py-3.5 font-lora text-parchment/70 hover:text-gold hover:bg-gold/5 transition-colors text-sm"
                onClick={() => setMobileMenuOpen(false)}
              >
                References
              </Link>
              <Link
                href="/about"
                className="block px-6 py-3.5 font-lora text-parchment/70 hover:text-gold hover:bg-gold/5 transition-colors text-sm"
                onClick={() => setMobileMenuOpen(false)}
              >
                Our Story
              </Link>
            </nav>
          </div>
        )}
      </header>

      {/* Spacer for fixed header */}
      <div className="h-[88px]" />

      {/* Cart Drawer */}
      <CartDrawer />
    </>
  )
}

/* ── Inline SVG icons (no external dep needed at build time) ── */
function ChevronDown({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
    </svg>
  )
}
function SearchIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <circle cx="11" cy="11" r="8" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35" />
    </svg>
  )
}
function ShoppingBagIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z" />
      <line x1="3" y1="6" x2="21" y2="6" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M16 10a4 4 0 01-8 0" />
    </svg>
  )
}
function XIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
    </svg>
  )
}
function MenuIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
    </svg>
  )
}
