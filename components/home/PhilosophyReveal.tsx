'use client'

import { useEffect, useRef, useState } from 'react'

const WORDS =
  'Every pipe is a conversation between the craftsman and the flame — a partnership forged in patience, perfected in silence.'.split(
    ' '
  )

export default function PhilosophyReveal() {
  const sectionRef = useRef<HTMLElement>(null)
  const [litCount, setLitCount] = useState(0)

  useEffect(() => {
    const onScroll = () => {
      const el = sectionRef.current
      if (!el) return
      const rect = el.getBoundingClientRect()
      const viewport = window.innerHeight
      // 0 when the section top reaches the viewport bottom, 1 when its bottom nears the top third
      const progress = (viewport - rect.top) / (viewport + rect.height * 0.6)
      const clamped = Math.min(1, Math.max(0, progress * 1.4 - 0.2))
      setLitCount(Math.round(clamped * WORDS.length))
    }
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <section ref={sectionRef} className="bg-[#060403] py-32 md:py-44">
      <div className="mx-auto max-w-4xl px-6 text-center">
        <p className="font-fell italic text-gold/60 text-sm tracking-[0.3em] uppercase mb-12">
          The Faridunhill Philosophy
        </p>
        <p className="font-playfair text-3xl md:text-5xl leading-snug md:leading-snug">
          {WORDS.map((word, i) => (
            <span
              key={i}
              className="transition-colors duration-500"
              style={{ color: i < litCount ? '#F5EDD6' : 'rgba(245, 237, 214, 0.15)' }}
            >
              {word}{' '}
            </span>
          ))}
        </p>
        <p className="font-lora text-gold/70 text-sm tracking-[0.25em] uppercase mt-14">
          Farid · Founder
        </p>
      </div>
    </section>
  )
}
