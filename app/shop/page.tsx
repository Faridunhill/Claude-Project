import type { Metadata } from 'next'
import Link from 'next/link'
import Image from 'next/image'
import { departmentMeta } from '@/lib/products'

export const metadata: Metadata = {
  title: 'Shop All Departments',
  description: 'Browse all departments at Faridunhill — tobacco pipes, pipe tobacco, cigars, leather bags, accessories, and more.',
}

const deptImages: Record<string, string> = {
  'tobacco-pipes': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80',
  'pipe-tobacco': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=600&q=80',
  'cigars': 'https://images.unsplash.com/photo-1551024601-bec78aea704b?w=600&q=80',
  'pipe-accessories': 'https://images.unsplash.com/photo-1585155770447-2f66e2a397b5?w=600&q=80',
  'cigar-accessories': 'https://images.unsplash.com/photo-1585155770447-2f66e2a397b5?w=600&q=80',
  'leather-bags': 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600&q=80',
  'vaping': 'https://images.unsplash.com/photo-1606760227091-3dd870d97f1d?w=600&q=80',
  'lighters': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=600&q=80',
  'gift-sets': 'https://images.unsplash.com/photo-1512909006721-3d6018887383?w=600&q=80',
  'sale': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=600&q=80',
}

export default function ShopIndexPage() {
  return (
    <div className="min-h-screen bg-mahogany">
      <div className="bg-mahogany-dark border-b border-gold/15 py-14 text-center">
        <span className="font-fell italic text-gold/70 text-sm tracking-widest">~ Browse ~</span>
        <h1 className="font-playfair font-bold text-parchment text-5xl mt-3">The Shop</h1>
        <p className="font-lora text-parchment/55 mt-3 max-w-lg mx-auto">
          Curated with the knowledge of thirty years of collecting. Everything we stock, we smoke.
        </p>
      </div>

      <div className="max-w-screen-xl mx-auto px-6 lg:px-12 py-14">
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {Object.entries(departmentMeta).map(([slug, meta]) => (
            <Link
              key={slug}
              href={`/shop/${slug}`}
              className="group relative aspect-[3/4] overflow-hidden rounded-sm gold-frame product-card block"
            >
              <Image
                src={deptImages[slug] || 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=600&q=80'}
                alt={meta.name}
                fill
                className="object-cover transition-transform duration-700 group-hover:scale-105"
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 25vw"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-mahogany/90 via-mahogany/40 to-transparent" />
              <div className="absolute bottom-0 left-0 right-0 p-5">
                <h2 className="font-playfair font-bold text-parchment text-lg group-hover:text-gold transition-colors">
                  {meta.name}
                </h2>
                <p className="font-lora text-parchment/55 text-sm mt-1 line-clamp-2 group-hover:text-parchment/75 transition-colors">
                  {meta.description}
                </p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
