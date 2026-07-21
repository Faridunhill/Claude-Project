import type { Metadata } from 'next'
import Image from 'next/image'
import Link from 'next/link'
import { getAllEntries } from '@/lib/encyclopedia'

export const metadata: Metadata = {
  title: 'The Faridunhill Pipe Encyclopedia',
  description:
    'Brand dating guides, nomenclature references, and collector fundamentals — built on thirty-five years of pipe knowledge. Home of the free Pipe Passport identification service.',
}

export default function EncyclopediaPage() {
  const entries = getAllEntries()

  return (
    <div className="min-h-screen bg-mahogany">
      {/* Header */}
      <div className="bg-mahogany-dark border-b border-gold/15 py-14 text-center">
        <span className="font-fell italic text-gold/70 text-sm tracking-widest">~ The Reference Library ~</span>
        <h1 className="font-playfair font-bold text-parchment text-5xl lg:text-6xl mt-3">
          The Pipe Encyclopedia
        </h1>
        <div className="ornament-divider max-w-xs mx-auto mt-5 mb-4">
          <span className="ornament-divider-symbol text-gold">❧</span>
        </div>
        <p className="font-lora text-parchment/55 max-w-xl mx-auto text-base">
          Brand dating guides, nomenclature references, and collector fundamentals — thirty-five
          years of accumulated pipe knowledge, published for every collector to use.
        </p>
      </div>

      <div className="max-w-screen-xl mx-auto px-6 lg:px-12 py-14">
        {/* Pipe Passport feature banner */}
        <Link
          href="/encyclopedia/pipe-passport"
          className="group block rounded-sm gold-frame bg-mahogany-light overflow-hidden mb-14 product-card"
        >
          <div className="grid lg:grid-cols-5">
            <div className="lg:col-span-3 p-8 lg:p-12 flex flex-col justify-center">
              <span className="inline-block self-start bg-gold text-mahogany font-playfair font-bold text-[11px] uppercase tracking-widest px-3 py-1 rounded-sm mb-5">
                New — Free for Collectors
              </span>
              <h2 className="font-playfair font-bold text-parchment text-3xl lg:text-4xl leading-tight group-hover:text-gold transition-colors mb-4">
                The Pipe Passport
              </h2>
              <p className="font-lora text-parchment/65 leading-relaxed mb-6 max-w-xl">
                Six photographs in — a full identification and dating assessment out, in minutes.
                Our automated analysis reads the stamping, weighs the shape and finish against
                reference knowledge, and issues your pipe its own passport with a unique reference
                number. Free, instant, for any collector.
              </p>
              <span className="btn-gold self-start px-8 py-3.5 rounded-sm font-playfair font-bold text-sm tracking-widest uppercase">
                Identify My Pipe →
              </span>
            </div>
            <div className="lg:col-span-2 relative min-h-[220px]">
              <Image
                src="https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=1200&q=85"
                alt="Estate pipe awaiting identification"
                fill
                className="object-cover transition-transform duration-700 group-hover:scale-105"
                sizes="(max-width: 1024px) 100vw, 40vw"
              />
              <div className="absolute inset-0 bg-gradient-to-r from-mahogany-light/60 to-transparent" />
            </div>
          </div>
        </Link>

        {/* Entries */}
        <h2 className="font-playfair font-bold text-parchment text-2xl mb-6">Reference Articles</h2>
        {entries.length === 0 ? (
          <p className="text-center font-lora text-parchment/40 py-20">Entries coming soon.</p>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {entries.map((entry) => (
              <Link
                key={entry.slug}
                href={`/encyclopedia/${entry.slug}`}
                className="group block bg-mahogany-light rounded-sm gold-frame overflow-hidden product-card"
              >
                <div className="relative aspect-[16/9] overflow-hidden">
                  <Image
                    src={entry.image}
                    alt={entry.title}
                    fill
                    className="object-cover transition-transform duration-500 group-hover:scale-105"
                    sizes="(max-width: 768px) 100vw, 33vw"
                  />
                </div>
                <div className="p-5">
                  <p className="font-lora text-gold/70 text-xs uppercase tracking-widest mb-2">{entry.category}</p>
                  <h3 className="font-playfair font-semibold text-parchment text-base leading-snug group-hover:text-gold transition-colors line-clamp-2 mb-2">
                    {entry.title}
                  </h3>
                  <p className="font-lora text-parchment/55 text-sm line-clamp-3 leading-relaxed">{entry.excerpt}</p>
                </div>
              </Link>
            ))}
          </div>
        )}

        {/* Contribute note */}
        <div className="mt-14 p-8 bg-mahogany-light rounded-sm border border-gold/10 text-center">
          <p className="font-fell italic text-parchment/60 text-lg mb-2">
            &ldquo;The encyclopedia grows with every pipe identified.&rdquo;
          </p>
          <p className="font-lora text-parchment/40 text-sm">
            Every Pipe Passport submission strengthens the reference collection behind these pages.
          </p>
        </div>
      </div>
    </div>
  )
}
