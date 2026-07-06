import Image from 'next/image'
import Link from 'next/link'
import { getFeaturedProducts } from '@/lib/products'
import { departmentMeta } from '@/lib/products'

export default async function NumberedShowcase() {
  const featured = (await getFeaturedProducts()).slice(0, 4)
  if (!featured.length) return null

  return (
    <section className="bg-[#0d0a07] py-24 md:py-32">
      <div className="mx-auto max-w-screen-xl px-6 lg:px-12">
        <div className="mb-16 text-center">
          <p className="font-fell italic text-gold/60 text-sm tracking-[0.3em] uppercase">
            Selected Pieces
          </p>
          <h2 className="font-playfair font-bold text-parchment text-4xl md:text-5xl mt-4">
            The Collection
          </h2>
          <p className="font-lora text-parchment/50 mt-4 max-w-xl mx-auto">
            Each piece is personally selected. If Farid would not smoke it himself, it does not
            appear here.
          </p>
        </div>

        <div className="space-y-20 md:space-y-28">
          {featured.map((product, i) => (
            <div
              key={product.id}
              className={`flex flex-col items-center gap-10 md:gap-16 md:flex-row ${
                i % 2 === 1 ? 'md:flex-row-reverse' : ''
              }`}
            >
              {/* Image */}
              <Link
                href={`/shop/${product.department}/${product.slug}`}
                className="group relative block aspect-square w-full max-w-md overflow-hidden bg-[#1a1410]"
              >
                <Image
                  src={product.images[0]}
                  alt={product.name}
                  fill
                  sizes="(max-width: 768px) 100vw, 40vw"
                  className="object-cover transition-transform duration-700 group-hover:scale-105"
                />
              </Link>

              {/* Copy */}
              <div className="w-full max-w-md text-center md:text-left">
                <p className="font-playfair text-gold/30 text-6xl md:text-7xl leading-none">
                  {String(i + 1).padStart(2, '0')}
                </p>
                <p className="font-lora text-gold/70 text-xs tracking-[0.25em] uppercase mt-6">
                  {departmentMeta[product.department]?.name ?? product.category}
                </p>
                <h3 className="font-playfair font-bold text-parchment text-2xl md:text-3xl mt-3 leading-snug">
                  {product.name}
                </h3>
                <p className="font-lora text-parchment/55 mt-4 leading-relaxed">
                  {product.description}
                </p>
                <div className="mt-6 flex items-center justify-center gap-6 md:justify-start">
                  <span className="font-playfair font-bold text-gold text-2xl">
                    £{product.price.toFixed(2)}
                  </span>
                  <Link
                    href={`/shop/${product.department}/${product.slug}`}
                    className="nav-link-underline font-lora text-parchment/70 text-xs tracking-[0.2em] uppercase hover:text-gold transition-colors"
                  >
                    View Piece
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-20 text-center">
          <Link
            href="/shop"
            className="inline-block border border-gold/60 px-10 py-4 font-lora text-gold text-xs tracking-[0.25em] uppercase transition-colors duration-300 hover:bg-gold hover:text-mahogany-dark"
          >
            View Entire Collection
          </Link>
        </div>
      </div>
    </section>
  )
}
