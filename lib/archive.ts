import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'

export interface ArchiveItem {
  slug: string
  title: string
  sku: string
  brand: string
  department: string
  taxonomy: string
  soldAt: string
  soldChannel: string
  soldPrice: number | null
  images: string[]
  body: string
}

const ARCHIVE_DIR = path.join(process.cwd(), 'content', 'archive')

export function getAllArchiveItems(): ArchiveItem[] {
  if (!fs.existsSync(ARCHIVE_DIR)) return []
  return fs
    .readdirSync(ARCHIVE_DIR)
    .filter((f) => f.endsWith('.md'))
    .map((file) => {
      const raw = fs.readFileSync(path.join(ARCHIVE_DIR, file), 'utf-8')
      const { data, content } = matter(raw)
      return {
        slug: file.replace(/\.md$/, ''),
        title: (data.title as string) ?? '',
        sku: (data.sku as string) ?? '',
        brand: (data.brand as string) ?? '',
        department: (data.department as string) ?? 'pipes',
        taxonomy: (data.taxonomy as string) ?? '',
        soldAt: (data.soldAt as string) ?? '',
        soldChannel: (data.soldChannel as string) ?? '',
        soldPrice: typeof data.soldPrice === 'number' ? data.soldPrice : null,
        images: Array.isArray(data.images) ? (data.images as string[]) : [],
        body: content.trim(),
      }
    })
    .sort((a, b) => (b.soldAt || '').localeCompare(a.soldAt || ''))
}

export function getArchiveItem(slug: string): ArchiveItem | undefined {
  return getAllArchiveItems().find((i) => i.slug === slug)
}

export function getArchiveByBrand(brand: string): ArchiveItem[] {
  const needle = brand.toLowerCase()
  return getAllArchiveItems().filter((i) => i.brand.toLowerCase() === needle)
}
