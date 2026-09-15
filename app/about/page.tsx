import type { Metadata } from 'next'
import { externalLinks } from '@/lib/links'
import Image from 'next/image'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'About Us',
  description:
    'Thirty years of collecting estate pipes, and the shop it became. Around a hundred estate pipes listed at any time, plus vintage leather and smoking accessories. Est. 2015, New Jersey.',
}

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-mahogany">
      {/* Hero */}
      <div className="relative h-72 overflow-hidden">
        <Image
          src="https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=1600&q=85"
          alt="A warmly lit private library — the spiritual home of Faridunhill"
          fill
          className="object-cover"
          sizes="100vw"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-mahogany via-mahogany/70 to-mahogany/30" />
        <div className="relative h-full flex items-end max-w-screen-lg mx-auto px-6 lg:px-12 pb-10">
          <div>
            <span className="font-fell italic text-gold/70 text-sm tracking-widest">~ Our Story ~</span>
            <h1 className="font-playfair font-bold text-parchment text-4xl lg:text-5xl mt-2">About Faridunhill</h1>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-screen-lg mx-auto px-6 lg:px-12 py-16 space-y-12">

        {/* Origin story */}
        <section>
          <div className="ornament-divider mb-8">
            <span className="ornament-divider-symbol text-gold">❧</span>
          </div>
          <div className="grid lg:grid-cols-2 gap-10 items-start">
            <div className="space-y-5">
              <h2 className="font-playfair font-bold text-parchment text-3xl">
                Thirty Years in the Making
              </h2>
              <p className="font-lora text-parchment/75 leading-[1.95] text-[1.02rem]">
                Faridunhill did not begin as a business. It began as an obsession. In the early 1990s,
                our founder began collecting estate pipes — visiting antique shops, estate sales,
                tobacco auctions, and the darker corners of early internet forums in search of the
                pipes that other smokers had left behind. Dunhill, Barling, Comoy, Sasieni,
                Charatan — the names became a private language, a catalogue of desire.
              </p>
              <p className="font-lora text-parchment/75 leading-[1.95] text-[1.02rem]">
                Over three decades that obsession became expertise, and the collection passed four
                hundred pipes. Today around a hundred estate pipes are listed here at any one time
                — Stanwell, Vauen, Savinelli, Charatan, Ser Jacopo, Tsuge among them — rotating as
                pieces find new owners and new ones are acquired.
              </p>
              <p className="font-lora text-parchment/75 leading-[1.95] text-[1.02rem]">
                Faridunhill opened as a public shop in 2015, because the knowledge had become too
                good to keep private. More than five thousand pieces have gone out to collectors
                through{' '}
                <a
                  href={externalLinks.ebay.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gold hover:text-gold/80 underline underline-offset-4 decoration-gold/40 transition-colors"
                >
                  our eBay storefront
                </a>{' '}
                since — the feedback is public, and we would rather you checked it than took our
                word. The principle has not changed: every item is photographed exactly as it is,
                and described the way we would want it described to us.
              </p>
            </div>
            <div className="relative aspect-[4/5] rounded-sm overflow-hidden gold-frame">
              <Image
                src="https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&q=85"
                alt="Hands holding a lit briar pipe — the collector's contemplation"
                fill
                className="object-cover"
                sizes="50vw"
              />
            </div>
          </div>
        </section>

        {/* Mission */}
        <section className="bg-parchment-texture rounded-sm p-10 victorian-frame">
          <h2 className="font-playfair font-bold text-mahogany text-2xl mb-6 text-center">Our Mission & Values</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                title: 'Knowledge First',
                body: 'Thirty years of collecting is the whole qualification. Every pipe is examined in the hand before it is listed — grain, drilling, stem fit, and the honest condition of a piece that has already lived one life. We do not list anything we cannot explain.',
              },
              {
                title: 'Quality Without Compromise',
                body: 'We do not stock category-fillers. Every product in our range was chosen deliberately, tested rigorously, and priced to reflect its actual quality — not its margin. We would rather carry fewer products and stand behind each one completely.',
              },
              {
                title: 'The Long Game',
                body: 'The pipe is a lifelong pursuit. We are not interested in one-time customers. We are interested in guiding a smoker from their first corncob to their hundredth estate briar, and being a trusted resource at every stage of that journey.',
              },
            ].map((v) => (
              <div key={v.title} className="text-center">
                <h3 className="font-playfair font-bold text-mahogany text-lg mb-3">{v.title}</h3>
                <p className="font-lora text-mahogany/70 text-sm leading-relaxed">{v.body}</p>
              </div>
            ))}
          </div>
        </section>

        {/* The collection */}
        <section className="space-y-5">
          <h2 className="font-playfair font-bold text-parchment text-3xl">What We Stock, and Why</h2>
          <p className="font-lora text-parchment/75 leading-[1.95] text-[1.02rem]">
            Estate pipes are the heart of it — around a hundred at any time, drawn from private
            acquisitions and collection dispersals. The Danish and German workshops are well
            represented: Stanwell, Vauen, Big Ben. Alongside them, Italian work from Savinelli and
            Ser Jacopo, English Charatan, Japanese Tsuge, and hand-carved Turkish meerschaum.
            Stock rotates constantly, so the shop is the catalogue — if it is listed, we have it.
          </p>
          <p className="font-lora text-parchment/75 leading-[1.95] text-[1.02rem]">
            Our leather is vintage and estate rather than new production: mid-century German
            tobacco pouches and tin carriers, Offenbach cigar cases, Spanish Ubrique travel cases
            — full-grain pieces made in the years when leather goods were built to outlast their
            owner. Each is sold in the condition it reached us, with its flaws described rather
            than photographed around.
          </p>
          <p className="font-lora text-parchment/75 leading-[1.95] text-[1.02rem]">
            Alongside these: Solingen cigar cutters and scissors, ashtrays, tampers, pipe stands,
            and vintage lighters. What we do not stock is tobacco — no tins, no cigars, no vaping
            products. This is a shop for the objects, not the leaf.
          </p>
        </section>

        {/* CTA */}
        <div className="text-center border-t border-gold/15 pt-12">
          <p className="font-fell italic text-gold/70 text-lg mb-4">
            &ldquo;Come in. Stay a while. The pipe will keep.&rdquo;
          </p>
          <Link href="/shop" className="btn-gold inline-flex px-10 py-4 rounded-sm text-sm tracking-widest uppercase">
            Explore Our Collection
          </Link>
        </div>
      </div>
    </div>
  )
}
