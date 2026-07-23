import { NextResponse } from 'next/server'

export const runtime = 'nodejs'
export const maxDuration = 120

/**
 * Narration preview in the author's cloned voice.
 * POST { text } → audio/mpeg
 *
 * Requires ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID (your voice clone) — see ENCYCLOPEDIA.md.
 */
export async function POST(request: Request) {
  const apiKey = process.env.ELEVENLABS_API_KEY
  const voiceId = process.env.ELEVENLABS_VOICE_ID

  if (!apiKey || !voiceId) {
    return NextResponse.json(
      {
        error:
          'ElevenLabs is not configured. Set ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID in .env.local — see ENCYCLOPEDIA.md for how to clone your voice.',
      },
      { status: 503 }
    )
  }

  let body: { text?: string }
  try {
    body = await request.json()
  } catch {
    return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 })
  }

  const text = (body.text || '').trim()
  if (!text) {
    return NextResponse.json({ error: 'Text is required' }, { status: 400 })
  }
  if (text.length > 5000) {
    return NextResponse.json(
      { error: 'Preview text is limited to 5,000 characters — preview a shorter section.' },
      { status: 400 }
    )
  }

  const res = await fetch(
    `https://api.elevenlabs.io/v1/text-to-speech/${encodeURIComponent(voiceId)}`,
    {
      method: 'POST',
      headers: {
        'xi-api-key': apiKey,
        'Content-Type': 'application/json',
        Accept: 'audio/mpeg',
      },
      body: JSON.stringify({
        text,
        model_id: 'eleven_multilingual_v2',
        voice_settings: { stability: 0.5, similarity_boost: 0.8 },
      }),
    }
  )

  if (!res.ok) {
    const detail = await res.text().catch(() => '')
    console.error('ElevenLabs error:', res.status, detail)
    return NextResponse.json(
      { error: `ElevenLabs request failed (${res.status})` },
      { status: 502 }
    )
  }

  return new NextResponse(res.body, {
    headers: {
      'Content-Type': 'audio/mpeg',
      'Cache-Control': 'no-store',
    },
  })
}
