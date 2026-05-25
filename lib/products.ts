import { sanityClient, hasSanity } from '@/lib/sanity'
import pipesData from '@/data/products/pipes.json'
import tobaccoData from '@/data/products/tobacco.json'
import cigarsData from '@/data/products/cigars.json'
import leatherData from '@/data/products/leather-bags.json'
import giftData from '@/data/products/gift-sets.json'
import pipeAccData from '@/data/products/pipe-accessories.json'
import cigarAccData from '@/data/products/cigar-accessories.json'
import vapingData from '@/data/products/vaping.json'
import lightersData from '@/data/products/lighters.json'

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

const jsonProducts: Product[] = [
  ...pipesData,
  ...tobaccoData,
  ...cigarsData,
  ...leatherData,
  ...giftData,
  ...pipeAccData,
  ...cigarAccData,
  ...vapingData,
  ...lightersData,
] as Product[]

const PRODUCTS_QUERY = `*[_type == "product"] {
  "id": _id,
  name,
  brand,
  "slug": slug.current,
  department,
  category,
  price,
  originalPrice,
  sku,
  "images": images[].asset->url,
  featured,
  inStock,
  rating,
  reviewCount,
  description,
  tags,
  "specs": specs[]{key, value},
  size,
  vitola,
  origin,
  wrapper,
  contents
}`

interface SanityProduct {
  id: string
  name: string
  brand: string
  slug: string
  department: string
  category: string
  price: number
  originalPrice?: number
  sku: string
  images: string[]
  featured: boolean
  inStock: boolean
  rating: number
  reviewCount: number
  description: string
  tags: string[]
  specs?: Array<{ key: string; value: string }>
  size?: string
  vitola?: string
  origin?: string
  wrapper?: string
  contents?: string[]
}

function mapSanityProduct(doc: SanityProduct): Product {
  return {
    ...doc,
    originalPrice: doc.originalPrice ?? null,
    specs: doc.specs
      ? Object.fromEntries(doc.specs.map((s) => [s.key, s.value]))
      : undefined,
  }
}

async function fetchFromSanity(): Promise<Product[] | null> {
  if (!hasSanity || !sanityClient) return null
  try {
    const docs = await sanityClient.fetch<SanityProduct[]>(PRODUCTS_QUERY)
    if (docs && docs.length > 0) return docs.map(mapSanityProduct)
  } catch (err) {
    console.error('Sanity product fetch failed, using JSON fallback:', err)
  }
  return null
}

export async function getAllProducts(): Promise<Product[]> {
  return (await fetchFromSanity()) ?? jsonProducts
}

export async function getFeaturedProducts(): Promise<Product[]> {
  const products = (await fetchFromSanity()) ?? jsonProducts
  return products.filter((p) => p.featured && p.inStock)
}

export async function getProductsByDepartment(department: string): Promise<Product[]> {
  const products = (await fetchFromSanity()) ?? jsonProducts
  return products.filter((p) => p.department === department)
}

export async function getProductBySlug(slug: string): Promise<Product | undefined> {
  const products = (await fetchFromSanity()) ?? jsonProducts
  return products.find((p) => p.slug === slug)
}

export async function getRelatedProducts(product: Product, limit = 4): Promise<Product[]> {
  const products = (await fetchFromSanity()) ?? jsonProducts
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
  'tobacco-pipes': {
    name: 'Tobacco Pipes',
    description:
      'Estate finds, classic briars, hand-carved meerschaums, and American corncobs — every pipe a lifetime companion.',
  },
  'pipe-tobacco': {
    name: 'Pipe Tobacco',
    description:
      'Virginia, Burley, Latakia, aromatic blends, and bulk tobaccos, chosen by smokers for smokers.',
  },
  cigars: {
    name: 'Cigars',
    description:
      'Premium hand-rolled cigars, curated bundles, and samplers from the finest growing regions in the world.',
  },
  'pipe-accessories': {
    name: 'Pipe Accessories',
    description:
      'Tools, cleaners, filters, stands, racks, and pouches — everything the discerning pipe man requires.',
  },
  'cigar-accessories': {
    name: 'Cigar Accessories',
    description:
      'Cutters, lighters, humidors, ashtrays, and travel cases for the serious cigar aficionado.',
  },
  'leather-bags': {
    name: 'Leather Bags & Cases',
    description:
      'Handcrafted in full-grain leather — pipe rolls, cigar cases, and travel companions built to last a lifetime.',
  },
  vaping: {
    name: 'Vaping & E-Liquids',
    description:
      'Modern vapor devices and e-liquids, curated with the same care as our traditional tobaccos.',
  },
  lighters: {
    name: 'Lighters & Matches',
    description:
      'Pipe lighters, torch lighters, cedar spills, and matchbooks — strike the proper flame, every time.',
  },
  'gift-sets': {
    name: 'Gift Sets & Samplers',
    description:
      'Curated collections for the beginner and the collector, beautifully presented for any occasion.',
  },
  sale: {
    name: 'Sale & Clearance',
    description: 'Exceptional value on fine stock — while supplies last.',
  },
}
