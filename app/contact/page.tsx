'use client'

import { useState } from 'react'

export default function ContactPage() {
  const [formData, setFormData] = useState({ name: '', email: '', subject: '', message: '' })
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setStatus('loading')
    /* In production, wire this to an email API (Resend, SendGrid, etc.) */
    setTimeout(() => setStatus('success'), 1200)
  }

  return (
    <div className="min-h-screen bg-mahogany">
      <div className="bg-mahogany-dark border-b border-gold/15 py-12">
        <div className="max-w-screen-lg mx-auto px-6 lg:px-12">
          <span className="font-fell italic text-gold/70 text-sm tracking-widest">~ We&apos;d Love to Hear From You ~</span>
          <h1 className="font-playfair font-bold text-parchment text-4xl mt-2">Contact Us</h1>
        </div>
      </div>

      <div className="max-w-screen-lg mx-auto px-6 lg:px-12 py-14 grid lg:grid-cols-2 gap-12">
        {/* Contact info */}
        <div className="space-y-8">
          <div>
            <h2 className="font-playfair font-bold text-parchment text-2xl mb-4">Get in Touch</h2>
            <p className="font-lora text-parchment/70 leading-relaxed text-base">
              Whether you have a question about a product, need advice on choosing your first pipe,
              want to enquire about a specific estate pipe, or simply wish to discuss tobacco —
              we are here. Our head tobacconist reads every message personally and responds to
              each one.
            </p>
          </div>

          <div className="space-y-5">
            {[
              { label: 'General Enquiries', value: 'contact@faridunhill.com' },
              { label: 'Orders & Shipping', value: 'orders@faridunhill.com' },
              { label: 'Returns', value: 'returns@faridunhill.com' },
            ].map((c) => (
              <div key={c.label} className="bg-mahogany-light rounded-sm p-4 border border-gold/10">
                <p className="font-playfair text-gold/70 text-xs uppercase tracking-widest mb-1">{c.label}</p>
                <a href={`mailto:${c.value}`} className="font-lora text-parchment hover:text-gold transition-colors">
                  {c.value}
                </a>
              </div>
            ))}
          </div>

          <div className="bg-mahogany-light rounded-sm p-5 border border-gold/10">
            <h3 className="font-playfair font-semibold text-parchment mb-3">Business Hours</h3>
            <div className="space-y-1 font-lora text-parchment/65 text-sm">
              <div className="flex justify-between"><span>Monday – Friday</span><span>9:00 AM – 6:00 PM EST</span></div>
              <div className="flex justify-between"><span>Saturday</span><span>10:00 AM – 4:00 PM EST</span></div>
              <div className="flex justify-between"><span>Sunday</span><span>Closed</span></div>
            </div>
            <p className="font-lora text-parchment/40 text-xs mt-3">
              We aim to respond to all enquiries within one business day.
            </p>
          </div>

          {/* Pull quote */}
          <blockquote className="border-l-2 border-gold/40 pl-5 py-1">
            <p className="font-fell italic text-parchment/60 text-lg leading-relaxed">
              &ldquo;There is no question too simple, and no pipe too obscure. Ask us anything.&rdquo;
            </p>
            <footer className="font-lora text-gold/50 text-xs mt-2 uppercase tracking-wider">— F. Dunhill, Founder</footer>
          </blockquote>
        </div>

        {/* Form */}
        <div className="bg-mahogany-light rounded-sm gold-frame p-8">
          <h2 className="font-playfair font-bold text-parchment text-xl mb-6">Send a Message</h2>

          {status === 'success' ? (
            <div className="text-center py-10">
              <div className="text-gold text-4xl mb-4">✦</div>
              <p className="font-playfair font-semibold text-parchment text-xl mb-2">Message Received</p>
              <p className="font-lora text-parchment/60 text-sm">
                Thank you for writing. We will respond within one business day.
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              {[
                { name: 'name', label: 'Your Name', type: 'text', placeholder: 'John Smith', required: true },
                { name: 'email', label: 'Email Address', type: 'email', placeholder: 'john@example.com', required: true },
              ].map((field) => (
                <div key={field.name}>
                  <label htmlFor={field.name} className="block font-playfair text-parchment text-sm font-semibold mb-1.5 tracking-wide">
                    {field.label} {field.required && <span className="text-gold">*</span>}
                  </label>
                  <input
                    id={field.name}
                    name={field.name}
                    type={field.type}
                    required={field.required}
                    placeholder={field.placeholder}
                    value={(formData as Record<string, string>)[field.name]}
                    onChange={handleChange}
                    className="w-full bg-mahogany border border-gold/20 rounded-sm px-4 py-3 font-lora text-parchment text-sm placeholder-parchment/25 focus:outline-none focus:border-gold/50 focus:ring-1 focus:ring-gold/20 transition-colors"
                  />
                </div>
              ))}

              <div>
                <label htmlFor="subject" className="block font-playfair text-parchment text-sm font-semibold mb-1.5 tracking-wide">
                  Subject <span className="text-gold">*</span>
                </label>
                <select
                  id="subject"
                  name="subject"
                  required
                  value={formData.subject}
                  onChange={handleChange}
                  className="w-full bg-mahogany border border-gold/20 rounded-sm px-4 py-3 font-lora text-parchment text-sm focus:outline-none focus:border-gold/50 transition-colors"
                >
                  <option value="">Select a subject...</option>
                  <option value="product">Product Question</option>
                  <option value="order">Order Enquiry</option>
                  <option value="estate">Estate Pipe Enquiry</option>
                  <option value="advice">Pipe Smoking Advice</option>
                  <option value="return">Return or Exchange</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label htmlFor="message" className="block font-playfair text-parchment text-sm font-semibold mb-1.5 tracking-wide">
                  Message <span className="text-gold">*</span>
                </label>
                <textarea
                  id="message"
                  name="message"
                  required
                  rows={5}
                  placeholder="Tell us what you need..."
                  value={formData.message}
                  onChange={handleChange}
                  className="w-full bg-mahogany border border-gold/20 rounded-sm px-4 py-3 font-lora text-parchment text-sm placeholder-parchment/25 focus:outline-none focus:border-gold/50 focus:ring-1 focus:ring-gold/20 transition-colors resize-none"
                />
              </div>

              <button
                type="submit"
                disabled={status === 'loading'}
                className="btn-gold w-full py-4 rounded-sm font-playfair font-bold text-sm tracking-widest uppercase disabled:opacity-60"
              >
                {status === 'loading' ? 'Sending...' : 'Send Message'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
