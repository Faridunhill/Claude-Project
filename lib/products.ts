import { createReader } from '@keystatic/core/reader'
import keystatic from '@/keystatic.config'
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
      department: e.entry.department ?? 'tobacco-pipes',
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
  const keystaticProducts = await fetchFromKeystatic()
  if (!keystaticProducts) return jsonProducts
  // Merge, not replace: JSON seed is the base catalog; Keystatic (hub-published)
  // entries augment it and override any seed product that shares a slug.
  const bySlug = new Map<string, Product>(jsonProducts.map((p) => [p.slug, p]))
  for (const p of keystaticProducts) bySlug.set(p.slug, p)
  return Array.from(bySlug.values())
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
