import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import Image from 'next/image'
import Link from 'next/link'
import { getAllEntries, getAllEntrySlugs, getEntryBySlug } from '@/lib/encyclopedia'

interface Props {
  params: { slug: string }
}

export async function generateStaticParams() {
  return getAllEntrySlugs().map((slug) => ({ slug }))
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const entry = getEntryBySlug(params.slug)
  if (!entry) return {}
  return {
    title: `${entry.title} — Pipe Encyclopedia`,
    description: entry.excerpt,
  }
}

export default function EncyclopediaEntryPage({ params }: Props) {
  const entry = getEntryBySlug(params.slug)
  if (!entry) notFound()

  const related = getAllEntries().filter((e) => e.slug !== entry.slug).slice(0, 3)

  return (
    <div className="min-h-screen bg-mahogany">
      {/* Hero image */}
      <div className="relative h-[40vh] min-h-[300px] overflow-hidden">
        <Image src={entry.image} alt={entry.title} fill priority className="object-cover" sizes="100vw" />
        <div className="absolute inset-0 bg-gradient-to-t from-mahogany via-mahogany/50 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 max-w-screen-lg mx-auto px-6 lg:px-12 pb-8">
          <nav className="flex items-center gap-2 text-xs font-lora text-parchment/50 mb-4">
            <Link href="/" className="hover:text-gold transition-colors">Home</Link>
            <span>/</span>
            <Link href="/encyclopedia" className="hover:text-gold transition-colors">Encyclopedia</Link>
            <span>/</span>
            <span className="text-parchment/70 line-clamp-1">{entry.title}</span>
          </nav>
        </div>
      </div>

      {/* Article */}
      <div className="max-w-screen-lg mx-auto px-6 lg:px-12 -mt-4 pb-20">
        <div className="flex items-center flex-wrap gap-x-4 gap-y-2 mb-6">
          <span className="font-lora text-gold text-sm uppercase tracking-widest">{entry.category}</span>
          {entry.updated && (
            <>
              <span className="text-parchment/20">·</span>
              <span className="font-lora text-parchment/50 text-sm">
                Updated {new Date(entry.updated).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
              </span>
            </>
          )}
        </div>

        <h1 className="font-playfair font-bold text-parchment text-3xl lg:text-5xl leading-tight mb-4">
          {entry.title}
        </h1>

        <p className="font-lora text-parchment/60 text-lg leading-relaxed mb-10 pb-8 border-b border-gold/15">
          {entry.excerpt}
        </p>

        {/* Article body — rendered as HTML from markdown */}
        <article
          className="prose-victorian max-w-none space-y-6"
          style={{
            fontFamily: 'var(--font-lora)',
            color: '#F5EDD6',
            lineHeight: '1.95',
          }}
          dangerouslySetInnerHTML={{
            __html: entry.content
              .replace(/^## (.+)$/gm, '<h2 style="font-family:var(--font-playfair);font-size:1.6rem;font-weight:700;color:#F5EDD6;margin:2.5rem 0 1rem">$1</h2>')
              .replace(/^### (.+)$/gm, '<h3 style="font-family:var(--font-playfair);font-size:1.2rem;font-weight:600;color:#C9A84C;margin:2rem 0 0.75rem">$1</h3>')
              .replace(/\*\*(.+?)\*\*/g, '<strong style="color:#E8D5A3">$1</strong>')
              .replace(/\*(.+?)\*/g, '<em>$1</em>')
              .replace(/^---$/gm, '<hr style="border-color:rgba(201,168,76,0.2);margin:2.5rem 0">')
              .replace(/^(\d+)\. (.+)$/gm, '<li style="margin:0.4rem 0;padding-left:1rem">$2</li>')
              .replace(/^- (.+)$/gm, '<li style="margin:0.4rem 0;padding-left:1rem">$1</li>')
              .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" style="color:#C9A84C;text-decoration:underline">$1</a>')
              .replace(/\n\n/g, '</p><p style="margin-bottom:1.5rem">')
              .replace(/^<p/, '<p style="margin-bottom:1.5rem"'),
          }}
        />

        {/* Pipe Passport CTA */}
        <div className="mt-14 p-8 bg-mahogany-light rounded-sm gold-frame text-center">
          <p className="font-playfair font-bold text-parchment text-xl mb-2">Have a pipe you can&apos;t identify?</p>
          <p className="font-lora text-parchment/60 text-sm mb-5 max-w-lg mx-auto">
            Submit six photographs and receive a free identification and dating assessment —
            your pipe&apos;s own passport, in minutes.
          </p>
          <Link
            href="/encyclopedia/pipe-passport"
            className="btn-gold inline-block px-8 py-3.5 rounded-sm font-playfair font-bold text-sm tracking-widest uppercase"
          >
            Get a Free Pipe Passport
          </Link>
        </div>

        {/* Related entries */}
        {related.length > 0 && (
          <div className="mt-14">
            <h2 className="font-playfair font-bold text-parchment text-2xl mb-6">More from the Encyclopedia</h2>
            <div className="grid md:grid-cols-3 gap-5">
              {related.map((rel) => (
                <Link
                  key={rel.slug}
                  href={`/encyclopedia/${rel.slug}`}
                  className="group block bg-mahogany-light rounded-sm gold-frame overflow-hidden product-card"
                >
                  <div className="relative aspect-[16/9] overflow-hidden">
                    <Image src={rel.image} alt={rel.title} fill className="object-cover group-hover:scale-105 transition-transform duration-500" sizes="33vw" />
                  </div>
                  <div className="p-4">
                    <p className="font-lora text-gold/60 text-xs uppercase tracking-widest mb-1">{rel.category}</p>
                    <p className="font-playfair font-semibold text-parchment text-sm line-clamp-2 group-hover:text-gold transition-colors">{rel.title}</p>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
