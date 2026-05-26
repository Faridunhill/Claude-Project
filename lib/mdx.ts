import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'
import { createReader } from '@keystatic/core/reader'
import keystatic from '@/keystatic.config'

const BLOG_DIR = path.join(process.cwd(), 'content/blog')

export interface PostMeta {
  slug: string
  title: string
  author: string
  date: string
  category: string
  excerpt: string
  image: string
  tags: string[]
  readingTime?: string
}

export interface Post extends PostMeta {
  content: string
}

function calcReadingTime(text: string): string {
  const minutes = Math.ceil(text.split(/\s+/).length / 238)
  return `${minutes} min read`
}

function getReader() {
  return createReader(process.cwd(), keystatic)
}

async function fetchKeystaticPosts(): Promise<Post[] | null> {
  try {
    const reader = getReader()
    const entries = await reader.collections.posts.all()
    if (!entries.length) return null
    return entries.map((e) => ({
      slug: e.slug,
      title: e.entry.title,
      author: e.entry.author ?? 'The Faridunhill Editors',
      date: e.entry.publishedAt ?? '',
      category: e.entry.category ?? 'Pipe Culture',
      excerpt: e.entry.excerpt ?? '',
      image:
        e.entry.image ||
        'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=1200&q=85',
      tags: (e.entry.tags as string[]) ?? [],
      readingTime: calcReadingTime(e.entry.content ?? ''),
      content: e.entry.content ?? '',
    }))
  } catch (err) {
    console.error('Keystatic post read failed, using MDX fallback:', err)
    return null
  }
}

function getMdxSlugs(): string[] {
  if (!fs.existsSync(BLOG_DIR)) return []
  return fs
    .readdirSync(BLOG_DIR)
    .filter((f) => f.endsWith('.mdx') || f.endsWith('.md'))
    .map((f) => f.replace(/\.(mdx|md)$/, ''))
}

function getMdxPost(slug: string): Post | null {
  const mdxPath = path.join(BLOG_DIR, `${slug}.mdx`)
  const mdPath = path.join(BLOG_DIR, `${slug}.md`)
  const filePath = fs.existsSync(mdxPath) ? mdxPath : fs.existsSync(mdPath) ? mdPath : null
  if (!filePath) return null

  const raw = fs.readFileSync(filePath, 'utf8')
  const { data, content } = matter(raw)

  return {
    slug,
    title: data.title || '',
    author: data.author || 'The Faridunhill Editors',
    date: data.date || '',
    category: data.category || 'Pipe Culture',
    excerpt: data.excerpt || '',
    image: data.image || 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=1200&q=85',
    tags: data.tags || [],
    readingTime: calcReadingTime(content),
    content,
  }
}

export async function getAllPosts(): Promise<PostMeta[]> {
  const keystaticPosts = await fetchKeystaticPosts()
  if (keystaticPosts) return keystaticPosts.sort((a, b) => (b.date > a.date ? 1 : -1))

  return getMdxSlugs()
    .map(getMdxPost)
    .filter((p): p is Post => p !== null)
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
}

export async function getPostBySlug(slug: string): Promise<Post | null> {
  const keystaticPosts = await fetchKeystaticPosts()
  if (keystaticPosts) return keystaticPosts.find((p) => p.slug === slug) ?? null
  return getMdxPost(slug)
}

export async function getAllPostSlugs(): Promise<string[]> {
  const keystaticPosts = await fetchKeystaticPosts()
  if (keystaticPosts) return keystaticPosts.map((p) => p.slug)
  return getMdxSlugs()
}

export async function getRecentPosts(limit = 3): Promise<PostMeta[]> {
  return (await getAllPosts()).slice(0, limit)
}
