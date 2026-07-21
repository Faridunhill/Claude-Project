import { NextRequest, NextResponse } from 'next/server'
import Anthropic from '@anthropic-ai/sdk'

export const maxDuration = 300

const RESEND_API_KEY = process.env.RESEND_API_KEY
const ARCHIVE_EMAIL = 'vintagepipevault@gmail.com'

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

export interface PassportAssessment {
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

const ASSESSMENT_SCHEMA = {
  type: 'object' as const,
  properties: {
    brand: {
      type: 'string',
      description: 'Most likely maker/brand, or "Unattributed" if it cannot be determined',
    },
    model_or_line: {
      type: 'string',
      description: 'Model, line, or finish name if determinable (e.g. "Shell Briar"), else "Unknown"',
    },
    shape: {
      type: 'string',
      description: 'Shape name and, if readable, shape number (e.g. "Billiard, shape 120")',
    },
    estimated_era: {
      type: 'string',
      description: 'Estimated production period, as precise as the evidence allows (e.g. "1962", "late 1950s–1960s", "mid-20th century")',
    },
    confidence: {
      type: 'string',
      enum: ['high', 'medium', 'low'],
      description: 'Overall confidence in the identification',
    },
    stamping_reading: {
      type: 'string',
      description: 'Transcription of all stamping visible in the photos, noting any illegible portions',
    },
    dating_rationale: {
      type: 'string',
      description: 'The specific evidence supporting the dating: stamp conventions, finish, stem logic, shape language',
    },
    condition_notes: {
      type: 'string',
      description: 'Observed condition: cake, rim, stem, fills, repairs, originality of parts',
    },
    expert_summary: {
      type: 'string',
      description: 'Two to four sentences summarizing the assessment in a warm, knowledgeable tobacconist voice, addressed to the owner',
    },
  },
  required: [
    'brand',
    'model_or_line',
    'shape',
    'estimated_era',
    'confidence',
    'stamping_reading',
    'dating_rationale',
    'condition_notes',
    'expert_summary',
  ],
  additionalProperties: false as const,
}

const SYSTEM_PROMPT = `You are the identification engine of the Faridunhill Pipe Passport — a free identification and dating assessment service for tobacco pipe collectors, backed by thirty-five years of dealer expertise.

You receive six standardized photographs of one pipe (left profile, right profile, top/bowl rim, bottom/heel, and close-ups of the shank stamping) plus whatever the owner knows.

Your method:
1. Read the stamping first — transcribe every mark you can see, including partial letters. The nomenclature is the primary evidence.
2. Cross-check against maker conventions: country-of-origin wording, date codes and suffixes, finish names, shape numbers, stem logos.
3. Weigh shape language, finish, stem material and logic, and drilling style as secondary evidence.
4. Use the owner's transcription and measurements as hints, but trust the photographs over the owner's guesses.
5. Assess visible condition: chamber cake, rim char, stem oxidation and tooth marks, fills, whether the stem appears original.

Rules:
- Be honest about uncertainty. A wrong confident attribution damages collectors; "Unattributed, likely English, mid-century" is a respectable answer.
- Never invent stamp text you cannot see. Mark illegible portions as illegible.
- This is a professional opinion based on visual analysis — never phrase anything as a certificate or guarantee of authenticity.
- Do not estimate monetary value.
- Write the expert_summary warmly, as Faridunhill's head tobacconist addressing a fellow collector.`

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

    const client = new Anthropic()

    const imageBlocks: Anthropic.ImageBlockParam[] = photoList.map((p) => ({
      type: 'image',
      source: {
        type: 'base64',
        media_type: 'image/jpeg',
        data: p.data.replace(/^data:image\/\w+;base64,/, ''),
      },
    }))

    const ownerContext = [
      `Photo order: ${photoList.map((p) => VIEW_LABELS[p.view]).join(', ')}.`,
      `Owner's brand guess: ${brandGuess || 'none given'}.`,
      `Stamping as the owner reads it: ${stampText || 'none given'}.`,
      `Length: ${length || 'not given'}.`,
      `Owner's notes: ${notes || 'none'}.`,
      'Identify and date this pipe.',
    ].join('\n')

    const response = await client.messages.create({
      model: 'claude-opus-4-8',
      max_tokens: 4096,
      thinking: { type: 'adaptive' },
      system: SYSTEM_PROMPT,
      output_config: {
        format: { type: 'json_schema', schema: ASSESSMENT_SCHEMA },
      },
      messages: [
        {
          role: 'user',
          content: [...imageBlocks, { type: 'text', text: ownerContext }],
        },
      ],
    })

    if (response.stop_reason === 'refusal') {
      console.error('Passport analysis refused')
      return NextResponse.json({ error: 'The analysis could not be completed. Please try again.' }, { status: 502 })
    }

    const textBlock = response.content.find((b): b is Anthropic.TextBlock => b.type === 'text')
    if (!textBlock) {
      return NextResponse.json({ error: 'The analysis could not be completed. Please try again.' }, { status: 502 })
    }
    const assessment: PassportAssessment = JSON.parse(textBlock.text)

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
