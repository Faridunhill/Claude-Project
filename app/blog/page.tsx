import type { Metadata } from 'next'
import Image from 'next/image'
import Link from 'next/link'
import { getAllPosts } from '@/lib/mdx'

export const metadata: Metadata = {
  title: 'The Faridunhill Journal',
  description:
    'Pipe culture, tobacco reviews, collector\'s notes, and the literature of the slow smoke. Published daily by the editors of Faridunhill.',
}

export default async function BlogIndexPage() {
  const posts = await getAllPosts()
  const [featured, ...rest] = posts

  return (
    <div className="min-h-screen bg-mahogany">
      {/* Header */}
      <div className="bg-mahogany-dark border-b border-gold/15 py-14 text-center">
        <span className="font-fell italic text-gold/70 text-sm tracking-widest">~ Est. 2007 ~</span>
        <h1 className="font-playfair font-bold text-parchment text-5xl lg:text-6xl mt-3">
          The Faridunhill Journal
        </h1>
        <div className="ornament-divider max-w-xs mx-auto mt-5 mb-4">
          <span className="ornament-divider-symbol text-gold">❧</span>
        </div>
        <p className="font-lora text-parchment/55 max-w-xl mx-auto text-base">
          Pipe culture, tobacco reviews, collector&apos;s notes, and the literature of the slow smoke.
          Published for the curious, the dedicated, and the unhurried.
        </p>
      </div>

      <div className="max-w-screen-xl mx-auto px-6 lg:px-12 py-14">
        {posts.length === 0 ? (
          <p className="text-center font-lora text-parchment/40 py-20">Posts coming soon.</p>
        ) : (
          <>
            {/* Featured post */}
            {featured && (
              <div className="mb-12">
                <p className="font-playfair text-gold/70 text-xs uppercase tracking-widest mb-4">Featured</p>
                <Link
                  href={`/blog/${featured.slug}`}
                  className="group grid lg:grid-cols-2 gap-0 rounded-sm gold-frame overflow-hidden bg-mahogany-light product-card"
                >
                  <div className="relative aspect-[16/10] lg:aspect-auto overflow-hidden">
                    <Image
                      src={featured.image}
                      alt={featured.title}
                      fill
                      priority
                      className="object-cover transition-transform duration-700 group-hover:scale-105"
                      sizes="(max-width: 1024px) 100vw, 50vw"
                    />
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent to-mahogany-light/40" />
                  </div>
                  <div className="p-8 lg:p-10 flex flex-col justify-center">
                    <div className="flex items-center gap-2 mb-4">
                      <span className="font-lora text-gold text-xs uppercase tracking-widest">{featured.category}</span>
                      <span className="text-parchment/20">·</span>
                      <span className="font-lora text-parchment/40 text-xs">{featured.readingTime}</span>
                    </div>
                    <h2 className="font-playfair font-bold text-parchment text-2xl lg:text-3xl leading-tight group-hover:text-gold transition-colors mb-4">
                      {featured.title}
                    </h2>
                    <p className="font-lora text-parchment/60 leading-relaxed line-clamp-3 mb-6">{featured.excerpt}</p>
                    <div className="flex items-center justify-between text-xs font-lora">
                      <span className="text-parchment/50">{featured.author}</span>
                      <span className="text-parchment/35">
                        {new Date(featured.date).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
                      </span>
                    </div>
                  </div>
                </Link>
              </div>
            )}

            {/* Grid of remaining posts */}
            {rest.length > 0 && (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {rest.map((post) => (
                  <Link
                    key={post.slug}
                    href={`/blog/${post.slug}`}
                    className="group block bg-mahogany-light rounded-sm gold-frame overflow-hidden product-card"
                  >
                    <div className="relative aspect-[16/9] overflow-hidden">
                      <Image
                        src={post.image}
                        alt={post.title}
                        fill
                        className="object-cover transition-transform duration-500 group-hover:scale-105"
                        sizes="(max-width: 768px) 100vw, 33vw"
                      />
                    </div>
                    <div className="p-5">
                      <div className="flex items-center gap-2 mb-3">
                        <span className="font-lora text-gold/70 text-xs uppercase tracking-widest">{post.category}</span>
                        <span className="text-parchment/20">·</span>
                        <span className="font-lora text-parchment/40 text-xs">{post.readingTime}</span>
                      </div>
                      <h2 className="font-playfair font-semibold text-parchment text-base leading-snug group-hover:text-gold transition-colors line-clamp-2 mb-2">
                        {post.title}
                      </h2>
                      <p className="font-lora text-parchment/55 text-sm line-clamp-2 leading-relaxed mb-4">{post.excerpt}</p>
                      <div className="flex justify-between text-xs font-lora text-parchment/35">
                        <span>{post.author}</span>
                        <span>{new Date(post.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
