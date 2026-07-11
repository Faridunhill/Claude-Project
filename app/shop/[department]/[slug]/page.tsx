import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import Image from 'next/image'
import Link from 'next/link'
import { getAllProducts, getProductBySlug, getRelatedProducts, departmentMeta } from '@/lib/products'
import AddToCartButton from '@/components/ui/AddToCartButton'

interface Props {
  params: { department: string; slug: string }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const product = await getProductBySlug(params.slug)
  if (!product) return {}
  return {
    title: product.name,
    description: product.description.slice(0, 160),
    openGraph: {
      title: `${product.name} | Faridunhill`,
      description: product.description.slice(0, 160),
      images: [{ url: product.images[0], width: 800, height: 800 }],
    },
  }
}

export async function generateStaticParams() {
  const products = await getAllProducts()
  return products.map((p) => ({
    department: p.department,
    slug: p.slug,
  }))
}

function StarRating({ rating, count }: { rating: number; count: number }) {
  return (
    <div className="flex items-center gap-2">
      <div className="flex gap-0.5">
        {Array.from({ length: 5 }).map((_, i) => (
          <svg
            key={i}
            className={`w-4 h-4 ${i < Math.floor(rating) ? 'text-gold' : 'text-parchment/20'}`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        ))}
      </div>
      <span className="font-lora text-parchment/50 text-sm">
        {rating} ({count} reviews)
      </span>
    </div>
  )
}

export default async function ProductPage({ params }: Props) {
  const product = await getProductBySlug(params.slug)
  if (!product || product.department !== params.department) notFound()

  const related = await getRelatedProducts(product, 4)
  const deptMeta = departmentMeta[product.department]

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: product.name,
    description: product.description,
    image: product.images,
    brand: { '@type': 'Brand', name: product.brand },
    sku: product.sku,
    offers: {
      '@type': 'Offer',
      price: product.price,
      priceCurrency: 'GBP',
      availability: product.inStock
        ? 'https://schema.org/InStock'
        : 'https://schema.org/OutOfStock',
      seller: { '@type': 'Organization', name: 'Faridunhill' },
    },
    // aggregateRating is only emitted when real reviews exist — fake review
    // markup with zero reviews is a search-engine policy violation
    ...(product.reviewCount > 0 && {
      aggregateRating: {
        '@type': 'AggregateRating',
        ratingValue: product.rating,
        reviewCount: product.reviewCount,
      },
    }),
  }

  return (
    <div className="min-h-screen bg-mahogany">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <div className="max-w-screen-xl mx-auto px-6 lg:px-12 py-10">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-xs font-lora text-parchment/40 mb-8">
          <Link href="/" className="hover:text-gold transition-colors">Home</Link>
          <span>/</span>
          <Link href="/shop" className="hover:text-gold transition-colors">Shop</Link>
          <span>/</span>
          <Link href={`/shop/${product.department}`} className="hover:text-gold transition-colors">
            {deptMeta?.name}
          </Link>
          <span>/</span>
          <span className="text-parchment/60 line-clamp-1">{product.name}</span>
        </nav>

        {/* Main product layout */}
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16">
          {/* Images */}
          <div>
            <div className="relative aspect-square rounded-sm overflow-hidden gold-frame bg-mahogany-light">
              <Image
                src={product.images[0]}
                alt={product.name}
                fill
                priority
                className="object-cover"
                sizes="(max-width: 1024px) 100vw, 50vw"
              />
              <div className="absolute top-3 right-3 text-gold/30 text-sm">✦</div>
            </div>
            {product.images.length > 1 && (
              <div className="flex gap-3 mt-3">
                {product.images.map((img, i) => (
                  <div key={i} className="relative w-20 h-20 rounded-sm overflow-hidden border border-gold/20">
                    <Image
                      src={img}
                      alt={`${product.name} view ${i + 1}`}
                      fill
                      className="object-cover"
                      sizes="80px"
                    />
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Details */}
          <div>
            <p className="font-lora text-gold/70 text-xs uppercase tracking-widest mb-2">
              {product.brand}
            </p>
            <h1 className="font-playfair font-bold text-parchment text-3xl lg:text-4xl leading-tight mb-4">
              {product.name}
            </h1>

            {product.reviewCount > 0 && (
              <StarRating rating={product.rating} count={product.reviewCount} />
            )}

            <div className="flex items-center gap-4 mt-5 mb-6">
              <span className="font-playfair font-bold text-gold text-3xl">
                £{product.price.toFixed(2)}
              </span>
              {product.originalPrice !== null && product.originalPrice !== undefined && (
                <span className="font-lora text-parchment/40 text-lg line-through">
                  £{product.originalPrice.toFixed(2)}
                </span>
              )}
              {product.inStock ? (
                <span className="font-lora text-sm text-hunter-light">● In Stock</span>
              ) : (
                <span className="font-lora text-sm text-red-400">● Out of Stock</span>
              )}
            </div>

            <div className="h-px bg-gold/15 mb-6" />

            <p className="font-lora text-parchment/80 leading-[1.9] text-[1.02rem] mb-8">
              {product.description}
            </p>

            {product.specs && (
              <div className="bg-mahogany-light rounded-sm p-5 border border-gold/15 mb-8">
                <h3 className="font-playfair font-semibold text-parchment text-sm uppercase tracking-widest mb-4">
                  Specifications
                </h3>
                <dl className="space-y-2">
                  {Object.entries(product.specs).map(([key, value]) => (
                    <div key={key} className="flex gap-3">
                      <dt className="font-lora text-parchment/45 text-sm w-28 flex-shrink-0 capitalize">
                        {key.replace(/([A-Z])/g, ' $1')}
                      </dt>
                      <dd className="font-lora text-parchment/80 text-sm">{value}</dd>
                    </div>
                  ))}
                </dl>
              </div>
            )}

            <div className="flex gap-3">
              <AddToCartButton product={product} className="flex-1 py-4 text-sm" />
            </div>

            <p className="font-lora text-parchment/35 text-xs mt-4 leading-relaxed">
              Free shipping on orders over $75. Age verification (21+) required for tobacco products.
              Estimated delivery 3–7 business days within the continental US.
            </p>

            <div className="flex flex-wrap gap-2 mt-6">
              {product.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-3 py-1 border border-gold/15 rounded-sm font-lora text-parchment/40 text-xs"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Related products */}
        {related.length > 0 && (
          <div className="mt-20 pt-12 border-t border-gold/15">
            <h2 className="font-playfair font-bold text-parchment text-2xl mb-8">
              You May Also Enjoy
            </h2>
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
              {related.map((rel) => (
                <Link
                  key={rel.id}
                  href={`/shop/${rel.department}/${rel.slug}`}
                  className="product-card group bg-mahogany-light rounded-sm gold-frame overflow-hidden block"
                >
                  <div className="relative aspect-square overflow-hidden">
                    <Image
                      src={rel.images[0]}
                      alt={rel.name}
                      fill
                      className="object-cover transition-transform duration-500 group-hover:scale-105"
                      sizes="25vw"
                    />
                  </div>
                  <div className="p-4">
                    <p className="font-lora text-gold/60 text-xs mb-1">{rel.brand}</p>
                    <p className="font-playfair font-semibold text-parchment text-sm line-clamp-2 group-hover:text-gold transition-colors">
                      {rel.name}
                    </p>
                    <p className="font-playfair font-bold text-gold mt-2">
                      £{rel.price.toFixed(2)}
                    </p>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
