import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import Image from 'next/image'
import Link from 'next/link'
import { getProductsByDepartment, departmentMeta } from '@/lib/products'
import AddToCartButton from '@/components/ui/AddToCartButton'

interface Props {
  params: { department: string }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const meta = departmentMeta[params.department]
  if (!meta) return {}
  return {
    title: meta.name,
    description: meta.description,
  }
}

export async function generateStaticParams() {
  return Object.keys(departmentMeta).map((d) => ({ department: d }))
}

export default async function DepartmentPage({ params }: Props) {
  const meta = departmentMeta[params.department]
  if (!meta) notFound()

  const products = await getProductsByDepartment(params.department)

  return (
    <div className="min-h-screen bg-mahogany">
      {/* Department hero */}
      <div className="bg-mahogany-dark border-b border-gold/15 py-14">
        <div className="max-w-screen-xl mx-auto px-6 lg:px-12">
          {/* Breadcrumb */}
          <nav className="flex items-center gap-2 text-xs font-lora text-parchment/40 mb-6">
            <Link href="/" className="hover:text-gold transition-colors">Home</Link>
            <span>/</span>
            <Link href="/shop" className="hover:text-gold transition-colors">Shop</Link>
            <span>/</span>
            <span className="text-parchment/70">{meta.name}</span>
          </nav>

          <span className="font-fell italic text-gold/70 text-sm tracking-widest">~ Department ~</span>
          <h1 className="font-playfair font-bold text-parchment text-4xl lg:text-5xl mt-2 mb-4">
            {meta.name}
          </h1>
          <p className="font-lora text-parchment/60 text-base max-w-2xl leading-relaxed">
            {meta.description}
          </p>
        </div>
      </div>

      {/* Product grid */}
      <div className="max-w-screen-xl mx-auto px-6 lg:px-12 py-14">
        {products.length === 0 ? (
          <div className="text-center py-20">
            <p className="font-playfair text-parchment/50 text-2xl mb-3">Coming Soon</p>
            <p className="font-lora text-parchment/35 max-w-md mx-auto">
              We are currently curating our selection for this department. Check back soon, or{' '}
              <Link href="/contact" className="text-gold hover:underline">contact us</Link> to enquire about specific items.
            </p>
          </div>
        ) : (
          <>
            <p className="font-lora text-parchment/40 text-sm mb-8">
              Showing {products.length} {products.length === 1 ? 'product' : 'products'}
            </p>

            <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
              {products.map((product) => (
                <div key={product.id} className="product-card bg-mahogany-light rounded-sm gold-frame overflow-hidden group">
                  {/* Image */}
                  <Link href={`/shop/${product.department}/${product.slug}`} className="block relative aspect-square overflow-hidden">
                    <Image
                      src={product.images[0]}
                      alt={product.name}
                      fill
                      className="object-cover transition-transform duration-500 group-hover:scale-105"
                      sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 25vw"
                    />
                    {!product.inStock && (
                      <div className="absolute inset-0 bg-mahogany/70 flex items-center justify-center">
                        <span className="font-playfair text-gold text-sm uppercase tracking-widest">Sold Out</span>
                      </div>
                    )}
                    {product.originalPrice && (
                      <div className="absolute top-3 left-3 bg-red-900 px-2.5 py-0.5 rounded-sm">
                        <span className="font-playfair text-parchment text-xs font-bold uppercase tracking-wide">Sale</span>
                      </div>
                    )}
                    <div className="absolute top-2 right-2 text-gold/30 text-xs">✦</div>
                  </Link>

                  {/* Info */}
                  <div className="p-4">
                    <p className="font-lora text-gold/60 text-xs uppercase tracking-widest mb-1">{product.brand}</p>
                    <Link href={`/shop/${product.department}/${product.slug}`}>
                      <h2 className="font-playfair font-semibold text-parchment text-sm leading-snug hover:text-gold transition-colors line-clamp-2 mb-3">
                        {product.name}
                      </h2>
                    </Link>

                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <span className="font-playfair font-bold text-gold">£{product.price.toFixed(2)}</span>
                        {product.originalPrice && (
                          <span className="font-lora text-parchment/35 text-xs line-through">£{product.originalPrice.toFixed(2)}</span>
                        )}
                      </div>
                      <span className="font-lora text-parchment/35 text-xs">★ {product.rating}</span>
                    </div>

                    <AddToCartButton product={product} className="w-full" />
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
