import { NextRequest, NextResponse } from 'next/server'
import {
  analyzePipe,
  REQUIRED_VIEWS,
  VIEW_LABELS,
  type PassportAssessment,
} from '@/lib/passport-engine'

export const maxDuration = 300

const RESEND_API_KEY = process.env.RESEND_API_KEY
const ARCHIVE_EMAIL = 'vintagepipevault@gmail.com'

// Client compresses to ~1600px JPEGs, so 6 photos stay well under this.
const MAX_TOTAL_PHOTO_BYTES = 3.5 * 1024 * 1024

interface PassportPhoto {
  view: string
  data: string // data:image/jpeg;base64,...
}

export async function POST(request: NextRequest) {
  try {
    const { name, email, brandGuess, stampText, length, notes, photos } = await request.json()

    if (!name || !email) {
      return NextResponse.json({ error: 'Name and email are required.' }, { status: 400 })
    }

    const photoList: PassportPhoto[] = Array.isArray(photos)
      ? photos.filter((p) => p && VIEW_LABELS[p.view] && typeof p.data === 'string' && p.data.startsWith('data:image/'))
      : []

    const providedViews = new Set(photoList.map((p) => p.view))
    const missing = REQUIRED_VIEWS.filter((v) => !providedViews.has(v))
    if (missing.length > 0) {
      return NextResponse.json(
        { error: `Missing required photos: ${missing.map((v) => VIEW_LABELS[v]).join(', ')}.` },
        { status: 400 }
      )
    }

    const totalBytes = photoList.reduce((sum, p) => sum + Math.floor(p.data.length * 0.75), 0)
    if (totalBytes > MAX_TOTAL_PHOTO_BYTES) {
      return NextResponse.json({ error: 'Photos are too large. Please try again.' }, { status: 413 })
    }

    if (!process.env.ANTHROPIC_API_KEY) {
      console.error('ANTHROPIC_API_KEY not set')
      return NextResponse.json({ error: 'Identification service unavailable.' }, { status: 503 })
    }

    const referenceId = `FH-PP-${Date.now().toString(36).toUpperCase()}${Math.floor(Math.random() * 36 ** 2)
      .toString(36)
      .toUpperCase()
      .padStart(2, '0')}`

    let assessment: PassportAssessment
    try {
      assessment = await analyzePipe(
        photoList.map((p) => ({ view: p.view, base64: p.data.replace(/^data:image\/\w+;base64,/, '') })),
        { brandGuess, stampText, length, notes }
      )
    } catch (err) {
      console.error('Passport analysis failed:', err)
      return NextResponse.json({ error: 'The analysis could not be completed. Please try again.' }, { status: 502 })
    }

    // Email the passport to the collector (fire-and-forget: the on-screen result
    // is the deliverable; a failed email must not fail the request).
    if (RESEND_API_KEY) {
      sendPassportEmail({ name, email, referenceId, assessment, brandGuess }).catch((err) =>
        console.error('Passport email failed:', err)
      )
    }

    return NextResponse.json({ success: true, referenceId, assessment })
  } catch (err) {
    console.error('Passport route error:', err)
    return NextResponse.json({ error: 'An unexpected error occurred.' }, { status: 500 })
  }
}

async function sendPassportEmail({
  name,
  email,
  referenceId,
  assessment,
  brandGuess,
}: {
  name: string
  email: string
  referenceId: string
  assessment: PassportAssessment
  brandGuess?: string
}) {
  const esc = (s: string) => String(s ?? '').replace(/</g, '&lt;').replace(/>/g, '&gt;')

  const rows = [
    ['Brand', assessment.brand],
    ['Model / Line', assessment.model_or_line],
    ['Shape', assessment.shape],
    ['Estimated Era', assessment.estimated_era],
    ['Confidence', assessment.confidence],
    ['Stamping', assessment.stamping_reading],
    ['Dating Rationale', assessment.dating_rationale],
    ['Condition', assessment.condition_notes],
  ]
    .map(
      ([label, value]) => `
        <tr>
          <td style="padding: 8px 0; color: #8b6b4a; width: 150px; vertical-align: top;">${label}</td>
          <td style="padding: 8px 0;">${esc(value)}</td>
        </tr>`
    )
    .join('')

  const res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${RESEND_API_KEY}`,
    },
    body: JSON.stringify({
      from: 'Faridunhill Pipe Passport <contact@faridunhill.com>',
      to: [email],
      bcc: [ARCHIVE_EMAIL],
      subject: `Your Pipe Passport ${referenceId} — ${assessment.brand}`,
      html: `
        <div style="font-family: Georgia, serif; max-width: 600px; margin: 0 auto; padding: 32px; background: #f5edd6; color: #2c1810;">
          <div style="border-bottom: 2px solid #c9a84c; padding-bottom: 16px; margin-bottom: 24px;">
            <h2 style="font-size: 22px; margin: 0; color: #2c1810;">Pipe Passport</h2>
            <p style="margin: 4px 0 0; color: #8b6b4a; font-style: italic;">Reference ${referenceId} — faridunhill.com</p>
          </div>

          <p style="line-height: 1.7;">Dear ${esc(name)},</p>
          <p style="line-height: 1.7;">${esc(assessment.expert_summary)}</p>

          <table style="width: 100%; border-collapse: collapse; margin: 24px 0;">${rows}</table>

          <div style="background: #fff8ec; border-left: 3px solid #c9a84c; padding: 14px 18px; border-radius: 2px; margin-bottom: 24px;">
            <p style="margin: 0; font-size: 13px; line-height: 1.7; color: #6b5138;">
              The Faridunhill Pipe Passport is an identification and dating assessment based on
              comparative visual analysis, historical catalogues, and market data. Results are
              professional opinions, not certificates of authenticity.
            </p>
          </div>

          <p style="font-size: 13px; color: #8b6b4a; border-top: 1px solid #d4c4a0; padding-top: 16px; line-height: 1.7;">
            Thinking of selling${brandGuess ? ` your ${esc(brandGuess)}` : ''}, or looking for its
            companion? Browse our estate collection at
            <a href="https://faridunhill.com/shop" style="color: #c9a84c;">faridunhill.com</a>.
          </p>
        </div>
      `,
    }),
  })

  if (!res.ok) {
    console.error('Resend error:', await res.json())
  }
}
