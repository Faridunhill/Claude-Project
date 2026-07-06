import { createReader } from '@keystatic/core/reader'
import keystatic from '@/keystatic.config'

export interface Product {
  id: string
  name: string
  brand: string
  slug: string
  department: string
  category: string
  price: number
  originalPrice: number | null
  sku: string
  images: string[]
  featured: boolean
  inStock: boolean
  rating: number
  reviewCount: number
  description: string
  tags: string[]
  specs?: Record<string, string>
  size?: string
  vitola?: string
  origin?: string
  wrapper?: string
  contents?: string[]
}


function getReader() {
  return createReader(process.cwd(), keystatic)
}

async function fetchFromKeystatic(): Promise<Product[] | null> {
  try {
    const reader = getReader()
    const entries = await reader.collections.products.all()
    if (!entries.length) return null
    return entries.map((e) => ({
      id: e.slug,
      name: e.entry.name ?? '',
      brand: e.entry.brand ?? '',
      slug: e.slug,
      department: e.entry.department ?? 'estate-pipes',
      category: e.entry.category ?? '',
      price: parseFloat((e.entry.price as string) ?? '0') || 0,
      originalPrice: e.entry.originalPrice ? parseFloat(e.entry.originalPrice as string) || null : null,
      sku: e.entry.sku ?? '',
      images: (e.entry.images as string[]) ?? [],
      featured: e.entry.featured ?? false,
      inStock: e.entry.inStock ?? true,
      rating: parseFloat((e.entry.rating as string) ?? '4.5') || 4.5,
      reviewCount: (e.entry.reviewCount as number) ?? 0,
      description: e.entry.description ?? '',
      tags: (e.entry.tags as string[]) ?? [],
      specs: e.entry.specs?.length
        ? Object.fromEntries(
            (e.entry.specs as Array<{ key: string; value: string }>).map((s) => [s.key, s.value])
          )
        : undefined,
      size: e.entry.size ?? undefined,
      vitola: e.entry.vitola ?? undefined,
      origin: e.entry.origin ?? undefined,
      wrapper: e.entry.wrapper ?? undefined,
      contents: (e.entry.contents as string[])?.length
        ? (e.entry.contents as string[])
        : undefined,
    }))
  } catch (err) {
    console.error('Keystatic product read failed, using JSON fallback:', err)
    return null
  }
}

export async function getAllProducts(): Promise<Product[]> {
  return (await fetchFromKeystatic()) ?? []
}

export async function getFeaturedProducts(): Promise<Product[]> {
  const products = await getAllProducts()
  return products.filter((p) => p.featured && p.inStock)
}

export async function getProductsByDepartment(department: string): Promise<Product[]> {
  const products = await getAllProducts()
  return products.filter((p) => p.department === department)
}

export async function getProductBySlug(slug: string): Promise<Product | undefined> {
  const products = await getAllProducts()
  return products.find((p) => p.slug === slug)
}

export async function getRelatedProducts(product: Product, limit = 4): Promise<Product[]> {
  const products = await getAllProducts()
  return products
    .filter(
      (p) =>
        p.id !== product.id &&
        (p.department === product.department || p.tags.some((t) => product.tags.includes(t))) &&
        p.inStock
    )
    .slice(0, limit)
}

export const departmentMeta: Record<string, { name: string; description: string }> = {
  'estate-pipes': {
    name: 'Estate Pipes',
    description:
      'Restored and original estate pipes from the great workshops of Europe and beyond — every pipe photographed exactly as it is.',
  },
  'new-pipes': {
    name: 'New Pipes',
    description:
      'Unsmoked, new-old-stock, and contemporary pipes — ready for their first bowl.',
  },
  meerschaum: {
    name: 'Meerschaum',
    description:
      'Hand-carved Turkish meerschaum — sultans, figurals, and classic shapes that color beautifully with every smoke.',
  },
  'rare-collectible': {
    name: 'Rare & Collectible',
    description:
      'Complete sets, rarities, and museum-grade pieces for the serious collector.',
  },
  'leather-bags': {
    name: 'Leather Bags & Cases',
    description:
      'Handcrafted in full-grain leather — pipe rolls, tobacco pouches, cigar cases, and travel companions built to last a lifetime.',
  },
  'cigar-smoking-accessories': {
    name: 'Cigar & Smoking Accessories',
    description:
      'Cutters, humidors, ashtrays, tampers, stands, and tools — the proper accoutrements of the smoking life.',
  },
  lighters: {
    name: 'Lighters & Matches',
    description:
      'Vintage petrol, jet, and table lighters — strike the proper flame, every time.',
  },
  sale: {
    name: 'Sale & Clearance',
    description: 'Exceptional value on fine stock — while supplies last.',
  },
}
