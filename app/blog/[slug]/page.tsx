import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import Image from 'next/image'
import Link from 'next/link'
import { getAllPostSlugs, getPostBySlug, getAllPosts } from '@/lib/mdx'
import NewsletterSection from '@/components/home/NewsletterSection'

interface Props {
  params: { slug: string }
}

export async function generateStaticParams() {
  const slugs = await getAllPostSlugs()
  return slugs.map((slug) => ({ slug }))
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const post = await getPostBySlug(params.slug)
  if (!post) return {}
  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      type: 'article',
      publishedTime: post.date,
      authors: [post.author],
      images: [{ url: post.image, width: 1200, height: 630 }],
    },
    twitter: {
      card: 'summary_large_image',
      title: post.title,
      description: post.excerpt,
      images: [post.image],
    },
  }
}

export default async function BlogPostPage({ params }: Props) {
  const post = await getPostBySlug(params.slug)
  if (!post) notFound()

  const allPosts = await getAllPosts()
  const related = allPosts.filter((p) => p.slug !== post.slug && p.category === post.category).slice(0, 3)

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: post.title,
    description: post.excerpt,
    author: { '@type': 'Person', name: post.author },
    datePublished: post.date,
    image: post.image,
    publisher: {
      '@type': 'Organization',
      name: 'Faridunhill',
      logo: { '@type': 'ImageObject', url: `${process.env.NEXT_PUBLIC_SITE_URL}/logo.svg` },
    },
  }

  return (
    <div className="min-h-screen bg-mahogany">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      {/* Hero image */}
      <div className="relative h-[50vh] min-h-[380px] overflow-hidden">
        <Image
          src={post.image}
          alt={post.title}
          fill
          priority
          className="object-cover"
          sizes="100vw"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-mahogany via-mahogany/50 to-transparent" />

        {/* Breadcrumb over image */}
        <div className="absolute bottom-0 left-0 right-0 max-w-screen-lg mx-auto px-6 lg:px-12 pb-8">
          <nav className="flex items-center gap-2 text-xs font-lora text-parchment/50 mb-4">
            <Link href="/" className="hover:text-gold transition-colors">Home</Link>
            <span>/</span>
            <Link href="/blog" className="hover:text-gold transition-colors">Journal</Link>
            <span>/</span>
            <span className="text-parchment/70 line-clamp-1">{post.title}</span>
          </nav>
        </div>
      </div>

      {/* Article */}
      <div className="max-w-screen-lg mx-auto px-6 lg:px-12 -mt-4 pb-20">
        {/* Meta */}
        <div className="flex items-center flex-wrap gap-x-4 gap-y-2 mb-6">
          <span className="font-lora text-gold text-sm uppercase tracking-widest">{post.category}</span>
          <span className="text-parchment/20">·</span>
          <span className="font-lora text-parchment/50 text-sm">{post.readingTime}</span>
          <span className="text-parchment/20">·</span>
          <span className="font-lora text-parchment/50 text-sm">
            {new Date(post.date).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
          </span>
        </div>

        <h1 className="font-playfair font-bold text-parchment text-3xl lg:text-5xl leading-tight mb-4">
          {post.title}
        </h1>

        <p className="font-lora text-parchment/60 text-lg leading-relaxed mb-8">{post.excerpt}</p>

        <div className="flex items-center gap-3 mb-10 pb-8 border-b border-gold/15">
          <div className="w-10 h-10 rounded-full bg-mahogany-light border border-gold/20 flex items-center justify-center">
            <span className="font-playfair text-gold text-sm font-bold">
              {post.author.charAt(0)}
            </span>
          </div>
          <div>
            <p className="font-playfair font-semibold text-parchment text-sm">{post.author}</p>
            <p className="font-lora text-parchment/40 text-xs">Head Tobacconist, Faridunhill</p>
          </div>
        </div>

        {/* Article body — rendered as HTML from markdown */}
        <article
          className="prose-victorian max-w-none space-y-6"
          style={{
            fontFamily: 'var(--font-lora)',
            color: '#F5EDD6',
            lineHeight: '1.95',
          }}
          dangerouslySetInnerHTML={{
            /* Basic markdown conversion — for production, use next-mdx-remote */
            __html: post.content
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

        {/* Social share */}
        <div className="mt-12 pt-8 border-t border-gold/15">
          <p className="font-playfair text-parchment/60 text-sm mb-4">Share this article:</p>
          <div className="flex gap-3">
            {['Twitter / X', 'Facebook', 'Reddit', 'Email'].map((s) => (
              <a
                key={s}
                href="#"
                className="btn-ghost px-4 py-2 rounded-sm text-xs tracking-wide"
              >
                {s}
              </a>
            ))}
          </div>
        </div>

        {/* Author bio */}
        <div className="mt-10 p-6 bg-mahogany-light rounded-sm gold-frame">
          <p className="font-playfair font-bold text-parchment mb-1">{post.author}</p>
          <p className="font-lora text-parchment/60 text-sm leading-relaxed">
            Head Tobacconist at Faridunhill with over thirty years of experience collecting and
            smoking fine pipes. His particular passions are Virginia flakes, estate briars from
            the Saint-Claude period, and the slow art of pipe restoration.
          </p>
        </div>

        {/* Related posts */}
        {related.length > 0 && (
          <div className="mt-14">
            <h2 className="font-playfair font-bold text-parchment text-2xl mb-6">Related from the Journal</h2>
            <div className="grid md:grid-cols-3 gap-5">
              {related.map((rel) => (
                <Link key={rel.slug} href={`/blog/${rel.slug}`} className="group block bg-mahogany-light rounded-sm gold-frame overflow-hidden product-card">
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

        {/* Disqus placeholder */}
        <div className="mt-14 p-8 bg-mahogany-light rounded-sm border border-gold/10 text-center">
          <p className="font-playfair text-parchment/50 text-sm">Comments powered by Disqus</p>
          <p className="font-lora text-parchment/30 text-xs mt-1">
            {/* Add your Disqus shortname to enable: https://disqus.com */}
            Insert Disqus embed code here — set shortname in environment variables
          </p>
        </div>
      </div>

      {/* Newsletter at bottom of every post */}
      <NewsletterSection />
    </div>
  )
}
