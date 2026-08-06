import type { Metadata } from 'next'
import SelfCheck from '@/components/standard/SelfCheck'
import {
  CONDITION_GRADES,
  COMPONENTS,
  MEASUREMENTS,
  PHOTO_ROLES,
  PHOTO_RULES,
  ATTRIBUTION_FIELDS,
  SECTIONS,
  STANDARD_VERSION,
  STANDARD_DATE,
  MAX_SCORE,
} from '@/lib/listing-standard.mjs'

export const metadata: Metadata = {
  title: 'The Listing Standard',
  description:
    'A grammar for estate pipe listings: attribution, a seven-grade condition code graded in four parts, six measurements, an eight-photograph sequence, and a description built from the record rather than written.',
}

type Grade = { code: string; label: string; rank: number; short: string; criteria: string[] }
type Field = { key: string; label: string; note?: string }
type Pose = { n: number; key: string; label: string; required: boolean; note: string }
type Section = { name: string; weight: number }

function Rule({ children }: { children: React.ReactNode }) {
  return (
    <p className="font-lora text-parchment/75 leading-[1.95] text-[1.02rem]">{children}</p>
  )
}

function Divider() {
  return (
    <div className="ornament-divider my-14">
      <span className="ornament-divider-symbol text-gold">❧</span>
    </div>
  )
}

export default function StandardPage() {
  const grades = CONDITION_GRADES as Grade[]
  const poses = PHOTO_ROLES as Pose[]

  return (
    <div className="min-h-screen bg-mahogany">
      {/* Masthead */}
      <div className="bg-mahogany-dark border-b border-gold/15 py-16 text-center px-6">
        <span className="font-fell italic text-gold/70 text-sm tracking-widest">~ A reference, freely published ~</span>
        <h1 className="font-playfair font-bold text-parchment text-4xl lg:text-5xl mt-3">
          The Faridunhill Listing Standard
        </h1>
        <p className="font-lora text-parchment/55 mt-5 max-w-2xl mx-auto leading-relaxed">
          A pipe listing should say what the pipe is, what condition it is in, how big it is, and
          show it honestly. No venue in this trade requires any of that. So here is the grammar,
          written down — free to use, free to copy, and we are the first to be judged by it.
        </p>
        <p className="font-fell italic text-gold/50 text-sm mt-6">
          Draft v{STANDARD_VERSION} · {STANDARD_DATE} · {MAX_SCORE} points, normalised to 100
        </p>
      </div>

      <div className="max-w-screen-lg mx-auto px-6 lg:px-12 py-16">

        {/* Why */}
        <section className="space-y-5">
          <h2 className="font-playfair font-bold text-parchment text-3xl">Why this exists</h2>
          <Rule>
            The overwhelming majority of estate pipes in the world change hands on a platform where
            pipes are a rounding error. There is no pipe department there, so there is nobody whose
            job it is to ask a seller for a brand, a chamber depth, or a photograph of the rim. Ten
            pipes can be listed with no maker named at all. A chewed stem can be sold as
            &ldquo;excellent overall.&rdquo;
          </Rule>
          <Rule>
            That is not neglect and it will not be fixed. A form that demands attribution, six
            measurements and eight photographs is friction deliberately added to raise quality and
            lower volume — the opposite of the model that makes a general marketplace work.
          </Rule>
          <Rule>
            So the standard is published here instead, separately from any shop, for any seller on
            any venue to use. It is not a rule anyone can enforce on a stranger. It is a grammar,
            and grammar spreads by being useful.
          </Rule>
        </section>

        <Divider />

        {/* Attribution */}
        <section className="space-y-5">
          <h2 className="font-playfair font-bold text-parchment text-3xl">1 · Attribution</h2>
          <Rule>
            The requirement is not that a pipe carries a famous name. Plenty do not, and an honest
            catalogue is full of unmarked meerschaums and no-name antiques. The requirement is that
            the field is <em className="text-gold/80">answered</em>. <span className="font-fell italic text-gold/70">Unmarked</span> and{' '}
            <span className="font-fell italic text-gold/70">unattributed</span> are complete answers. A
            blank is not, and neither is a title stuffed with four makers the pipe does not carry.
          </Rule>
          <div className="gold-frame bg-mahogany-dark/50 rounded-sm overflow-hidden">
            <table className="w-full text-left">
              <tbody className="divide-y divide-gold/10">
                {(ATTRIBUTION_FIELDS as Field[]).map((f) => (
                  <tr key={f.key}>
                    <td className="font-playfair text-parchment/90 px-5 py-3.5 align-top whitespace-nowrap">{f.label}</td>
                    <td className="font-lora text-parchment/60 px-5 py-3.5 text-[0.95rem]">{f.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Rule>
            <strong className="text-parchment">The stamp transcription is the most valuable line in the
            listing</strong>, and no venue asks for it. Copied literally — line by line, including the parts
            that make no sense — it is what allows a pipe to be dated correctly in ten years by a rule
            that has not been discovered yet. Everything else describes the pipe. This one preserves it.
          </Rule>
          <Rule>
            A date is given as a bracket with the evidence beside it. Where the evidence is thin, the
            honest entry is <span className="font-fell italic text-gold/70">undated</span>. A single year
            requires a hard cliff — a stamp or a documented change that can only mean one year. Absence
            of evidence never dates a pipe.
          </Rule>
        </section>

        <Divider />

        {/* Condition */}
        <section className="space-y-5">
          <h2 className="font-playfair font-bold text-parchment text-3xl">2 · Condition</h2>

          <div className="gold-frame bg-hunter/10 border-l-2 border-gold rounded-sm p-6">
            <p className="font-playfair text-parchment text-xl leading-snug">
              A pipe is graded in four parts — briar, rim, stem, stamps — and the headline grade is the
              <em className="text-gold"> lowest</em> of the four.
            </p>
            <p className="font-lora text-parchment/60 mt-3 text-[0.97rem] leading-relaxed">
              Never an average, never an overall impression. The most common dishonesty in this trade is
              a chewed stem hidden under &ldquo;excellent overall.&rdquo; One rule, and it stops working.
              All four grades are shown, so a buyer sees not only the grade but why.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 gap-3">
            {(COMPONENTS as { key: string; label: string; watches: string }[]).map((c) => (
              <div key={c.key} className="border border-gold/15 rounded-sm px-5 py-4">
                <div className="font-playfair text-parchment">{c.label}</div>
                <div className="font-lora text-parchment/50 text-sm mt-1">{c.watches}</div>
              </div>
            ))}
          </div>

          <Rule>
            Stamps are graded because in this category the stamp is a large part of the value, and
            nobody grades it.
          </Rule>

          <div className="space-y-3 mt-4">
            {grades.map((g) => (
              <details key={g.code} className="gold-frame bg-mahogany-dark/50 rounded-sm group">
                <summary className="cursor-pointer px-5 py-4 flex items-baseline gap-4 list-none">
                  <span className="font-playfair font-bold text-gold text-lg w-40 shrink-0">{g.label}</span>
                  <span className="font-lora text-parchment/65 text-[0.97rem]">{g.short}</span>
                </summary>
                <ul className="px-5 pb-5 pt-1 space-y-1.5 border-t border-gold/10 mt-1">
                  {g.criteria.map((c, i) => (
                    <li key={i} className="font-lora text-parchment/60 text-[0.93rem] leading-relaxed pl-4 relative">
                      <span className="absolute left-0 text-gold/50">·</span>{c}
                    </li>
                  ))}
                </ul>
              </details>
            ))}
          </div>

          <Rule>
            <strong className="text-parchment">Restoration piece</strong> is the seventh rung, and it is
            the one the familiar six-grade ladder is missing. Without it, &ldquo;fair&rdquo; quietly
            absorbs cracked shanks, burnouts and bite-throughs — which is exactly where the category&rsquo;s
            dishonesty lives. With it, fair starts meaning something again.
          </Rule>
          <Rule>
            Four things are declared separately and never folded into a grade, because folding them in is
            how they get lost: smoked or unsmoked · sanitised, with the method stated · refurbished ·
            repaired, naming the repair.
          </Rule>
          <Rule>
            <strong className="text-parchment">And where they disagree, the photograph wins.</strong> A
            grade is the seller&rsquo;s judgment and carries his name. A photograph is a fact. If the two
            contradict each other the listing is corrected, in public, with the correction logged.
          </Rule>
        </section>

        <Divider />

        {/* Measurement */}
        <section className="space-y-5">
          <h2 className="font-playfair font-bold text-parchment text-3xl">3 · Measurement</h2>
          <Rule>
            Six numbers, measured, never estimated from a photograph. They are the only fields in a
            listing that cannot be argued with — and two of them decide how the pipe actually smokes and
            are published almost nowhere.
          </Rule>
          <div className="grid sm:grid-cols-3 gap-3">
            {(MEASUREMENTS as { key: string; label: string; unit: string }[]).map((m) => (
              <div key={m.key} className="border border-gold/15 rounded-sm px-5 py-4 text-center">
                <div className="font-playfair text-parchment text-[0.98rem]">{m.label}</div>
                <div className="font-fell italic text-gold/60 text-sm mt-1">{m.unit}</div>
              </div>
            ))}
          </div>
          <Rule>
            Metric first, imperial in parentheses. Filter size, stem material, mount and hallmark stated.
            A measurement that was not taken is written as <span className="font-fell italic text-gold/70">not
            measured</span> — it is never silently absent, because an absent number reads as a small one.
          </Rule>
        </section>

        <Divider />

        {/* Photography */}
        <section className="space-y-5">
          <h2 className="font-playfair font-bold text-parchment text-3xl">4 · Photography</h2>
          <Rule>
            Eight photographs is the floor: six poses and two stamp close-ups, in a fixed order, never
            dropped or reordered silently. Ten is the ceiling — a listing that needs more is hiding
            something in the pile.
          </Rule>
          <ol className="space-y-2">
            {poses.map((p) => (
              <li key={p.key} className="flex items-baseline gap-4 border-b border-gold/10 pb-2">
                <span className="font-playfair font-bold text-gold/70 w-6 shrink-0">{p.n}</span>
                <span className="font-playfair text-parchment w-56 shrink-0">{p.label}</span>
                <span className="font-lora text-parchment/50 text-sm">
                  {p.note}{!p.required && <span className="font-fell italic text-gold/50"> — optional</span>}
                </span>
              </li>
            ))}
          </ol>
          <div className="gold-frame bg-hunter/10 border-l-2 border-gold rounded-sm p-6 mt-2">
            <p className="font-playfair text-parchment text-lg">
              Any part graded below <em className="text-gold">very good</em> carries its own photograph.
            </p>
            <p className="font-lora text-parchment/60 mt-2 text-[0.97rem]">
              A declared flaw with no picture of it is not a disclosure. It is a hedge.
            </p>
          </div>
          <ul className="space-y-1.5 pt-2">
            {(PHOTO_RULES as string[]).map((r, i) => (
              <li key={i} className="font-lora text-parchment/60 text-[0.95rem] pl-4 relative leading-relaxed">
                <span className="absolute left-0 text-gold/50">·</span>{r}
              </li>
            ))}
          </ul>
        </section>

        <Divider />

        {/* Description */}
        <section className="space-y-5">
          <h2 className="font-playfair font-bold text-parchment text-3xl">5 · The description is derived</h2>
          <Rule>
            The factual part of a description is <strong className="text-parchment">generated from the
            record</strong> — attribution, measurements, grades, declarations. Nobody types it, so nobody
            can contradict a field in it, and it regenerates whenever the record is corrected.
          </Rule>
          <Rule>
            No adjective survives in it that is not backed by a field. <em>Rare</em>, <em>stunning</em>,{' '}
            <em>must-have</em>, <em>investment</em>, <em>flawless</em> and their family do not appear
            among the facts.
          </Rule>
          <Rule>
            Opinion is welcome — below the line, in its own block, signed. Thirty years of looking at
            pipes is worth reading. It is simply not the same kind of statement as a chamber depth, and
            a listing should never blur the two.
          </Rule>
        </section>

        <Divider />

        {/* Scoring */}
        <section className="space-y-5">
          <h2 className="font-playfair font-bold text-parchment text-3xl">6 · Scoring, and our own score</h2>
          <div className="grid sm:grid-cols-3 gap-3">
            {(SECTIONS as Section[]).map((s) => (
              <div key={s.name} className="border border-gold/15 rounded-sm px-5 py-4 flex items-baseline justify-between">
                <span className="font-playfair text-parchment">{s.name}</span>
                <span className="font-fell italic text-gold/70">{s.weight}</span>
              </div>
            ))}
          </div>
          <Rule>
            Some rules are required: a listing that fails one does not meet the standard at any score.
            The rest carry points. <strong className="text-parchment">The score is printed on the listing
            — ours included, and ours especially.</strong> A house that publishes a rule and hides its own
            marks against it has published an advertisement, not a standard.
          </Rule>
        </section>

        <div className="mt-10">
          <SelfCheck />
        </div>

        <p className="font-fell italic text-parchment/35 text-center text-sm mt-14">
          Draft. Published for comment, versioned, with a changelog. Corrections are welcome and are
          recorded with the name of whoever sent them.
        </p>
      </div>
    </div>
  )
}
