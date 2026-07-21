import { NextRequest, NextResponse } from 'next/server'

const RESEND_API_KEY = process.env.RESEND_API_KEY
const TO_EMAIL = 'vintagepipevault@gmail.com'

// Client compresses to ~1600px JPEGs, so 6 photos stay well under this.
const MAX_TOTAL_PHOTO_BYTES = 3.5 * 1024 * 1024

const VIEW_LABELS: Record<string, string> = {
  left: 'Left Profile',
  right: 'Right Profile',
  top: 'Top (Bowl Rim)',
  bottom: 'Bottom (Heel)',
  stampA: 'Stamping Close-up A',
  stampB: 'Stamping Close-up B',
}

const REQUIRED_VIEWS = ['left', 'right', 'top', 'bottom', 'stampA']

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

    if (!RESEND_API_KEY) {
      console.error('RESEND_API_KEY not set')
      return NextResponse.json({ error: 'Submission service unavailable.' }, { status: 503 })
    }

    const referenceId = `FH-PP-${Date.now().toString(36).toUpperCase()}${Math.floor(Math.random() * 36 ** 2)
      .toString(36)
      .toUpperCase()
      .padStart(2, '0')}`

    const esc = (s: string) => String(s ?? '').replace(/</g, '&lt;').replace(/>/g, '&gt;')

    const detailRows = [
      ['Reference', referenceId],
      ['Name', esc(name)],
      ['Email', `<a href="mailto:${esc(email)}" style="color: #c9a84c;">${esc(email)}</a>`],
      ['Brand (owner’s guess)', esc(brandGuess) || '—'],
      ['Stamping (as read by owner)', esc(stampText) || '—'],
      ['Length', esc(length) || '—'],
    ]
      .map(
        ([label, value]) => `
          <tr>
            <td style="padding: 8px 0; color: #8b6b4a; width: 200px; vertical-align: top;">${label}</td>
            <td style="padding: 8px 0; font-weight: bold;">${value}</td>
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
        to: [TO_EMAIL],
        reply_to: email,
        subject: `[Pipe Passport] ${referenceId} — ${brandGuess || 'Unknown brand'} from ${name}`,
        html: `
          <div style="font-family: Georgia, serif; max-width: 600px; margin: 0 auto; padding: 32px; background: #f5edd6; color: #2c1810;">
            <div style="border-bottom: 2px solid #c9a84c; padding-bottom: 16px; margin-bottom: 24px;">
              <h2 style="font-size: 22px; margin: 0; color: #2c1810;">New Pipe Passport Submission</h2>
              <p style="margin: 4px 0 0; color: #8b6b4a; font-style: italic;">Reference ${referenceId} — ${photoList.length} photos attached</p>
            </div>

            <table style="width: 100%; border-collapse: collapse; margin-bottom: 24px;">${detailRows}</table>

            <div style="background: #fff8ec; border-left: 3px solid #c9a84c; padding: 16px 20px; border-radius: 2px;">
              <p style="margin: 0 0 4px; color: #8b6b4a; font-size: 12px;">Owner&rsquo;s notes</p>
              <p style="margin: 0; line-height: 1.8; white-space: pre-wrap;">${esc(notes) || '—'}</p>
            </div>

            <p style="margin-top: 24px; font-size: 12px; color: #8b6b4a; border-top: 1px solid #d4c4a0; padding-top: 16px;">
              Reply directly to this email to send ${esc(name)} their Pipe Passport assessment.
            </p>
          </div>
        `,
        attachments: photoList.map((p) => ({
          filename: `${referenceId}-${p.view}.jpg`,
          content: p.data.replace(/^data:image\/\w+;base64,/, ''),
        })),
      }),
    })

    if (!res.ok) {
      const error = await res.json()
      console.error('Resend error:', error)
      return NextResponse.json({ error: 'Failed to submit. Please try again.' }, { status: 500 })
    }

    return NextResponse.json({ success: true, referenceId })
  } catch (err) {
    console.error('Passport route error:', err)
    return NextResponse.json({ error: 'An unexpected error occurred.' }, { status: 500 })
  }
}
