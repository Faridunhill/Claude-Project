import type { Metadata } from 'next'
import Link from 'next/link'
import { getAllCabinets } from '@/lib/dating'

export const metadata: Metadata = {
  title: 'Pipe Dating Directory',
  description:
    'The collector\'s identification system — date and identify an estate pipe from the evidence on the pipe itself: country stamps, silver hallmarks, patent numbers, and logo forms.',
}

export default async function DatingIndexPage() {
  const cabinets = await getAllCabinets()

  return (
    <div className="min-h-screen bg-mahogany">
      {/* Hero */}
      <div className="bg-mahogany-dark border-b border-gold/15 py-14">
        <div className="max-w-screen-xl mx-auto px-6 lg:px-12">
          <nav className="flex items-center gap-2 text-xs font-lora text-parchment/40 mb-6">
            <Link href="/" className="hover:text-gold transition-colors">Home</Link>
            <span>/</span>
            <span className="text-parchment/70">Dating Directory</span>
          </nav>

          <span className="font-fell italic text-gold/70 text-sm tracking-widest">
            ~ The Collector&apos;s Identification System ~
          </span>
          <h1 className="font-playfair font-bold text-parchment text-4xl lg:text-5xl mt-2 mb-4">
            Pipe Dating Directory
          </h1>
          <p className="font-lora text-parchment/60 text-base max-w-2xl leading-relaxed">
            Date and identify an estate pipe from the evidence on the pipe itself.
            Pick a maker&apos;s cabinet, read straight down the markers — country
            stamp, silver hallmark, patent number, logo form — and walk away with a
            defensible date in a single pass.
          </p>
        </div>
      </div>

      {/* Cabinets */}
      <div className="max-w-screen-xl mx-auto px-6 lg:px-12 py-14">
        {cabinets.length === 0 ? (
          <div className="text-center py-20">
            <p className="font-playfair text-parchment/50 text-2xl mb-3">Cabinets Coming Soon</p>
            <p className="font-lora text-parchment/35 max-w-md mx-auto">
              The first maker cabinets are being assembled.
            </p>
          </div>
        ) : (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {cabinets.map((c) => (
              <Link
                key={c.maker}
                href={`/dating/${c.maker}`}
                className="group block rounded-lg border border-gold/15 bg-mahogany-light/40 p-6 transition-colors hover:border-gold/40 hover:bg-mahogany-light/60"
              >
                <div className="flex items-baseline justify-between gap-3">
                  <h2 className="font-playfair text-parchment text-2xl group-hover:text-gold transition-colors">
                    {c.displayName}
                  </h2>
                  <span className="font-lora text-xs text-parchment/40 whitespace-nowrap">
                    {c.founded && `est. ${c.founded}`}
                  </span>
                </div>
                {c.country && (
                  <p className="font-fell italic text-gold/60 text-sm mt-1">{c.country}</p>
                )}
                <p className="font-lora text-parchment/55 text-sm mt-3 leading-relaxed line-clamp-4">
                  {c.summary}
                </p>
                <p className="font-lora text-xs text-parchment/40 mt-4">
                  {c.markers.length} marker{c.markers.length === 1 ? '' : 's'} ·{' '}
                  <span className="text-gold/70 group-hover:text-gold">Open cabinet →</span>
                </p>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
