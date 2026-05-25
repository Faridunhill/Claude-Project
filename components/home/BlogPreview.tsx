import Link from 'next/link'
import Image from 'next/image'
import { getRecentPosts } from '@/lib/mdx'

export default async function BlogPreview() {
  const posts = await getRecentPosts(3)

  return (
    <section className="bg-wood-texture py-24">
      <div className="max-w-screen-xl mx-auto px-6 lg:px-12">
        {/* Header */}
        <div className="flex items-end justify-between mb-10 gap-4 flex-wrap">
          <div>
            <span className="font-fell italic text-gold/70 text-sm tracking-widest">~ From the Editors ~</span>
            <h2 className="font-playfair font-bold text-parchment text-4xl mt-2">
              The Faridunhill Journal
            </h2>
            <p className="font-lora text-parchment/55 mt-2 max-w-lg">
              Pipe culture, tobacco reviews, collector's notes, and the literature of the slow smoke.
            </p>
          </div>
          <Link href="/blog" className="btn-ghost px-6 py-2.5 rounded-sm text-sm tracking-widest uppercase">
            Visit the Journal →
          </Link>
        </div>

        {/* Post grid */}
        {posts.length === 0 ? (
          <div className="text-center py-12 text-parchment/40 font-lora">
            Posts loading — check back soon.
          </div>
        ) : (
          <div className="grid md:grid-cols-3 gap-6">
            {posts.map((post, i) => (
              <Link
                key={post.slug}
                href={`/blog/${post.slug}`}
                className="group block bg-mahogany-light rounded-sm gold-frame overflow-hidden product-card"
              >
                {/* Thumbnail */}
                <div className="relative aspect-[16/9] overflow-hidden">
                  <Image
                    src={post.image}
                    alt={post.title}
                    fill
                    className="object-cover transition-transform duration-500 group-hover:scale-105"
                    sizes="(max-width: 768px) 100vw, 33vw"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-mahogany/60 to-transparent" />
                  {i === 0 && (
                    <div className="absolute top-3 left-3 bg-gold px-2.5 py-0.5 rounded-sm">
                      <span className="font-playfair text-mahogany text-xs font-bold uppercase tracking-wide">Latest</span>
                    </div>
                  )}
                </div>

                {/* Content */}
                <div className="p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="font-lora text-gold/70 text-xs uppercase tracking-widest">{post.category}</span>
                    {post.readingTime && (
                      <>
                        <span className="text-parchment/20">·</span>
                        <span className="font-lora text-parchment/40 text-xs">{post.readingTime}</span>
                      </>
                    )}
                  </div>

                  <h3 className="font-playfair font-semibold text-parchment text-base leading-snug group-hover:text-gold transition-colors line-clamp-2 mb-2">
                    {post.title}
                  </h3>

                  <p className="font-lora text-parchment/55 text-sm leading-relaxed line-clamp-3 mb-4">
                    {post.excerpt}
                  </p>

                  <div className="flex items-center justify-between text-xs">
                    <span className="font-lora text-parchment/40">{post.author}</span>
                    <span className="font-lora text-parchment/30">
                      {new Date(post.date).toLocaleDateString('en-US', {
                        month: 'long',
                        day: 'numeric',
                        year: 'numeric',
                      })}
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}

        {/* Bottom CTA */}
        <div className="text-center mt-10">
          <Link
            href="/blog"
            className="btn-gold inline-flex items-center gap-2 px-8 py-3.5 rounded-sm text-sm tracking-widest uppercase"
          >
            Visit the Full Journal
          </Link>
        </div>
      </div>
    </section>
  )
}
