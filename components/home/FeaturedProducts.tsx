import Image from 'next/image'
import Link from 'next/link'
import { getFeaturedProducts } from '@/lib/products'
import AddToCartButton from '@/components/ui/AddToCartButton'

export default async function FeaturedProducts() {
  const products = (await getFeaturedProducts()).slice(0, 8)

  return (
    <section className="bg-leather-texture py-24">
      <div className="max-w-screen-xl mx-auto px-6 lg:px-12">
        {/* Header */}
        <div className="flex items-end justify-between mb-10 gap-4 flex-wrap">
          <div>
            <span className="font-fell italic text-gold/70 text-sm tracking-widest">~ Curated Selection ~</span>
            <h2 className="font-playfair font-bold text-parchment text-4xl mt-2">
              Featured Products
            </h2>
          </div>
          <Link href="/shop" className="btn-ghost px-6 py-2.5 rounded-sm text-sm tracking-widest uppercase">
            View All →
          </Link>
        </div>

        {/* Horizontal scroll row */}
        <div className="flex gap-5 overflow-x-auto pb-4 snap-x snap-mandatory scrollbar-thin"
          style={{ scrollbarColor: '#3D2317 #1A0E09' }}>
          {products.map((product) => (
            <div
              key={product.id}
              className="product-card flex-none w-64 snap-start bg-mahogany-light rounded-sm gold-frame overflow-hidden group"
            >
              {/* Image */}
              <Link href={`/shop/${product.department}/${product.slug}`} className="block relative aspect-square overflow-hidden">
                <Image
                  src={product.images[0]}
                  alt={product.name}
                  fill
                  className="object-cover transition-transform duration-500 group-hover:scale-105"
                  sizes="256px"
                />
                {/* Out of stock overlay */}
                {!product.inStock && (
                  <div className="absolute inset-0 bg-mahogany/70 flex items-center justify-center">
                    <span className="font-playfair text-gold text-sm uppercase tracking-widest">Sold Out</span>
                  </div>
                )}
                {/* Sale badge */}
                {product.originalPrice && (
                  <div className="absolute top-3 left-3 bg-burgundy px-2.5 py-1 rounded-sm">
                    <span className="font-playfair text-parchment text-xs font-bold uppercase tracking-wide">
                      Sale
                    </span>
                  </div>
                )}
                {/* Corner ornament */}
                <div className="absolute top-2 right-2 text-gold/30 text-xs">✦</div>
              </Link>

              {/* Info */}
              <div className="p-4">
                <p className="font-lora text-gold/60 text-xs uppercase tracking-widest mb-1">{product.brand}</p>
                <Link href={`/shop/${product.department}/${product.slug}`}>
                  <h3 className="font-playfair font-semibold text-parchment text-sm leading-snug hover:text-gold transition-colors line-clamp-2 mb-2">
                    {product.name}
                  </h3>
                </Link>

                {/* Stars */}
                <div className="flex items-center gap-1 mb-3">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <svg
                      key={i}
                      className={`w-3 h-3 ${i < Math.floor(product.rating) ? 'text-gold' : 'text-parchment/20'}`}
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                  <span className="text-parchment/40 text-xs ml-1">({product.reviewCount})</span>
                </div>

                {/* Price row */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-playfair font-bold text-gold text-base">
                      £{product.price.toFixed(2)}
                    </span>
                    {product.originalPrice && (
                      <span className="font-lora text-parchment/40 text-xs line-through">
                        £{product.originalPrice.toFixed(2)}
                      </span>
                    )}
                  </div>
                </div>

                <AddToCartButton product={product} className="w-full mt-3" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
