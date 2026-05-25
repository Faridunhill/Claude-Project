import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'

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

export function getAllPostSlugs(): string[] {
  if (!fs.existsSync(BLOG_DIR)) return []
  return fs
    .readdirSync(BLOG_DIR)
    .filter((f) => f.endsWith('.mdx') || f.endsWith('.md'))
    .map((f) => f.replace(/\.(mdx|md)$/, ''))
}

export function getPostBySlug(slug: string): Post | null {
  const mdxPath = path.join(BLOG_DIR, `${slug}.mdx`)
  const mdPath = path.join(BLOG_DIR, `${slug}.md`)
  const filePath = fs.existsSync(mdxPath) ? mdxPath : fs.existsSync(mdPath) ? mdPath : null
  if (!filePath) return null

  const raw = fs.readFileSync(filePath, 'utf8')
  const { data, content } = matter(raw)
  const wordCount = content.split(/\s+/).length
  const minutes = Math.ceil(wordCount / 238)

  return {
    slug,
    title: data.title || '',
    author: data.author || 'The Faridunhill Editors',
    date: data.date || '',
    category: data.category || 'Pipe Culture',
    excerpt: data.excerpt || '',
    image: data.image || 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=1200&q=85',
    tags: data.tags || [],
    readingTime: `${minutes} min read`,
    content,
  }
}

export function getAllPosts(): PostMeta[] {
  return getAllPostSlugs()
    .map((slug) => getPostBySlug(slug))
    .filter((p): p is Post => p !== null)
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
}

export function getRecentPosts(limit = 3): PostMeta[] {
  return getAllPosts().slice(0, limit)
}
