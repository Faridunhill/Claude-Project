import Link from 'next/link'

const STEPS = ['Fill.', 'Light.', 'Breathe.']

export default function RitualSection() {
  return (
    <section className="bg-[#060403] py-28 md:py-40">
      <div className="mx-auto max-w-3xl px-6 text-center">
        <p className="font-fell italic text-gold/60 text-sm tracking-[0.3em] uppercase mb-12">
          The Ritual
        </p>
        <div className="space-y-2">
          {STEPS.map((step) => (
            <p
              key={step}
              className="font-playfair font-bold text-parchment text-5xl md:text-7xl leading-tight"
            >
              {step}
            </p>
          ))}
        </div>
        <p className="font-lora text-parchment/55 leading-relaxed mt-12 max-w-xl mx-auto">
          Every day, the same pipe. The same blend. The same silence. Not habit — ceremony. The
          pipe demands that you slow down. It is the only thing in your life that cannot be
          rushed.
        </p>
        <Link
          href="/shop"
          className="mt-12 inline-block border border-gold/60 px-10 py-4 font-lora text-gold text-xs tracking-[0.25em] uppercase transition-colors duration-300 hover:bg-gold hover:text-mahogany-dark"
        >
          Begin Your Ritual
        </Link>
      </div>
    </section>
  )
}
