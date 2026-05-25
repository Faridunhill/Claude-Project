'use client'

import { useState, useEffect } from 'react'
import { usePathname } from 'next/navigation'
import Logo from '@/components/ui/Logo'

const STORAGE_KEY = 'fh-age-verified'

export default function AgeGate() {
  const pathname = usePathname()
  const [show, setShow] = useState(false)

  useEffect(() => {
    if (pathname?.startsWith('/studio')) return
    try {
      if (!sessionStorage.getItem(STORAGE_KEY)) {
        setShow(true)
      }
    } catch {
      // sessionStorage unavailable (private browsing edge case) — show gate
      setShow(true)
    }
  }, [pathname])

  function handleConfirm() {
    try {
      sessionStorage.setItem(STORAGE_KEY, '1')
    } catch {}
    setShow(false)
  }

  function handleDeny() {
    // Redirect away — standard practice for age-gated tobacco sites
    window.location.href = 'https://www.google.com'
  }

  if (!show) return null

  return (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center p-4"
      style={{ background: 'rgba(10, 8, 6, 0.97)' }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="age-gate-title"
    >
      {/* Backdrop texture */}
      <div
        className="absolute inset-0 pointer-events-none opacity-30"
        style={{
          backgroundImage:
            'repeating-linear-gradient(87deg, transparent, transparent 2px, rgba(201,168,76,0.03) 2px, rgba(201,168,76,0.03) 4px)',
        }}
      />

      <div className="relative w-full max-w-md text-center">
        {/* Outer ornamental border */}
        <div className="border border-gold/30 rounded-sm p-10 bg-mahogany shadow-mahogany">
          {/* Corner flourishes */}
          <span className="absolute top-4 left-4 text-gold/40 font-fell text-lg">❦</span>
          <span className="absolute top-4 right-4 text-gold/40 font-fell text-lg" style={{ transform: 'scaleX(-1)' }}>❦</span>
          <span className="absolute bottom-4 left-4 text-gold/30 text-sm">✦</span>
          <span className="absolute bottom-4 right-4 text-gold/30 text-sm">✦</span>

          {/* Logo */}
          <div className="flex justify-center mb-8">
            <Logo size="md" variant="light" />
          </div>

          {/* Divider */}
          <div className="h-px bg-gradient-to-r from-transparent via-gold/40 to-transparent mb-8" />

          {/* Headline */}
          <h1
            id="age-gate-title"
            className="font-playfair font-bold text-parchment text-2xl leading-snug mb-3"
          >
            Age Verification Required
          </h1>

          <p className="font-fell italic text-gold/70 text-base mb-6">
            This website contains tobacco products.
          </p>

          <p className="font-lora text-parchment/65 text-sm leading-relaxed mb-8">
            You must be <strong className="text-parchment">21 years of age or older</strong> to
            enter this site. By continuing, you confirm that you are of legal age to purchase
            tobacco products in your jurisdiction.
          </p>

          {/* Buttons */}
          <div className="flex flex-col sm:flex-row gap-3">
            <button
              onClick={handleConfirm}
              className="btn-gold flex-1 py-4 rounded-sm font-playfair font-bold text-sm tracking-widest uppercase"
            >
              Yes, I am 21 or Older
            </button>
            <button
              onClick={handleDeny}
              className="btn-ghost flex-1 py-4 rounded-sm font-playfair font-bold text-sm tracking-widest uppercase"
            >
              No, Exit
            </button>
          </div>

          {/* Legal note */}
          <p className="font-lora text-parchment/30 text-xs mt-6 leading-relaxed">
            By entering this site you agree to our{' '}
            <a href="/privacy" className="underline hover:text-parchment/50 transition-colors">
              Privacy Policy
            </a>{' '}
            and confirm you are of legal smoking age. This site uses session storage to remember
            your response for the duration of your visit.
          </p>
        </div>
      </div>
    </div>
  )
}
