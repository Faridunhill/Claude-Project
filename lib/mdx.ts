import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'
import { sanityClient, hasSanity } from '@/lib/sanity'

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

const POSTS_QUERY = `*[_type == "post"] | order(publishedAt desc) {
  "slug": slug.current,
  title,
  author,
  "date": publishedAt,
  category,
  excerpt,
  "image": mainImage.asset->url,
  tags,
  "content": body
}`

function calcReadingTime(text: string): string {
  const minutes = Math.ceil(text.split(/\s+/).length / 238)
  return `${minutes} min read`
}

async function fetchSanityPosts(): Promise<Post[] | null> {
  if (!hasSanity || !sanityClient) return null
  try {
    const docs = await sanityClient.fetch<Post[]>(POSTS_QUERY)
    if (docs && docs.length > 0) {
      return docs.map((doc) => ({
        ...doc,
        readingTime: calcReadingTime(doc.content || ''),
      }))
    }
  } catch (err) {
    console.error('Sanity post fetch failed, using MDX fallback:', err)
  }
  return null
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

export async function getAllPostSlugs(): Promise<string[]> {
  if (hasSanity && sanityClient) {
    try {
      const slugs = await sanityClient.fetch<string[]>(
        `*[_type == "post"]{ "slug": slug.current }.slug`
      )
      if (slugs && slugs.length > 0) return slugs
    } catch {}
  }
  return getMdxSlugs()
}

export async function getPostBySlug(slug: string): Promise<Post | null> {
  const sanityPosts = await fetchSanityPosts()
  if (sanityPosts) {
    return sanityPosts.find((p) => p.slug === slug) ?? null
  }
  return getMdxPost(slug)
}

export async function getAllPosts(): Promise<PostMeta[]> {
  const sanityPosts = await fetchSanityPosts()
  if (sanityPosts) return sanityPosts

  return getMdxSlugs()
    .map(getMdxPost)
    .filter((p): p is Post => p !== null)
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
}

export async function getRecentPosts(limit = 3): Promise<PostMeta[]> {
  return (await getAllPosts()).slice(0, limit)
}
