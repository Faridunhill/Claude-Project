'use client'

import { useState } from 'react'
import Link from 'next/link'
import { generatePassportPdf } from '@/lib/passport-pdf'

const PASSPORT_LIVE = process.env.NEXT_PUBLIC_PASSPORT_LIVE === 'true'

interface PhotoSlot {
  view: string
  label: string
  hint: string
  required: boolean
}

interface Assessment {
  brand: string
  model_or_line: string
  shape: string
  estimated_era: string
  confidence: 'high' | 'medium' | 'low'
  stamping_reading: string
  dating_rationale: string
  condition_notes: string
  expert_summary: string
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
  { num: '3', title: 'Receive Your Passport', text: 'Our analysis engine — built on thirty-five years of reference knowledge — reads the stamping and issues your assessment in minutes, on screen and by email.' },
]

const CONFIDENCE_LABELS: Record<string, string> = {
  high: 'High Confidence',
  medium: 'Medium Confidence',
  low: 'Low Confidence — Preliminary',
}

export default function PipePassportPage() {
  const [formData, setFormData] = useState({ name: '', email: '', brandGuess: '', stampText: '', length: '', notes: '' })
  const [photos, setPhotos] = useState<Record<string, string>>({})
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [errorMsg, setErrorMsg] = useState('')
  const [referenceId, setReferenceId] = useState('')
  const [assessment, setAssessment] = useState<Assessment | null>(null)
  const [subscribe, setSubscribe] = useState(false)

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
        setAssessment(data.assessment ?? null)
        setStatus('success')
        if (subscribe) {
          fetch('/api/newsletter', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: formData.email }),
          }).catch(() => {})
        }
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
          <nav className="flex items-center justify-center gap-2 text-xs font-lora text-parchment/50 mb-5">
            <Link href="/" className="hover:text-gold transition-colors">Home</Link>
            <span>/</span>
            <Link href="/encyclopedia" className="hover:text-gold transition-colors">Encyclopedia</Link>
            <span>/</span>
            <span className="text-parchment/70">Pipe Passport</span>
          </nav>
          <span className="font-fell italic text-gold/70 text-sm tracking-widest">~ Free Identification &amp; Dating Assessment ~</span>
          <h1 className="font-playfair font-bold text-parchment text-4xl lg:text-5xl mt-3">The Pipe Passport</h1>
          <p className="font-lora text-parchment/70 leading-relaxed text-base max-w-2xl mx-auto mt-5">
            Found a pipe in an attic? Inherited a collection? Wondering whether that estate find is
            really what the seller claimed? Send six photographs and our identification engine —
            built on thirty-five years of collecting knowledge and over five thousand pipes sold —
            reads the stamping, dates the pipe, and issues its passport. Free, automated, in minutes.
          </p>
        </div>
      </div>

      <div className="max-w-screen-lg mx-auto px-6 lg:px-12 py-14">
        {/* Private beta notice */}
        {!PASSPORT_LIVE && (
          <div className="max-w-3xl mx-auto mb-10 p-5 bg-mahogany-light rounded-sm border border-gold/40 text-center">
            <p className="font-playfair font-bold text-gold text-sm uppercase tracking-widest mb-1.5">
              Private Beta — Testing in Progress
            </p>
            <p className="font-lora text-parchment/60 text-sm leading-relaxed">
              The Pipe Passport is being calibrated against our reference collection before its
              public launch. Assessments issued during the beta are for evaluation and may be revised.
            </p>
          </div>
        )}

        {/* How it works */}
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

        {/* Form / Result */}
        <div className="bg-mahogany-light rounded-sm gold-frame p-8 max-w-3xl mx-auto">
          {status === 'success' && assessment ? (
            <div>
              <div className="text-center mb-8 pb-6 border-b border-gold/15">
                <div className="text-gold text-4xl mb-3">✦</div>
                <p className="font-fell italic text-gold/70 text-sm tracking-widest">~ Faridunhill ~</p>
                <h2 className="font-playfair font-bold text-parchment text-2xl">Pipe Passport</h2>
                {referenceId && (
                  <p className="font-playfair text-gold text-lg tracking-widest mt-2">{referenceId}</p>
                )}
                <p className="font-lora text-parchment/50 text-xs mt-2">
                  {CONFIDENCE_LABELS[assessment.confidence] ?? assessment.confidence}
                </p>
              </div>

              <p className="font-lora text-parchment/80 leading-relaxed mb-8 font-fell italic text-lg">
                &ldquo;{assessment.expert_summary}&rdquo;
              </p>

              <div className="space-y-4">
                {[
                  ['Brand', assessment.brand],
                  ['Model / Line', assessment.model_or_line],
                  ['Shape', assessment.shape],
                  ['Estimated Era', assessment.estimated_era],
                  ['Stamping', assessment.stamping_reading],
                  ['Dating Rationale', assessment.dating_rationale],
                  ['Condition', assessment.condition_notes],
                ].map(([label, value]) => (
                  <div key={label} className="grid sm:grid-cols-4 gap-1 sm:gap-4 pb-4 border-b border-gold/10">
                    <p className="font-playfair text-gold/70 text-xs uppercase tracking-widest pt-0.5">{label}</p>
                    <p className="sm:col-span-3 font-lora text-parchment/85 text-sm leading-relaxed">{value}</p>
                  </div>
                ))}
              </div>

              <p className="font-lora text-parchment/50 text-sm mt-6 text-center">
                A copy of this passport has been sent to your email. Keep the reference number —
                it identifies this pipe in our records.
              </p>

              <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
                <button
                  type="button"
                  onClick={() =>
                    generatePassportPdf({
                      referenceId,
                      ownerName: formData.name,
                      ...assessment,
                      photoDataUrl: photos['left'],
                    }).catch(() => setErrorMsg('Could not generate the PDF. Please try again.'))
                  }
                  className="btn-gold px-8 py-3.5 rounded-sm font-playfair font-bold text-sm tracking-widest uppercase"
                >
                  Download PDF Passport
                </button>
                <Link
                  href="/shop/estate-pipes"
                  className="btn-ghost px-8 py-3.5 rounded-sm font-playfair font-bold text-sm tracking-widest uppercase"
                >
                  Browse Our Estate Pipes
                </Link>
              </div>
              {errorMsg && <p className="text-red-400 font-lora text-sm text-center mt-3">{errorMsg}</p>}
            </div>
          ) : status === 'loading' ? (
            <div className="text-center py-16">
              <div className="text-gold text-4xl mb-5 animate-pulse">✦</div>
              <p className="font-playfair font-semibold text-parchment text-xl mb-2">Examining Your Pipe...</p>
              <p className="font-lora text-parchment/60 text-sm max-w-md mx-auto">
                Reading the stamping, weighing the shape and finish against reference knowledge.
                This usually takes under a minute — please keep this page open.
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

              <label className="flex items-start gap-3 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={subscribe}
                  onChange={(e) => setSubscribe(e.target.checked)}
                  className="mt-1 h-4 w-4 accent-[#C9A84C] bg-mahogany border-gold/30"
                />
                <span className="font-lora text-parchment/60 text-sm leading-relaxed">
                  Add me to the Faridunhill newsletter — identification guides, new estate arrivals,
                  and subscriber-only markdowns. No spam, unsubscribe anytime.
                </span>
              </label>

              <button
                type="submit"
                className="btn-gold w-full py-4 rounded-sm font-playfair font-bold text-sm tracking-widest uppercase"
              >
                Request My Free Pipe Passport
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
