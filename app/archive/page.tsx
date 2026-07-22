import type { Metadata } from 'next'
import Link from 'next/link'
import Image from 'next/image'
import { getAllArchiveItems } from '@/lib/archive'

export const metadata: Metadata = {
  title: 'The Encyclopedia — Sold Archive | Faridunhill',
  description:
    'A permanent record of every piece that has passed through the Faridunhill collection — makers, shapes, stampings, and realized prices, kept as a reference for collectors.',
}

export default function ArchivePage() {
  const items = getAllArchiveItems()

  return (
    <div className="min-h-screen bg-mahogany">
      <div className="max-w-screen-xl mx-auto px-6 lg:px-12 py-14">
        <p className="font-lora text-gold/70 text-xs uppercase tracking-widest mb-3">
          The Encyclopedia
        </p>
        <h1 className="font-playfair font-bold text-parchment text-4xl mb-4">Sold Archive</h1>
        <p className="font-lora text-parchment/60 max-w-2xl mb-12">
          Every piece that finds its home stays documented here — maker, shape, stampings,
          condition, and realized price. A permanent reference for collectors researching
          what things are, and what they bring.
        </p>

        {items.length === 0 ? (
          <p className="font-lora text-parchment/40 italic">
            The archive opens with the first sale. Check back soon.
          </p>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {items.map((item) => (
              <Link
                key={item.slug}
                href={`/archive/${item.slug}`}
                className="group block bg-mahogany-light rounded-sm overflow-hidden border border-gold/15 hover:border-gold/40 transition-colors"
              >
                <div className="relative aspect-square">
                  {item.images[0] && (
                    <Image
                      src={item.images[0]}
                      alt={item.title}
                      fill
                      className="object-cover opacity-80 group-hover:opacity-100 transition-opacity"
                      sizes="(max-width: 768px) 50vw, 25vw"
                    />
                  )}
                  <span className="absolute top-2 left-2 bg-mahogany/80 text-gold/80 text-[10px] font-lora uppercase tracking-widest px-2 py-1 rounded-sm">
                    Sold
                  </span>
                </div>
                <div className="p-3">
                  <p className="font-lora text-gold/60 text-[10px] uppercase tracking-widest mb-1">
                    {item.brand || 'Unattributed'}
                  </p>
                  <h2 className="font-playfair text-parchment text-sm leading-snug line-clamp-2">
                    {item.title}
                  </h2>
                  {item.soldPrice !== null && (
                    <p className="font-lora text-parchment/40 text-xs mt-2">
                      Realized £{item.soldPrice.toFixed(2)}
                    </p>
                  )}
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
