'use client'

import { useMemo, useState } from 'react'
import { RULES, MAX_SCORE, PUBLISH_THRESHOLD } from '@/lib/listing-standard.mjs'

type Rule = { id: string; section: string; label: string; weight: number; blocking: boolean }

const SECTION_ORDER = ['Attribution', 'Condition', 'Measurement', 'Photography', 'Description', 'Provenance']

/**
 * The free self-check. Any seller, on any venue, can run a listing through this
 * and see where it stands. Nothing is sent anywhere — it runs in the browser.
 */
export default function SelfCheck() {
  const rules = RULES as Rule[]
  const [ticked, setTicked] = useState<Record<string, boolean>>({})

  const { score, blockingFails } = useMemo(() => {
    const earned = rules.filter((r) => ticked[r.id]).reduce((s, r) => s + r.weight, 0)
    return {
      score: Math.round((earned / MAX_SCORE) * 100),
      blockingFails: rules.filter((r) => r.blocking && !ticked[r.id]),
    }
  }, [rules, ticked])

  const publishable = blockingFails.length === 0 && score >= PUBLISH_THRESHOLD

  return (
    <div className="gold-frame bg-mahogany-dark/60 rounded-sm p-6 lg:p-8">
      <div className="flex flex-wrap items-baseline justify-between gap-4 border-b border-gold/15 pb-5 mb-6">
        <div>
          <h3 className="font-playfair font-bold text-parchment text-2xl">Score your listing</h3>
          <p className="font-lora text-parchment/50 text-sm mt-1">
            Tick what your listing already does. Nothing leaves your browser.
          </p>
        </div>
        <div className="text-right">
          <div className="font-playfair font-bold text-4xl text-gold leading-none">{score}<span className="text-parchment/30 text-xl"> / 100</span></div>
          <div className={`font-fell italic text-sm mt-1 ${publishable ? 'text-hunter-light' : 'text-parchment/45'}`}>
            {publishable
              ? 'Meets the standard'
              : blockingFails.length > 0
                ? `${blockingFails.length} required rule${blockingFails.length === 1 ? '' : 's'} unmet`
                : `Below the ${PUBLISH_THRESHOLD} threshold`}
          </div>
        </div>
      </div>

      <div className="space-y-7">
        {SECTION_ORDER.map((section) => {
          const inSection = rules.filter((r) => r.section === section)
          if (!inSection.length) return null
          return (
            <div key={section}>
              <h4 className="font-fell italic text-gold/70 text-sm tracking-widest mb-3">~ {section} ~</h4>
              <ul className="space-y-2">
                {inSection.map((r) => (
                  <li key={r.id}>
                    <label className="flex items-start gap-3 cursor-pointer group">
                      <input
                        type="checkbox"
                        checked={Boolean(ticked[r.id])}
                        onChange={(e) => setTicked((t) => ({ ...t, [r.id]: e.target.checked }))}
                        className="mt-1 h-4 w-4 accent-gold shrink-0"
                      />
                      <span className="font-lora text-parchment/75 text-[0.97rem] leading-relaxed group-hover:text-parchment">
                        {r.label}
                        {r.blocking && (
                          <span className="font-fell italic text-gold/60 text-xs ml-2 whitespace-nowrap">required</span>
                        )}
                        <span className="text-parchment/25 text-xs ml-2">{r.weight} pts</span>
                      </span>
                    </label>
                  </li>
                ))}
              </ul>
            </div>
          )
        })}
      </div>

      <p className="font-lora text-parchment/40 text-sm mt-8 pt-5 border-t border-gold/10">
        A listing that fails a required rule does not meet the standard at any score. We publish
        our own catalogue&rsquo;s score under the same rules — including the listings that fail.
      </p>
    </div>
  )
}
