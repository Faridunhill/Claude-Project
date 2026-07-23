import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import { getAllEntrySlugs, getAllEntries, getEntryBySlug } from '@/lib/encyclopedia'

interface Props {
  params: { slug: string }
}

export function generateStaticParams() {
  return getAllEntrySlugs().map((slug) => ({ slug }))
}

export function generateMetadata({ params }: Props): Metadata {
  const entry = getEntryBySlug(params.slug)
  if (!entry) return {}
  return {
    title: entry.title,
    description: entry.summary,
    openGraph: {
      title: entry.title,
      description: entry.summary,
      type: 'article',
      images: [{ url: entry.image, width: 1200, height: 630 }],
    },
  }
}

export default function EncyclopediaEntryPage({ params }: Props) {
  const entry = getEntryBySlug(params.slug)
  if (!entry) notFound()

  const related = getAllEntries()
    .filter((e) => e.slug !== entry.slug && e.category === entry.category)
    .slice(0, 3)

  return (
    <div className="min-h-screen bg-mahogany">
      <div className="max-w-screen-lg mx-auto px-6 lg:px-12 pt-10 pb-20">
        <nav className="flex items-center gap-2 text-xs font-lora text-parchment/50 mb-8">
          <Link href="/" className="hover:text-gold transition-colors">Home</Link>
          <span>/</span>
          <Link href="/encyclopedia" className="hover:text-gold transition-colors">Encyclopedia</Link>
          <span>/</span>
          <span className="text-parchment/70 line-clamp-1">{entry.title}</span>
        </nav>

        <div className="flex items-center flex-wrap gap-x-4 gap-y-2 mb-4">
          <span className="font-lora text-gold text-sm uppercase tracking-widest">{entry.category}</span>
          <span className="text-parchment/20">·</span>
          <span className="font-lora text-parchment/50 text-sm">{entry.readingTime}</span>
          {entry.date && (
            <>
              <span className="text-parchment/20">·</span>
              <span className="font-lora text-parchment/50 text-sm">
                {new Date(entry.date).toLocaleDateString('en-US', {
                  month: 'long',
                  day: 'numeric',
                  year: 'numeric',
                })}
              </span>
            </>
          )}
        </div>

        <h1 className="font-playfair font-bold text-parchment text-3xl lg:text-5xl leading-tight mb-4">
          {entry.title}
        </h1>
        <p className="font-lora text-parchment/60 text-lg leading-relaxed mb-8">{entry.summary}</p>

        {/* Presenter video */}
        {entry.videoUrl ? (
          <div className="mb-10 gold-frame rounded-sm overflow-hidden bg-mahogany-dark">
            <video controls src={entry.videoUrl} poster={entry.image} className="w-full" />
          </div>
        ) : (
          <div className="mb-10 p-6 bg-mahogany-light rounded-sm border border-gold/10 text-center">
            <p className="font-lora text-parchment/40 text-sm">
              The video lesson for this entry hasn&apos;t been rendered yet — read the article below.
            </p>
          </div>
        )}

        {entry.audioUrl && (
          <div className="mb-10">
            <p className="font-playfair text-parchment/60 text-sm mb-2">Listen to the narration:</p>
            <audio controls src={entry.audioUrl} className="w-full" />
          </div>
        )}

        {/* Article body — same lightweight markdown rendering as the Journal */}
        <article
          className="prose-victorian max-w-none space-y-6"
          style={{ fontFamily: 'var(--font-lora)', color: '#F5EDD6', lineHeight: '1.95' }}
          dangerouslySetInnerHTML={{
            __html: entry.content
              .replace(/^## (.+)$/gm, '<h2 style="font-family:var(--font-playfair);font-size:1.6rem;font-weight:700;color:#F5EDD6;margin:2.5rem 0 1rem">$1</h2>')
              .replace(/^### (.+)$/gm, '<h3 style="font-family:var(--font-playfair);font-size:1.2rem;font-weight:600;color:#C9A84C;margin:2rem 0 0.75rem">$1</h3>')
              .replace(/\*\*(.+?)\*\*/g, '<strong style="color:#E8D5A3">$1</strong>')
              .replace(/\*(.+?)\*/g, '<em>$1</em>')
              .replace(/^---$/gm, '<hr style="border-color:rgba(201,168,76,0.2);margin:2.5rem 0">')
              .replace(/^- (.+)$/gm, '<li style="margin:0.4rem 0;padding-left:1rem">$1</li>')
              .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" style="color:#C9A84C;text-decoration:underline">$1</a>')
              .replace(/\n\n/g, '</p><p style="margin-bottom:1.5rem">')
              .replace(/^<p/, '<p style="margin-bottom:1.5rem"'),
          }}
        />

        {entry.tags.length > 0 && (
          <div className="mt-10 flex flex-wrap gap-2">
            {entry.tags.map((tag) => (
              <span
                key={tag}
                className="font-lora text-xs text-gold/70 border border-gold/20 rounded-sm px-3 py-1"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {related.length > 0 && (
          <div className="mt-14">
            <h2 className="font-playfair font-bold text-parchment text-2xl mb-6">
              More in {entry.category}
            </h2>
            <div className="grid md:grid-cols-3 gap-5">
              {related.map((rel) => (
                <Link
                  key={rel.slug}
                  href={`/encyclopedia/${rel.slug}`}
                  className="group block bg-mahogany-light rounded-sm gold-frame overflow-hidden product-card p-4"
                >
                  <p className="font-lora text-gold/60 text-xs uppercase tracking-widest mb-1">
                    {rel.videoUrl ? 'Video + article' : 'Article'}
                  </p>
                  <p className="font-playfair font-semibold text-parchment text-sm line-clamp-2 group-hover:text-gold transition-colors">
                    {rel.title}
                  </p>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
