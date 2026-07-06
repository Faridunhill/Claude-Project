import Link from 'next/link'

// The founder's treasures — full-quality photography from the live catalog.
const HERO_IMAGES = [
  'https://i.etsystatic.com/34479460/r/il/df7987/7663292576/il_fullxfull.7663292576_kbvp.jpg', // Rattray's Mary set
  'https://i.etsystatic.com/34479460/r/il/d22f04/7660094618/il_fullxfull.7660094618_qvl4.jpg', // Jurgen Moritz freehand
  'https://i.etsystatic.com/34479460/r/il/b638f2/7771295153/il_fullxfull.7771295153_5yx6.jpg', // Charatan Grosvenor
  'https://i.etsystatic.com/34479460/r/il/13888d/7332132978/il_fullxfull.7332132978_b5zs.jpg', // Butz-Choquin Flamme
]

export default function CinematicHero() {
  return (
    <section className="relative h-screen min-h-[640px] overflow-hidden bg-[#060403]">
      {/* Slow crossfading treasures, each with a Ken Burns drift */}
      {HERO_IMAGES.map((src, i) => (
        <div
          key={src}
          className="hero-slide ken-burns absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url('${src}')`, animationDelay: `${i * 8}s, 0s` }}
        />
      ))}
      <div className="absolute inset-0 bg-gradient-to-b from-[#060403]/75 via-[#060403]/45 to-[#060403]" />

      {/* Copy */}
      <div className="relative z-10 flex h-full flex-col items-center justify-center px-6 text-center">
        <p className="fade-up font-fell italic text-gold/80 text-sm md:text-base tracking-[0.3em] uppercase">
          The Art of the Pipe
        </p>
        <h1 className="fade-up-1 font-playfair font-bold text-parchment text-5xl sm:text-7xl lg:text-8xl tracking-[0.08em] mt-6">
          FARIDUNHILL
        </h1>
        <p className="fade-up-2 font-lora text-parchment/60 text-sm md:text-base tracking-[0.2em] uppercase mt-6">
          Est. 2007 · Hand-Selected Collection
        </p>
        <Link
          href="/shop"
          className="fade-up-3 mt-10 inline-block border border-gold/60 px-10 py-4 font-lora text-gold text-xs tracking-[0.25em] uppercase transition-colors duration-300 hover:bg-gold hover:text-mahogany-dark"
        >
          Explore Collection
        </Link>
      </div>

      {/* Scroll cue */}
      <div className="absolute bottom-8 left-1/2 z-10 -translate-x-1/2 text-center">
        <p className="font-lora text-parchment/40 text-[10px] tracking-[0.3em] uppercase mb-2">Scroll</p>
        <div className="scroll-cue mx-auto h-8 w-px bg-gold/50" />
      </div>
    </section>
  )
}
