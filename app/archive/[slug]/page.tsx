import type { Metadata } from 'next'
import Link from 'next/link'
import Image from 'next/image'
import { notFound } from 'next/navigation'
import { getAllArchiveItems, getArchiveItem } from '@/lib/archive'
import { formatFixed } from '@/lib/currency'

interface Props {
  params: { slug: string }
}

export async function generateStaticParams() {
  return getAllArchiveItems().map((i) => ({ slug: i.slug }))
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const item = getArchiveItem(params.slug)
  if (!item) return {}
  return {
    title: `${item.title} — Sold Archive | Faridunhill`,
    description: `Archived reference: ${item.title}. Maker, stampings, condition and realized price — part of the Faridunhill encyclopedia.`,
  }
}

export default function ArchiveItemPage({ params }: Props) {
  const item = getArchiveItem(params.slug)
  if (!item) notFound()

  const soldDate = item.soldAt ? new Date(item.soldAt) : null

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: item.title,
    image: item.images,
    sku: item.sku,
    brand: item.brand ? { '@type': 'Brand', name: item.brand } : undefined,
    offers: {
      '@type': 'Offer',
      availability: 'https://schema.org/SoldOut',
      priceCurrency: item.soldCurrency,
      ...(item.soldPrice !== null && { price: item.soldPrice }),
    },
  }

  return (
    <div className="min-h-screen bg-mahogany">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <div className="max-w-screen-xl mx-auto px-6 lg:px-12 py-10">
        <nav className="flex items-center gap-2 text-xs font-lora text-parchment/40 mb-8">
          <Link href="/" className="hover:text-gold transition-colors">Home</Link>
          <span>/</span>
          <Link href="/archive" className="hover:text-gold transition-colors">Sold Archive</Link>
          <span>/</span>
          <span className="text-parchment/60 line-clamp-1">{item.title}</span>
        </nav>

        <div className="grid lg:grid-cols-2 gap-12">
          <div>
            {item.images[0] && (
              <div className="relative aspect-square rounded-sm overflow-hidden gold-frame bg-mahogany-light">
                <Image
                  src={item.images[0]}
                  alt={item.title}
                  fill
                  priority
                  className="object-cover"
                  sizes="(max-width: 1024px) 100vw, 50vw"
                />
                <span className="absolute top-3 left-3 bg-mahogany/85 text-gold text-xs font-lora uppercase tracking-widest px-3 py-1.5 rounded-sm">
                  Sold
                </span>
              </div>
            )}
            {item.images.length > 1 && (
              <div className="flex gap-3 mt-3 flex-wrap">
                {item.images.slice(1).map((img, i) => (
                  <div key={i} className="relative w-20 h-20 rounded-sm overflow-hidden border border-gold/20">
                    <Image src={img} alt={`${item.title} view ${i + 2}`} fill className="object-cover" sizes="80px" />
                  </div>
                ))}
              </div>
            )}
          </div>

          <div>
            <p className="font-lora text-gold/70 text-xs uppercase tracking-widest mb-2">
              {item.brand || 'Unattributed'} · Encyclopedia Record
            </p>
            <h1 className="font-playfair font-bold text-parchment text-3xl lg:text-4xl leading-tight mb-5">
              {item.title}
            </h1>

            <div className="flex items-center gap-4 mb-8 font-lora text-sm">
              {item.soldPrice !== null && (
                <span className="text-gold text-xl font-playfair font-bold">
                  Realized {formatFixed(item.soldPrice, item.soldCurrency)}
                  <span className="text-parchment/40 text-sm font-lora font-normal ml-1.5">
                    {item.soldCurrency}
                  </span>
                </span>
              )}
              {soldDate && (
                <span className="text-parchment/40">
                  {soldDate.toLocaleDateString('en-GB', { year: 'numeric', month: 'long' })}
                </span>
              )}
            </div>

            <div className="font-lora text-parchment/70 leading-relaxed space-y-3 whitespace-pre-line">
              {item.body}
            </div>

            <div className="mt-10 border-t border-gold/20 pt-6">
              <p className="font-lora text-parchment/50 text-sm mb-4">
                Looking for a piece like this one?
              </p>
              <Link
                href={`/shop/estate-pipes`}
                className="inline-block font-lora text-gold text-sm uppercase tracking-widest hover:text-parchment transition-colors"
              >
                Browse the live collection →
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
