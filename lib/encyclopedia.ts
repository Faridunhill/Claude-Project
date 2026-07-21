import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'

const ENCYCLOPEDIA_DIR = path.join(process.cwd(), 'content/encyclopedia')

export interface EncyclopediaEntryMeta {
  slug: string
  title: string
  category: string
  excerpt: string
  image: string
  updated: string
}

export interface EncyclopediaEntry extends EncyclopediaEntryMeta {
  content: string
}

function getSlugs(): string[] {
  if (!fs.existsSync(ENCYCLOPEDIA_DIR)) return []
  return fs
    .readdirSync(ENCYCLOPEDIA_DIR)
    .filter((f) => f.endsWith('.mdx') || f.endsWith('.md'))
    .map((f) => f.replace(/\.(mdx|md)$/, ''))
}

export function getEntryBySlug(slug: string): EncyclopediaEntry | null {
  const mdxPath = path.join(ENCYCLOPEDIA_DIR, `${slug}.mdx`)
  const mdPath = path.join(ENCYCLOPEDIA_DIR, `${slug}.md`)
  const filePath = fs.existsSync(mdxPath) ? mdxPath : fs.existsSync(mdPath) ? mdPath : null
  if (!filePath) return null

  const raw = fs.readFileSync(filePath, 'utf8')
  const { data, content } = matter(raw)

  return {
    slug,
    title: data.title || '',
    category: data.category || 'Reference',
    excerpt: data.excerpt || '',
    image: data.image || 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=1200&q=85',
    updated: data.updated || '',
    content,
  }
}

export function getAllEntries(): EncyclopediaEntryMeta[] {
  return getSlugs()
    .map(getEntryBySlug)
    .filter((e): e is EncyclopediaEntry => e !== null)
    .sort((a, b) => a.title.localeCompare(b.title))
}

export function getAllEntrySlugs(): string[] {
  return getSlugs()
}
