'use client'

import { useState } from 'react'

export default function NewsletterSection() {
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setStatus('loading')

    try {
      const res = await fetch('/api/newsletter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, phone }),
      })
      const data = await res.json()

      if (res.ok) {
        setStatus('success')
        setMessage('Welcome to the Gentleman\'s Circle. Your first letter arrives shortly.')
        setEmail('')
        setPhone('')
      } else {
        setStatus('error')
        setMessage(data.error || 'Something went wrong. Please try again.')
      }
    } catch {
      setStatus('error')
      setMessage('Unable to subscribe at this time. Please try again later.')
    }
  }

  return (
    <section className="bg-parchment-texture relative py-24">
      <div className="max-w-screen-md mx-auto px-6 lg:px-12">
        {/* Ornate outer frame */}
        <div className="relative border border-leather/30 rounded-sm p-10 lg:p-14">
          {/* Corner flourishes */}
          <span className="absolute top-3 left-3 text-leather/40 text-lg font-fell">❦</span>
          <span className="absolute top-3 right-3 text-leather/40 text-lg font-fell" style={{ transform: 'scaleX(-1)' }}>❦</span>
          <span className="absolute bottom-3 left-3 text-leather/40 text-sm font-fell">✦</span>
          <span className="absolute bottom-3 right-3 text-leather/40 text-sm font-fell">✦</span>

          {/* Content */}
          <div className="text-center mb-10">
            <span className="font-fell italic text-leather text-sm tracking-widest">~ Join Us ~</span>
            <h2 className="font-playfair font-bold text-mahogany text-3xl lg:text-4xl mt-3 leading-tight">
              Join the Gentleman's Circle
            </h2>
            <div className="ornament-divider mt-5 mb-6">
              <span className="ornament-divider-symbol text-leather text-base">❧</span>
            </div>
            <p className="font-lora text-mahogany/70 text-base leading-relaxed max-w-md mx-auto">
              Receive our weekly letter — new arrivals, tobacco reviews, collector's notes, and
              occasional exclusive offers available only to subscribers.
            </p>
          </div>

          {status === 'success' ? (
            <div className="text-center py-8">
              <div className="text-gold text-4xl mb-4">✦</div>
              <p className="font-playfair font-semibold text-mahogany text-xl mb-2">
                Welcome to the Circle.
              </p>
              <p className="font-lora text-mahogany/70 text-sm">{message}</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Email */}
              <div>
                <label htmlFor="nl-email" className="block font-playfair text-mahogany text-sm font-semibold mb-1.5 tracking-wide">
                  Email Address <span className="text-leather">*</span>
                </label>
                <input
                  id="nl-email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@address.com"
                  className="w-full bg-parchment-dark border border-leather/30 rounded-sm px-4 py-3 font-lora text-mahogany text-sm placeholder-mahogany/30 focus:outline-none focus:border-gold focus:ring-1 focus:ring-gold/30 transition-colors"
                />
              </div>

              {/* Phone — optional */}
              <div>
                <label htmlFor="nl-phone" className="block font-playfair text-mahogany text-sm font-semibold mb-1.5 tracking-wide">
                  Phone Number <span className="font-lora text-mahogany/40 font-normal text-xs">(optional)</span>
                </label>
                <input
                  id="nl-phone"
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+1 (555) 000-0000"
                  className="w-full bg-parchment-dark border border-leather/30 rounded-sm px-4 py-3 font-lora text-mahogany text-sm placeholder-mahogany/30 focus:outline-none focus:border-gold focus:ring-1 focus:ring-gold/30 transition-colors"
                />
                <p className="font-lora text-mahogany/45 text-xs mt-1.5 leading-relaxed">
                  By providing your phone number, you agree to receive occasional SMS messages regarding
                  new arrivals and exclusive offers. Message and data rates may apply. Reply STOP to
                  unsubscribe at any time.
                </p>
              </div>

              {/* Submit */}
              <button
                type="submit"
                disabled={status === 'loading'}
                className="btn-gold w-full py-4 rounded-sm font-playfair font-bold text-sm tracking-widest uppercase mt-2 disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {status === 'loading' ? 'Enrolling...' : 'Join the Circle'}
              </button>

              {status === 'error' && (
                <p className="text-center font-lora text-red-700 text-sm">{message}</p>
              )}

              {/* Privacy note */}
              <p className="font-lora text-mahogany/40 text-xs text-center leading-relaxed">
                We take your privacy seriously. Your information is never sold or shared with third
                parties. Unsubscribe at any time. See our{' '}
                <a href="/privacy" className="underline hover:text-mahogany transition-colors">
                  Privacy Policy
                </a>
                .
              </p>
            </form>
          )}
        </div>
      </div>
    </section>
  )
}
