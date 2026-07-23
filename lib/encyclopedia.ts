import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'

const ENCYCLOPEDIA_DIR = path.join(process.cwd(), 'content/encyclopedia')

export const ENCYCLOPEDIA_CATEGORIES = [
  'History',
  'Science & Nature',
  'Arts & Culture',
  'Craft & Technique',
  'People & Places',
  'Language & Ideas',
] as const

export interface EncyclopediaEntryMeta {
  slug: string
  title: string
  category: string
  summary: string
  date: string
  tags: string[]
  /** Finished presenter video (HeyGen output or self-hosted MP4). Empty until rendered. */
  videoUrl: string
  /** Optional narration-only audio (ElevenLabs output). */
  audioUrl: string
  /** Poster / cover image for cards. */
  image: string
  readingTime?: string
}

export interface EncyclopediaEntry extends EncyclopediaEntryMeta {
  /** Article body (markdown). */
  content: string
  /** The spoken narration script used for the video. */
  narration: string
}

function calcReadingTime(text: string): string {
  const minutes = Math.ceil(text.split(/\s+/).length / 238)
  return `${minutes} min read`
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
    category: data.category || 'Language & Ideas',
    summary: data.summary || '',
    date: data.date || '',
    tags: data.tags || [],
    videoUrl: data.videoUrl || '',
    audioUrl: data.audioUrl || '',
    image:
      data.image ||
      'https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=1200&q=85',
    narration: data.narration || '',
    readingTime: calcReadingTime(content),
    content,
  }
}

export function getAllEntries(): EncyclopediaEntryMeta[] {
  return getSlugs()
    .map(getEntryBySlug)
    .filter((e): e is EncyclopediaEntry => e !== null)
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    .map(({ content: _content, narration: _narration, ...meta }) => meta)
}

export function getAllEntrySlugs(): string[] {
  return getSlugs()
}
