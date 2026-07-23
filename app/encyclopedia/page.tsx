import type { Metadata } from 'next'
import Image from 'next/image'
import Link from 'next/link'
import { getAllEntries, ENCYCLOPEDIA_CATEGORIES } from '@/lib/encyclopedia'

export const metadata: Metadata = {
  title: 'The Encyclopedia',
  description:
    'Short presenter-led learning videos with a written entry for every topic — history, science, craft, and ideas.',
}

export default function EncyclopediaIndexPage() {
  const entries = getAllEntries()

  return (
    <div className="min-h-screen bg-mahogany">
      <div className="bg-mahogany-dark border-b border-gold/15 py-14 text-center px-6">
        <span className="font-fell italic text-gold/70 text-sm tracking-widest">~ Learn Something ~</span>
        <h1 className="font-playfair font-bold text-parchment text-5xl lg:text-6xl mt-3">
          The Encyclopedia
        </h1>
        <div className="ornament-divider max-w-xs mx-auto mt-5 mb-4">
          <span className="ornament-divider-symbol text-gold">❧</span>
        </div>
        <p className="font-lora text-parchment/55 max-w-xl mx-auto text-base">
          Short learning videos, each presented on camera and paired with a written entry you
          can read at your own pace.
        </p>
        <Link
          href="/encyclopedia/builder"
          className="inline-block mt-6 border border-gold/40 text-gold hover:bg-gold/10 font-playfair px-6 py-2.5 rounded-sm text-sm tracking-wide transition-colors"
        >
          Open the Builder →
        </Link>
      </div>

      <div className="max-w-screen-xl mx-auto px-6 lg:px-12 py-14">
        {entries.length === 0 ? (
          <p className="text-center font-lora text-parchment/40 py-20">
            No entries yet — create the first one in the Builder.
          </p>
        ) : (
          ENCYCLOPEDIA_CATEGORIES.filter((cat) => entries.some((e) => e.category === cat)).map(
            (cat) => (
              <div key={cat} className="mb-12">
                <h2 className="font-playfair text-gold/70 text-sm uppercase tracking-widest mb-5">
                  {cat}
                </h2>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {entries
                    .filter((e) => e.category === cat)
                    .map((entry) => (
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
                          {entry.videoUrl && (
                            <div className="absolute inset-0 flex items-center justify-center">
                              <span className="w-12 h-12 rounded-full bg-mahogany/70 border border-gold/50 flex items-center justify-center text-gold text-lg">
                                ▶
                              </span>
                            </div>
                          )}
                        </div>
                        <div className="p-5">
                          <h3 className="font-playfair font-semibold text-parchment text-base leading-snug group-hover:text-gold transition-colors line-clamp-2 mb-2">
                            {entry.title}
                          </h3>
                          <p className="font-lora text-parchment/55 text-sm line-clamp-2 leading-relaxed mb-3">
                            {entry.summary}
                          </p>
                          <p className="font-lora text-parchment/35 text-xs">
                            {entry.videoUrl ? 'Video + article' : 'Article'} · {entry.readingTime}
                          </p>
                        </div>
                      </Link>
                    ))}
                </div>
              </div>
            )
          )
        )}
      </div>
    </div>
  )
}
