'use client'

import { useState } from 'react'

interface PhotoSlot {
  view: string
  label: string
  hint: string
  required: boolean
}

const PHOTO_SLOTS: PhotoSlot[] = [
  { view: 'left', label: 'Left Profile', hint: 'Full pipe from the left side', required: true },
  { view: 'right', label: 'Right Profile', hint: 'Full pipe from the right side', required: true },
  { view: 'top', label: 'Top — Bowl Rim', hint: 'Looking down into the chamber', required: true },
  { view: 'bottom', label: 'Bottom — Heel', hint: 'Underside of bowl and shank', required: true },
  { view: 'stampA', label: 'Stamping Close-up A', hint: 'Nomenclature on the shank, as sharp as possible', required: true },
  { view: 'stampB', label: 'Stamping Close-up B', hint: 'Other side of shank or stem logo (optional)', required: false },
]

const MAX_DIMENSION = 1600
const JPEG_QUALITY = 0.82
const MAX_TOTAL_PHOTO_BYTES = 3.5 * 1024 * 1024

function compressImage(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file)
    const img = new Image()
    img.onload = () => {
      const scale = Math.min(1, MAX_DIMENSION / Math.max(img.width, img.height))
      const canvas = document.createElement('canvas')
      canvas.width = Math.round(img.width * scale)
      canvas.height = Math.round(img.height * scale)
      const ctx = canvas.getContext('2d')
      if (!ctx) {
        URL.revokeObjectURL(url)
        reject(new Error('Canvas unavailable'))
        return
      }
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
      URL.revokeObjectURL(url)
      resolve(canvas.toDataURL('image/jpeg', JPEG_QUALITY))
    }
    img.onerror = () => {
      URL.revokeObjectURL(url)
      reject(new Error('Could not read image'))
    }
    img.src = url
  })
}

const steps = [
  { num: '1', title: 'Photograph', text: 'Take six photos of your pipe following our simple protocol — four angles plus close-ups of the stamping.' },
  { num: '2', title: 'Submit', text: 'Upload the photos with whatever you know: the stamping as you read it, brand guesses, measurements.' },
  { num: '3', title: 'Receive Your Passport', text: 'Farid personally examines every submission and replies with an identification and dating assessment — free of charge.' },
]

export default function PipePassportPage() {
  const [formData, setFormData] = useState({ name: '', email: '', brandGuess: '', stampText: '', length: '', notes: '' })
  const [photos, setPhotos] = useState<Record<string, string>>({})
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [errorMsg, setErrorMsg] = useState('')
  const [referenceId, setReferenceId] = useState('')

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  async function handlePhoto(view: string, file: File | undefined) {
    if (!file) return
    try {
      const data = await compressImage(file)
      setPhotos((prev) => ({ ...prev, [view]: data }))
      setErrorMsg('')
    } catch {
      setErrorMsg('Could not read that image. Please try a different photo.')
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const missing = PHOTO_SLOTS.filter((s) => s.required && !photos[s.view])
    if (missing.length > 0) {
      setErrorMsg(`Please add the required photos: ${missing.map((s) => s.label).join(', ')}.`)
      return
    }
    const photoList = PHOTO_SLOTS.filter((s) => photos[s.view]).map((s) => ({ view: s.view, data: photos[s.view] }))
    const totalBytes = photoList.reduce((sum, p) => sum + Math.floor(p.data.length * 0.75), 0)
    if (totalBytes > MAX_TOTAL_PHOTO_BYTES) {
      setErrorMsg('The photos are too large in total. Please retake the close-ups a little further away and try again.')
      return
    }

    setStatus('loading')
    setErrorMsg('')
    try {
      const res = await fetch('/api/passport', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...formData, photos: photoList }),
      })
      const data = await res.json()
      if (res.ok) {
        setReferenceId(data.referenceId ?? '')
        setStatus('success')
      } else {
        setStatus('error')
        setErrorMsg(data.error || 'Something went wrong. Please try again.')
      }
    } catch {
      setStatus('error')
      setErrorMsg('Unable to submit. Please try again later.')
    }
  }

  return (
    <div className="min-h-screen bg-mahogany">
      {/* Hero */}
      <div className="bg-mahogany-dark border-b border-gold/15 py-14">
        <div className="max-w-screen-lg mx-auto px-6 lg:px-12 text-center">
          <span className="font-fell italic text-gold/70 text-sm tracking-widest">~ Free Identification &amp; Dating Assessment ~</span>
          <h1 className="font-playfair font-bold text-parchment text-4xl lg:text-5xl mt-3">The Pipe Passport</h1>
          <p className="font-lora text-parchment/70 leading-relaxed text-base max-w-2xl mx-auto mt-5">
            Found a pipe in an attic? Inherited a collection? Wondering whether that estate find is
            really what the seller claimed? Send us six photographs and Farid — with thirty-five years
            of collecting and over five thousand pipes sold — will identify it, date it, and tell you
            what he sees. Free, for any collector.
          </p>
        </div>
      </div>

      {/* How it works */}
      <div className="max-w-screen-lg mx-auto px-6 lg:px-12 py-14">
        <div className="grid md:grid-cols-3 gap-6 mb-14">
          {steps.map((step) => (
            <div key={step.num} className="bg-mahogany-light rounded-sm p-6 border border-gold/10">
              <div className="w-9 h-9 rounded-full border border-gold/40 flex items-center justify-center font-playfair font-bold text-gold mb-4">
                {step.num}
              </div>
              <h3 className="font-playfair font-semibold text-parchment text-lg mb-2">{step.title}</h3>
              <p className="font-lora text-parchment/60 text-sm leading-relaxed">{step.text}</p>
            </div>
          ))}
        </div>

        {/* Form */}
        <div className="bg-mahogany-light rounded-sm gold-frame p-8 max-w-3xl mx-auto">
          {status === 'success' ? (
            <div className="text-center py-10">
              <div className="text-gold text-4xl mb-4">✦</div>
              <p className="font-playfair font-semibold text-parchment text-xl mb-2">Submission Received</p>
              {referenceId && (
                <p className="font-playfair text-gold text-lg tracking-widest mb-3">{referenceId}</p>
              )}
              <p className="font-lora text-parchment/60 text-sm max-w-md mx-auto">
                That is your Pipe Passport reference — keep it. Farid will examine your pipe personally
                and reply to your email with his assessment, usually within two to three business days.
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              <h2 className="font-playfair font-bold text-parchment text-xl">Submit Your Pipe</h2>

              {/* Contact fields */}
              <div className="grid sm:grid-cols-2 gap-4">
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
              </div>

              {/* Photo protocol */}
              <div>
                <p className="font-playfair text-parchment text-sm font-semibold tracking-wide mb-1.5">
                  The Six Photographs <span className="text-gold">*</span>
                </p>
                <p className="font-lora text-parchment/50 text-xs mb-4">
                  Natural daylight, plain background, pipe filling the frame. Photos are resized in your
                  browser before upload — full-size originals never leave your device.
                </p>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {PHOTO_SLOTS.map((slot) => (
                    <label
                      key={slot.view}
                      className={`relative block rounded-sm border cursor-pointer overflow-hidden transition-colors ${
                        photos[slot.view] ? 'border-gold/60' : 'border-gold/20 hover:border-gold/40'
                      } bg-mahogany`}
                    >
                      <input
                        type="file"
                        accept="image/*"
                        className="sr-only"
                        onChange={(e) => handlePhoto(slot.view, e.target.files?.[0])}
                      />
                      {photos[slot.view] ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={photos[slot.view]} alt={slot.label} className="w-full h-28 object-cover" />
                      ) : (
                        <div className="h-28 flex flex-col items-center justify-center px-3 text-center">
                          <span className="text-gold/40 text-xl mb-1">+</span>
                          <span className="font-playfair text-parchment/70 text-xs font-semibold">
                            {slot.label}
                            {!slot.required && <span className="text-parchment/40 font-normal"> (optional)</span>}
                          </span>
                        </div>
                      )}
                      <div className="px-2 py-1.5 border-t border-gold/10">
                        <p className="font-lora text-parchment/45 text-[10px] leading-tight">
                          {photos[slot.view] ? `${slot.label} — tap to replace` : slot.hint}
                        </p>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Detail fields */}
              <div className="grid sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="brandGuess" className="block font-playfair text-parchment text-sm font-semibold mb-1.5 tracking-wide">
                    Brand, If Known
                  </label>
                  <input
                    id="brandGuess"
                    name="brandGuess"
                    type="text"
                    placeholder="e.g. Dunhill, Peterson, unknown..."
                    value={formData.brandGuess}
                    onChange={handleChange}
                    className="w-full bg-mahogany border border-gold/20 rounded-sm px-4 py-3 font-lora text-parchment text-sm placeholder-parchment/25 focus:outline-none focus:border-gold/50 focus:ring-1 focus:ring-gold/20 transition-colors"
                  />
                </div>
                <div>
                  <label htmlFor="length" className="block font-playfair text-parchment text-sm font-semibold mb-1.5 tracking-wide">
                    Length
                  </label>
                  <input
                    id="length"
                    name="length"
                    type="text"
                    placeholder='e.g. 5.5" / 14 cm'
                    value={formData.length}
                    onChange={handleChange}
                    className="w-full bg-mahogany border border-gold/20 rounded-sm px-4 py-3 font-lora text-parchment text-sm placeholder-parchment/25 focus:outline-none focus:border-gold/50 focus:ring-1 focus:ring-gold/20 transition-colors"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="stampText" className="block font-playfair text-parchment text-sm font-semibold mb-1.5 tracking-wide">
                  Stamping, As You Read It
                </label>
                <input
                  id="stampText"
                  name="stampText"
                  type="text"
                  placeholder='e.g. "DUNHILL SHELL BRIAR — MADE IN ENGLAND 12" — even partial letters help'
                  value={formData.stampText}
                  onChange={handleChange}
                  className="w-full bg-mahogany border border-gold/20 rounded-sm px-4 py-3 font-lora text-parchment text-sm placeholder-parchment/25 focus:outline-none focus:border-gold/50 focus:ring-1 focus:ring-gold/20 transition-colors"
                />
              </div>

              <div>
                <label htmlFor="notes" className="block font-playfair text-parchment text-sm font-semibold mb-1.5 tracking-wide">
                  Anything Else We Should Know
                </label>
                <textarea
                  id="notes"
                  name="notes"
                  rows={4}
                  placeholder="Where it came from, family history, repairs you can see, questions you have..."
                  value={formData.notes}
                  onChange={handleChange}
                  className="w-full bg-mahogany border border-gold/20 rounded-sm px-4 py-3 font-lora text-parchment text-sm placeholder-parchment/25 focus:outline-none focus:border-gold/50 focus:ring-1 focus:ring-gold/20 transition-colors resize-none"
                />
              </div>

              <button
                type="submit"
                disabled={status === 'loading'}
                className="btn-gold w-full py-4 rounded-sm font-playfair font-bold text-sm tracking-widest uppercase disabled:opacity-60"
              >
                {status === 'loading' ? 'Submitting...' : 'Request My Free Pipe Passport'}
              </button>
              {errorMsg && <p className="text-red-400 font-lora text-sm text-center">{errorMsg}</p>}
            </form>
          )}
        </div>

        {/* Legal framing */}
        <div className="max-w-3xl mx-auto mt-10">
          <p className="font-lora text-parchment/40 text-xs leading-relaxed text-center">
            The Faridunhill Pipe Passport is an identification and dating assessment service based on
            comparative visual analysis, historical catalogues, and market data. Results are provided
            as professional opinions, not certificates of authenticity. By submitting photographs you
            agree that they may be retained to improve our reference database.
          </p>
        </div>
      </div>
    </div>
  )
}
