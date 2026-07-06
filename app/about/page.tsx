import type { Metadata } from 'next'
import Image from 'next/image'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'About Us',
  description:
    'Thirty years of collector knowledge, old-world craftsmanship, and an abiding love of the pipe. The story of Faridunhill.',
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
                Over three decades, that obsession became expertise. A collection of over four hundred
                pipes. A tobacco cellar of particular depth — tins and jars cellared through the
                years when the great blenders were still producing the blends that have since
                become legendary. And a knowledge of the craft that can only come from decades of
                patient, attentive smoking.
              </p>
              <p className="font-lora text-parchment/75 leading-[1.95] text-[1.02rem]">
                The faridunhill store first opened its doors on eBay in 2007, because the knowledge
                had become too good to keep private. We built it on a simple principle: every product we sell must
                be something we would be proud to smoke ourselves. Nothing else makes the cut.
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
                body: 'Every member of our team is a smoker. We test every pipe, smoke every tobacco, and stand behind every product with direct experience. We do not sell anything we cannot explain, and we cannot explain anything we have not smoked.',
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
            Our pipe selection spans the full range of the craft. We carry new production pipes from
            the world&apos;s finest makers — Dunhill, Savinelli, Peterson, Stanwell, Chacom, and
            Missouri Meerschaum — alongside our rotating estate collection, which is drawn from
            private acquisitions, collection dispersals, and the work of our in-house restoration
            specialist.
          </p>
          <p className="font-lora text-parchment/75 leading-[1.95] text-[1.02rem]">
            Our tobaccos are chosen with the same rigour. We prioritise classic English blenders —
            Samuel Gawith, Gawith &amp; Hoggarth, Dunhill, G.L. Pease — alongside the finest
            American blenders: Cornell &amp; Diehl, McClelland (from our estate tin stock), and
            the Sutliff catalogue. We maintain a small but serious cigar selection drawn from the
            premium Nicaraguan, Honduran, and Dominican producers.
          </p>
          <p className="font-lora text-parchment/75 leading-[1.95] text-[1.02rem]">
            Our leather goods are made in house, in small batches, from vegetable-tanned full-grain
            leather. Our gift sets are curated personally by our head tobacconist, who refuses to
            put his name on anything he would not give to a friend.
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
