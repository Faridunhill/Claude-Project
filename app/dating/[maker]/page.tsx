import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import { getAllCabinets, getCabinetBySlug, weightMeta, type Confidence } from '@/lib/dating'

interface Props {
  params: { maker: string }
}

export async function generateStaticParams() {
  const cabinets = await getAllCabinets()
  return cabinets.map((c) => ({ maker: c.maker }))
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const cabinet = await getCabinetBySlug(params.maker)
  if (!cabinet) return {}
  return {
    title: `Dating ${cabinet.displayName}`,
    description: cabinet.summary,
  }
}

const confidenceStyle: Record<Confidence, string> = {
  high: 'bg-hunter/40 text-parchment border-hunter-light/50',
  medium: 'bg-gold/15 text-gold-pale border-gold/40',
  low: 'bg-smoke/20 text-parchment/60 border-smoke-light/40',
}

const weightStyle = {
  primary: 'bg-gold/20 text-gold-pale border-gold/50',
  precision: 'bg-hunter/40 text-parchment border-hunter-light/50',
  corroborating: 'bg-smoke/20 text-parchment/60 border-smoke-light/40',
}

export default async function CabinetPage({ params }: Props) {
  const cabinet = await getCabinetBySlug(params.maker)
  if (!cabinet) notFound()

  return (
    <div className="min-h-screen bg-mahogany">
      {/* Hero */}
      <div className="bg-mahogany-dark border-b border-gold/15 py-14">
        <div className="max-w-screen-xl mx-auto px-6 lg:px-12">
          <nav className="flex items-center gap-2 text-xs font-lora text-parchment/40 mb-6">
            <Link href="/" className="hover:text-gold transition-colors">Home</Link>
            <span>/</span>
            <Link href="/dating" className="hover:text-gold transition-colors">Dating Directory</Link>
            <span>/</span>
            <span className="text-parchment/70">{cabinet.displayName}</span>
          </nav>

          <span className="font-fell italic text-gold/70 text-sm tracking-widest">
            ~ Dating Cabinet ~
          </span>
          <h1 className="font-playfair font-bold text-parchment text-4xl lg:text-5xl mt-2 mb-3">
            {cabinet.displayName}
          </h1>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 font-lora text-sm text-parchment/50 mb-5">
            {cabinet.country && <span>{cabinet.country}</span>}
            {cabinet.founded && <span>· est. {cabinet.founded}</span>}
            {cabinet.aka.length > 0 && <span>· a.k.a. {cabinet.aka.join(', ')}</span>}
          </div>
          <p className="font-lora text-parchment/65 text-base max-w-3xl leading-relaxed">
            {cabinet.summary}
          </p>
        </div>
      </div>

      <div className="max-w-screen-xl mx-auto px-6 lg:px-12 py-14 space-y-14">
        {/* How to use */}
        {cabinet.howToUse && (
          <section className="rounded-lg border border-gold/20 bg-mahogany-light/40 p-6 lg:p-8">
            <h2 className="font-playfair text-gold text-xl mb-3">How to read this cabinet</h2>
            <p className="font-lora text-parchment/70 leading-relaxed">{cabinet.howToUse}</p>
          </section>
        )}

        {/* Quick flow */}
        {cabinet.quickFlow.length > 0 && (
          <section>
            <h2 className="font-playfair text-parchment text-2xl mb-6">The quick flow</h2>
            <ol className="space-y-4">
              {cabinet.quickFlow.map((step, i) => (
                <li key={i} className="flex gap-4">
                  <span className="flex-shrink-0 flex items-center justify-center w-9 h-9 rounded-full border border-gold/40 bg-mahogany-light font-playfair text-gold">
                    {i + 1}
                  </span>
                  <p className="font-lora text-parchment/70 leading-relaxed pt-1">{step}</p>
                </li>
              ))}
            </ol>
          </section>
        )}

        {/* Markers */}
        <section>
          <h2 className="font-playfair text-parchment text-2xl mb-2">The markers</h2>
          <p className="font-lora text-parchment/45 text-sm mb-8">
            Read top to bottom. Each marker is one question, where to look, and how to
            read what you find.
          </p>

          <div className="space-y-6">
            {cabinet.markers.map((m) => (
              <article
                key={m.id}
                className="rounded-lg border border-gold/15 bg-mahogany-light/30 overflow-hidden"
              >
                <header className="border-b border-gold/10 p-6">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <span className="font-playfair text-gold/50 text-lg">
                          {String(m.priority).padStart(2, '0')}
                        </span>
                        <span
                          className={`inline-block rounded-full border px-2.5 py-0.5 text-[11px] font-lora uppercase tracking-wider ${weightStyle[m.weight]}`}
                          title={weightMeta[m.weight].blurb}
                        >
                          {weightMeta[m.weight].label}
                        </span>
                      </div>
                      <h3 className="font-playfair text-parchment text-xl">{m.label}</h3>
                    </div>
                  </div>
                  <p className="font-lora text-parchment/75 mt-3 leading-relaxed">
                    <span className="text-gold/70">Q. </span>{m.question}
                  </p>
                  {m.whereToLook && (
                    <p className="font-lora text-parchment/45 text-sm mt-2 leading-relaxed">
                      <span className="font-fell italic text-gold/50">Where to look — </span>
                      {m.whereToLook}
                    </p>
                  )}
                </header>

                <ul className="divide-y divide-gold/10">
                  {m.readings.map((r, i) => (
                    <li key={i} className="p-6 grid gap-3 md:grid-cols-[1fr_auto]">
                      <div>
                        <p className="font-lora text-parchment/85">
                          <span className="text-parchment/45">If it reads — </span>
                          {r.reads}
                        </p>
                        <p className="font-playfair text-gold text-lg mt-1">{r.indicates}</p>
                        {r.note && (
                          <p className="font-lora text-parchment/45 text-sm mt-2 leading-relaxed">
                            {r.note}
                          </p>
                        )}
                      </div>
                      <div className="md:text-right">
                        <span
                          className={`inline-block rounded-full border px-2.5 py-0.5 text-[11px] font-lora uppercase tracking-wider ${confidenceStyle[r.confidence]}`}
                        >
                          {r.confidence} confidence
                        </span>
                      </div>
                    </li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
        </section>

        {/* Sources */}
        {cabinet.sources.length > 0 && (
          <section className="border-t border-gold/15 pt-8">
            <h2 className="font-playfair text-parchment/70 text-lg mb-4">Sources</h2>
            <ul className="space-y-2">
              {cabinet.sources.map((s, i) => (
                <li key={i} className="font-lora text-parchment/45 text-sm leading-relaxed">
                  {s}
                </li>
              ))}
            </ul>
            <p className="font-lora text-parchment/30 text-xs mt-6 max-w-2xl leading-relaxed">
              Year boundaries encode collector consensus, not certainty. A hallmark or
              patent number overrides any stamp-based estimate. This directory is a
              research aid, not an appraisal or certificate of authenticity.
            </p>
          </section>
        )}
      </div>
    </div>
  )
}
