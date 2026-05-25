export default function StorySection() {
  return (
    <section className="bg-parchment-texture relative overflow-hidden">
      {/* Top ornamental border */}
      <div className="h-1 bg-gradient-to-r from-transparent via-gold to-transparent opacity-60" />

      <div className="max-w-screen-lg mx-auto px-6 lg:px-12 py-24">
        {/* Section header */}
        <div className="text-center mb-14">
          <span className="font-fell italic text-leather text-sm tracking-widest">~ Our Philosophy ~</span>
          <h2 className="font-playfair font-bold text-mahogany text-4xl lg:text-5xl mt-3 leading-tight">
            The Art of Slow Tobacco
          </h2>
          <div className="ornament-divider mt-6 max-w-xs mx-auto">
            <span className="ornament-divider-symbol text-leather">❧</span>
          </div>
        </div>

        {/* Editorial columns */}
        <div className="grid lg:grid-cols-2 gap-12 items-start">
          <div className="space-y-6">
            <p className="body-serif text-mahogany text-[1.05rem] leading-[1.95]">
              There is a particular quality to the silence that gathers in a room when a pipe is lit.
              It is not the silence of emptiness, but of fullness — of thought finding its proper
              pace. The pipe has been the companion of philosophers, poets, and men of affairs for
              five centuries, and it has never hurried any of them. That, we believe, is its
              greatest virtue.
            </p>
            <p className="body-serif text-mahogany/85 text-[1.05rem] leading-[1.95]">
              Faridunhill was born from three decades of obsession. Our founder began collecting
              estate pipes in the early 1990s, haunting antique shops, estate sales, and tobacco
              auctions with the particular fervour of a man who has found his calling. Each pipe
              told a story — of the hands that carved it, the workshops of Saint-Claude and
              Pesaro, the tobacconists of London's Jermyn Street, the smokers who wore grooves
              into the stem with their teeth.
            </p>
            <p className="body-serif text-mahogany/85 text-[1.05rem] leading-[1.95]">
              That knowledge — hard-won, lovingly accumulated — is the foundation of everything
              we sell. When we curate a pipe for our shelves, we smoke it first. When we select
              a tobacco blend, we taste it slowly, over weeks, in different conditions and different
              moods. We stock nothing we would not be proud to smoke ourselves.
            </p>
          </div>

          <div className="space-y-6">
            {/* Pull quote */}
            <blockquote className="relative bg-mahogany px-8 py-10 rounded-sm gold-frame my-2">
              <span className="absolute top-4 left-6 font-playfair text-gold/25 text-6xl leading-none select-none">&ldquo;</span>
              <p className="font-fell italic text-parchment text-xl lg:text-2xl leading-relaxed relative z-10 mt-4">
                A pipe is the philosopher's pen — it slows the mind and sharpens thought.
              </p>
              <footer className="mt-5 text-gold/60 font-lora text-xs tracking-wider uppercase">
                — The Faridunhill Creed
              </footer>
            </blockquote>

            <p className="body-serif text-mahogany/85 text-[1.05rem] leading-[1.95]">
              We are, above all, a shop for the serious smoker and the curious beginner alike.
              The man who has smoked the same Dunhill Shell Briar for forty years will find us
              a worthy resource. So will the young man who has just read his first Sherlock Holmes
              and feels, not unreasonably, that a pipe might help him think. We welcome them both
              with equal warmth, and the same depth of knowledge.
            </p>
            <p className="body-serif text-mahogany/85 text-[1.05rem] leading-[1.95]">
              This is Faridunhill: a gentleman's tobacconist for the twenty-first century,
              built on the values of the nineteenth. We hope you will stay a while.
            </p>
          </div>
        </div>

        {/* Signature */}
        <div className="text-center mt-16 pt-10 border-t border-leather/20">
          <p className="font-fell italic text-leather text-lg">
            Yours in smoke,
          </p>
          <p className="font-playfair font-bold text-mahogany text-2xl mt-2">
            F. Dunhill
          </p>
          <p className="font-lora text-leather/70 text-sm mt-1 tracking-wide">
            Founder &amp; Head Tobacconist
          </p>
        </div>
      </div>

      {/* Bottom ornamental border */}
      <div className="h-1 bg-gradient-to-r from-transparent via-gold to-transparent opacity-40" />
    </section>
  )
}
