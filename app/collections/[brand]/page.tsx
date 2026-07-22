import type { Metadata } from 'next'
import Link from 'next/link'
import Image from 'next/image'
import { notFound } from 'next/navigation'
import { getAllProducts } from '@/lib/products'
import { getAllArchiveItems } from '@/lib/archive'

interface Props {
  params: { brand: string }
}

function brandSlug(brand: string): string {
  return brand.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
}

async function getBrands(): Promise<Map<string, string>> {
  const products = await getAllProducts()
  const archive = getAllArchiveItems()
  const map = new Map<string, string>()
  for (const p of products) if (p.brand) map.set(brandSlug(p.brand), p.brand)
  for (const a of archive) if (a.brand) map.set(brandSlug(a.brand), a.brand)
  return map
}

export async function generateStaticParams() {
  const brands = await getBrands()
  return Array.from(brands.keys()).map((brand) => ({ brand }))
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const brands = await getBrands()
  const name = brands.get(params.brand)
  if (!name) return {}
  return {
    title: `${name} — Collector Hub | Faridunhill`,
    description: `${name} pipes at Faridunhill: pieces in stock now, plus our permanent sold archive of ${name} — shapes, stampings, and realized prices for collectors.`,
  }
}

export default async function BrandHubPage({ params }: Props) {
  const brands = await getBrands()
  const name = brands.get(params.brand)
  if (!name) notFound()

  const live = (await getAllProducts()).filter(
    (p) => p.brand && brandSlug(p.brand) === params.brand && p.inStock
  )
  const sold = getAllArchiveItems().filter(
    (a) => a.brand && brandSlug(a.brand) === params.brand
  )

  return (
    <div className="min-h-screen bg-mahogany">
      <div className="max-w-screen-xl mx-auto px-6 lg:px-12 py-14">
        <p className="font-lora text-gold/70 text-xs uppercase tracking-widest mb-3">
          Collector Hub
        </p>
        <h1 className="font-playfair font-bold text-parchment text-4xl mb-4">{name}</h1>
        <p className="font-lora text-parchment/60 max-w-2xl mb-12">
          Every {name} piece that passes through the collection is documented here —
          what is available now, and what has sold, with stampings and realized prices
          kept as a permanent collector reference.
        </p>

        <h2 className="font-playfair text-parchment text-2xl mb-6">
          In the shop now <span className="text-parchment/40 text-base">({live.length})</span>
        </h2>
        {live.length === 0 ? (
          <p className="font-lora text-parchment/40 italic mb-12">
            Nothing at the moment — new estates arrive weekly.
          </p>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mb-14">
            {live.map((p) => (
              <Link
                key={p.slug}
                href={`/shop/${p.department}/${p.slug}`}
                className="group block bg-mahogany-light rounded-sm overflow-hidden border border-gold/15 hover:border-gold/40 transition-colors"
              >
                <div className="relative aspect-square">
                  {p.images[0] && (
                    <Image src={p.images[0]} alt={p.name} fill className="object-cover" sizes="(max-width: 768px) 50vw, 25vw" />
                  )}
                </div>
                <div className="p-3">
                  <h3 className="font-playfair text-parchment text-sm leading-snug line-clamp-2 mb-1">{p.name}</h3>
                  <p className="font-lora text-gold text-sm font-bold">£{p.price.toFixed(2)}</p>
                </div>
              </Link>
            ))}
          </div>
        )}

        <h2 className="font-playfair text-parchment text-2xl mb-6">
          From the archive <span className="text-parchment/40 text-base">({sold.length})</span>
        </h2>
        {sold.length === 0 ? (
          <p className="font-lora text-parchment/40 italic">
            The {name} archive opens with the first sale.
          </p>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {sold.map((a) => (
              <Link
                key={a.slug}
                href={`/archive/${a.slug}`}
                className="group block bg-mahogany-light rounded-sm overflow-hidden border border-gold/10 hover:border-gold/30 transition-colors"
              >
                <div className="relative aspect-square">
                  {a.images[0] && (
                    <Image src={a.images[0]} alt={a.title} fill className="object-cover opacity-70 group-hover:opacity-90 transition-opacity" sizes="(max-width: 768px) 50vw, 25vw" />
                  )}
                  <span className="absolute top-2 left-2 bg-mahogany/80 text-gold/80 text-[10px] font-lora uppercase tracking-widest px-2 py-1 rounded-sm">
                    Sold
                  </span>
                </div>
                <div className="p-3">
                  <h3 className="font-playfair text-parchment/80 text-sm leading-snug line-clamp-2 mb-1">{a.title}</h3>
                  {a.soldPrice !== null && (
                    <p className="font-lora text-parchment/40 text-xs">Realized £{a.soldPrice.toFixed(2)}</p>
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
