'use client'

import { useEffect, useRef, useState } from 'react'
import { useCurrency } from '@/context/CurrencyContext'
import { BASE_CURRENCY, CURRENCIES, getCurrency } from '@/lib/currency'

export default function CurrencySelector({ className = '' }: { className?: string }) {
  const { currency, setCurrency } = useCurrency()
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false)
    }
    document.addEventListener('mousedown', onClick)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('mousedown', onClick)
      document.removeEventListener('keydown', onKey)
    }
  }, [open])

  const active = getCurrency(currency)

  return (
    <div ref={ref} className={`relative ${className}`}>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-label={`Change currency, currently ${active.label}`}
        className="font-lora text-xs uppercase tracking-widest text-parchment/60 hover:text-gold transition-colors px-2 py-1"
      >
        {active.symbol} {active.code}
      </button>

      {open && (
        <div
          role="listbox"
          className="absolute right-0 mt-1 z-50 min-w-[13rem] bg-mahogany-light border border-gold/25 rounded-sm shadow-xl py-1"
        >
          {CURRENCIES.map((c) => (
            <button
              key={c.code}
              role="option"
              aria-selected={c.code === currency}
              onClick={() => {
                setCurrency(c.code)
                setOpen(false)
              }}
              className={`w-full text-left px-3 py-2 font-lora text-xs tracking-wide transition-colors hover:bg-gold/10 ${
                c.code === currency ? 'text-gold' : 'text-parchment/70'
              }`}
            >
              <span className="inline-block w-10">{c.symbol}</span>
              {c.label}
            </button>
          ))}
          {currency !== BASE_CURRENCY && (
            <p className="px-3 pt-2 pb-1 font-lora text-[0.65rem] leading-snug text-parchment/40 border-t border-gold/15 mt-1">
              Indicative only — you will be charged in {BASE_CURRENCY}.
            </p>
          )}
        </div>
      )}
    </div>
  )
}
