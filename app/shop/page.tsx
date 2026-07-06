import type { Metadata } from 'next'
import Link from 'next/link'
import Image from 'next/image'
import { departmentMeta } from '@/lib/products'

export const metadata: Metadata = {
  title: 'Shop All Departments',
  description: 'Browse all departments at Faridunhill — estate pipes, meerschaums, rare collectibles, leather bags, smoking accessories, and lighters.',
}

const deptImages: Record<string, string> = {
  'estate-pipes': 'https://i.etsystatic.com/34479460/r/il/d22f04/7660094618/il_fullxfull.7660094618_qvl4.jpg',
  'new-pipes': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80',
  'meerschaum': 'https://i.etsystatic.com/34479460/r/il/9ed80b/7771380885/il_fullxfull.7771380885_is59.jpg',
  'rare-collectible': 'https://i.etsystatic.com/34479460/r/il/df7987/7663292576/il_fullxfull.7663292576_kbvp.jpg',
  'leather-bags': 'https://i.etsystatic.com/34479460/r/il/010080/4097242757/il_fullxfull.4097242757_k0j5.jpg',
  'cigar-smoking-accessories': 'https://i.etsystatic.com/34479460/r/il/a3dec9/7743422566/il_fullxfull.7743422566_29ep.jpg',
  'lighters': 'https://i.etsystatic.com/34479460/r/il/c54c6c/7778612773/il_fullxfull.7778612773_o35w.jpg',
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
