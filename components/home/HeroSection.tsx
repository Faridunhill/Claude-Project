import Image from 'next/image'
import Link from 'next/link'

export default function HeroSection() {
  return (
    <section className="relative w-full h-screen min-h-[700px] max-h-[1080px] overflow-hidden">
      {/* Background — swap this Unsplash URL for a real commissioned photo */}
      <Image
        src="https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920&q=85"
        alt="Victorian gentleman's study — mahogany desk, lit briar pipe, leather tobacco pouch, candlelight"
        fill
        priority
        className="object-cover object-center"
        sizes="100vw"
      />

      {/* Layered overlays — warm amber shadows frame the subject */}
      <div className="absolute inset-0 bg-gradient-to-r from-mahogany/95 via-mahogany/65 to-mahogany/30" />
      <div className="absolute inset-0 bg-gradient-to-t from-mahogany via-transparent to-mahogany/60" />
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-mahogany/80" />

      {/* Amber vignette */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse at 60% 40%, rgba(201,168,76,0.06) 0%, transparent 60%)',
        }}
      />

      {/* Content */}
      <div className="relative h-full flex items-center">
        <div className="max-w-screen-xl mx-auto px-6 lg:px-12 py-20">
          <div className="max-w-2xl">
            {/* Pre-headline ornament */}
            <div className="flex items-center gap-3 mb-8">
              <span className="h-px w-12 bg-gold/60" />
              <span className="font-fell italic text-gold text-sm tracking-widest">Fine Pipes &amp; Tobaccos</span>
              <span className="h-px w-12 bg-gold/60" />
            </div>

            {/* Main headline */}
            <h1 className="font-playfair font-black text-parchment leading-none tracking-tight mb-6"
              style={{ fontSize: 'clamp(2.8rem, 6vw, 5.5rem)' }}>
              Where Every Pipe<br />
              <em className="text-gold not-italic">Tells a Story</em>
            </h1>

            {/* Subheading */}
            <p className="font-lora text-parchment/75 leading-relaxed mb-10"
              style={{ fontSize: 'clamp(0.95rem, 1.5vw, 1.2rem)' }}>
              Purveyors of Fine Pipes, Tobaccos &amp; Gentleman's Accessories Since 2007.
              <br className="hidden sm:block" />
              Rooted in thirty years of collector knowledge and old-world craftsmanship.
            </p>

            {/* CTA row */}
            <div className="flex flex-wrap items-center gap-4">
              <Link
                href="/shop"
                className="btn-gold inline-flex items-center gap-2.5 px-8 py-4 rounded-sm text-sm uppercase tracking-widest"
              >
                Explore Our Collection
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/blog"
                className="btn-ghost inline-flex items-center gap-2.5 px-8 py-4 rounded-sm text-sm uppercase tracking-widest"
              >
                Read Our Journal
              </Link>
            </div>

            {/* Trust indicators */}
            <div className="flex flex-wrap items-center gap-6 mt-12 pt-8 border-t border-gold/15">
              {[
                { label: '30+ Years', sub: 'Collector Expertise' },
                { label: '2,400+', sub: 'Products Curated' },
                { label: 'Free Ship', sub: 'Orders over £75' },
              ].map((stat) => (
                <div key={stat.label} className="text-center">
                  <p className="font-playfair font-bold text-gold text-lg">{stat.label}</p>
                  <p className="font-lora text-parchment/50 text-xs tracking-wider uppercase">{stat.sub}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-gold/40">
        <span className="font-fell italic text-xs tracking-widest">Scroll</span>
        <div className="w-px h-10 bg-gradient-to-b from-gold/40 to-transparent" />
      </div>
    </section>
  )
}

function ArrowRight({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3" />
    </svg>
  )
}
