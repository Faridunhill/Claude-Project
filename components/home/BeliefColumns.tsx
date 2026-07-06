import Link from 'next/link'

const COLUMNS = [
  {
    title: 'The Belief',
    body: 'Faridunhill was born from a single conviction: that the pipe is not merely an object, but a ritual. A daily ceremony that demands presence, patience, and a profound reverence for craft. We do not sell accessories. We sell heirlooms.',
  },
  {
    title: 'The Curation',
    body: "Every piece in our collection has passed through Farid's hands. Not figuratively — literally. He fills each bowl, feels each stem, holds each weight. If he would not smoke it himself, it does not make the shelf. This is not a catalogue. It is a curation.",
  },
  {
    title: 'The Source',
    body: 'We source estate pieces and craftsman work from those who spent lifetimes perfecting their art — briar workshops of Europe, meerschaum carvers of Eskişehir, leather makers of the old school. No middlemen. No compromises. No shortcuts. Ever.',
  },
]

export default function BeliefColumns() {
  return (
    <section className="bg-[#0d0a07] py-24 md:py-32">
      <div className="mx-auto max-w-screen-xl px-6 lg:px-12">
        <div className="mb-16 text-center">
          <h2 className="font-playfair font-bold text-parchment text-3xl md:text-4xl">
            Built on one man&apos;s refusal to compromise.
          </h2>
        </div>
        <div className="grid gap-12 md:grid-cols-3 md:gap-10">
          {COLUMNS.map((col) => (
            <div key={col.title} className="text-center md:text-left">
              <p className="font-fell italic text-gold/70 text-sm tracking-[0.2em] uppercase">
                {col.title}
              </p>
              <div className="mx-auto mt-4 h-px w-10 bg-gold/40 md:mx-0" />
              <p className="font-lora text-parchment/55 leading-relaxed mt-6">{col.body}</p>
            </div>
          ))}
        </div>
        <div className="mt-16 text-center">
          <Link
            href="/about"
            className="nav-link-underline font-lora text-gold text-xs tracking-[0.25em] uppercase"
          >
            Read Our Full Story
          </Link>
        </div>
      </div>
    </section>
  )
}
