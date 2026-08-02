import type { Metadata } from 'next'
import Link from 'next/link'
import { getHoldings } from '@/lib/references'

export const metadata: Metadata = {
  title: 'Our References — the archive behind every entry',
  description:
    'The reference library our dating work is checked against: manufacturers’ catalogues, trade price lists, books, periodicals, period advertising and mirrored reference sites. We publish what we hold; we never republish it.',
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div className="text-center">
      <div className="font-playfair text-gold text-3xl lg:text-4xl">{value}</div>
      <div className="font-lora text-parchment/45 text-xs tracking-widest uppercase mt-1">{label}</div>
    </div>
  )
}

export default function ReferencesPage() {
  const { totals, mirrors, shelves } = getHoldings()
  const span = totals.dated_span

  return (
    <div className="min-h-screen bg-mahogany">
      {/* ── Header ───────────────────────────────────────────────────────── */}
      <div className="bg-mahogany-dark border-b border-gold/15 py-14 px-6 text-center">
        <span className="font-fell italic text-gold/70 text-sm tracking-widest">~ The Archive ~</span>
        <h1 className="font-playfair font-bold text-parchment text-5xl lg:text-6xl mt-3">Our References</h1>
        <div className="ornament-divider max-w-xs mx-auto mt-5 mb-4">
          <span className="ornament-divider-symbol text-gold">❧</span>
        </div>
        <p className="font-lora text-parchment/55 max-w-2xl mx-auto text-base leading-relaxed">
          Every dating bracket we publish is checked against something. This is that something —
          the catalogues, price lists, books, periodicals and advertisements held in our library,
          listed openly so you can see exactly what our answers rest on.
        </p>
      </div>

      {/* ── Totals ───────────────────────────────────────────────────────── */}
      <div className="border-b border-gold/10 py-10 px-6">
        <div className="max-w-4xl mx-auto grid grid-cols-2 lg:grid-cols-4 gap-8">
          <Stat value={totals.catalogued_items.toLocaleString()} label="Catalogued holdings" />
          <Stat value={totals.files.toLocaleString()} label="Files in the archive" />
          <Stat value={`${totals.gigabytes} GB`} label="Held on disk" />
          <Stat value={span ? `${span[0]}–${span[1]}` : '—'} label="Dated span" />
        </div>
      </div>

      <div className="max-w-screen-lg mx-auto px-6 lg:px-12 py-14">
        {/* ── The two rules ──────────────────────────────────────────────── */}
        <div className="border border-gold/20 bg-mahogany-dark/40 rounded-sm p-7 mb-16">
          <h2 className="font-playfair text-gold text-xl mb-3">How to read this list</h2>
          <ul className="font-lora text-parchment/65 text-sm leading-relaxed space-y-2.5">
            <li>
              <strong className="text-parchment/90">We publish what we hold — never the pages themselves.</strong>{' '}
              Copyright in these works belongs to their authors, publishers and the houses that
              printed them. We cite them; we do not redistribute them. Nothing on this page links
              to a scan, and nothing on this site serves one.
            </li>
            <li>
              <strong className="text-parchment/90">A holding is not a claim.</strong> Owning a
              catalogue does not date your pipe. It means that when we give a bracket, we can tell
              you which page it came from — and when the archive is silent, we say so instead of
              guessing.
            </li>
            <li>
              <strong className="text-parchment/90">The list only grows.</strong> It is generated
              directly from the archive index, so it is never out of date and never flattering.
            </li>
          </ul>
        </div>

        {/* ── Mirrored sites ─────────────────────────────────────────────── */}
        {mirrors.length > 0 && (
          <section className="mb-16">
            <h2 className="font-playfair text-parchment text-2xl lg:text-3xl">Mirrored reference sites</h2>
            <p className="font-lora text-parchment/45 text-sm mt-2 mb-6 max-w-2xl">
              Held so the knowledge survives the source. Kept for reference and cross-checking only.
            </p>
            <div className="grid sm:grid-cols-2 gap-4">
              {mirrors.map((m) => (
                <div key={m.key} className="border border-gold/15 rounded-sm p-5 bg-mahogany-dark/30">
                  <div className="font-playfair text-gold text-lg">{m.title}</div>
                  <div className="font-lora text-parchment/40 text-xs mt-1 tracking-wide">
                    {m.files.toLocaleString()} files · {m.gigabytes} GB
                  </div>
                  <p className="font-lora text-parchment/60 text-sm mt-3 leading-relaxed">{m.note}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* ── The shelves ────────────────────────────────────────────────── */}
        {shelves.map((shelf) => (
          <section key={shelf.key} className="mb-16">
            <div className="flex items-baseline justify-between gap-4 border-b border-gold/15 pb-3">
              <h2 className="font-playfair text-parchment text-2xl lg:text-3xl">{shelf.title}</h2>
              <span className="font-lora text-gold/60 text-sm shrink-0">{shelf.items.length}</span>
            </div>
            <p className="font-lora text-parchment/45 text-sm mt-3 mb-6 max-w-2xl">{shelf.blurb}</p>

            <ul className="divide-y divide-gold/10">
              {shelf.items.map((item) => (
                <li key={item.title} className="py-2.5 flex items-baseline gap-4">
                  <span className="font-lora text-gold/70 text-sm w-14 shrink-0 tabular-nums">
                    {item.year ?? '—'}
                  </span>
                  <span className="font-lora text-parchment/80 text-[15px] leading-snug flex-1">
                    {item.title}
                  </span>
                  <span className="font-lora text-parchment/30 text-xs shrink-0 tracking-wide">
                    {item.pages ? `${item.pages} sheets` : item.format}
                  </span>
                </li>
              ))}
            </ul>
          </section>
        ))}

        {/* ── Footer note ────────────────────────────────────────────────── */}
        <div className="border-t border-gold/15 pt-8 text-center">
          <p className="font-lora text-parchment/45 text-sm max-w-2xl mx-auto leading-relaxed">
            Something missing? If you hold a catalogue, price list or advertisement that is not on
            this list, we would like to hear about it — an archive is built by the people who kept
            the paper.
          </p>
          <Link
            href="/contact"
            className="inline-block mt-5 border border-gold/40 text-gold hover:bg-gold/10 font-playfair px-6 py-2.5 rounded-sm text-sm tracking-wide transition-colors"
          >
            Tell us what you have →
          </Link>
        </div>
      </div>
    </div>
  )
}
