import { NextResponse } from 'next/server'

export const runtime = 'nodejs'
export const maxDuration = 120

const HEYGEN_BASE = 'https://api.heygen.com'

/**
 * Presenter-video rendering via HeyGen.
 *
 * POST { narration, mode } → { videoId }
 *   mode: "avatar"        — your studio/stock-style avatar (HEYGEN_AVATAR_ID)
 *   mode: "photo"         — talking-photo avatar built from a photo of your face (HEYGEN_TALKING_PHOTO_ID)
 *   The narration is voiced with HEYGEN_VOICE_ID (link your ElevenLabs clone inside
 *   HeyGen, or use a HeyGen voice clone — see ENCYCLOPEDIA.md).
 *
 * GET ?videoId=... → { status, videoUrl }   (poll until status === "completed")
 */
export async function POST(request: Request) {
  const apiKey = process.env.HEYGEN_API_KEY
  if (!apiKey) {
    return NextResponse.json(
      { error: 'HEYGEN_API_KEY is not configured — see ENCYCLOPEDIA.md.' },
      { status: 503 }
    )
  }

  let body: { narration?: string; mode?: 'avatar' | 'photo' }
  try {
    body = await request.json()
  } catch {
    return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 })
  }

  const narration = (body.narration || '').trim()
  if (!narration) {
    return NextResponse.json({ error: 'Narration text is required' }, { status: 400 })
  }

  const mode = body.mode === 'photo' ? 'photo' : 'avatar'
  const avatarId = process.env.HEYGEN_AVATAR_ID
  const talkingPhotoId = process.env.HEYGEN_TALKING_PHOTO_ID
  const voiceId = process.env.HEYGEN_VOICE_ID

  if (!voiceId) {
    return NextResponse.json(
      { error: 'HEYGEN_VOICE_ID is not configured — see ENCYCLOPEDIA.md.' },
      { status: 503 }
    )
  }
  if (mode === 'avatar' && !avatarId) {
    return NextResponse.json(
      { error: 'HEYGEN_AVATAR_ID is not configured for avatar mode — see ENCYCLOPEDIA.md.' },
      { status: 503 }
    )
  }
  if (mode === 'photo' && !talkingPhotoId) {
    return NextResponse.json(
      { error: 'HEYGEN_TALKING_PHOTO_ID is not configured for photo mode — see ENCYCLOPEDIA.md.' },
      { status: 503 }
    )
  }

  const character =
    mode === 'photo'
      ? { type: 'talking_photo', talking_photo_id: talkingPhotoId }
      : { type: 'avatar', avatar_id: avatarId, avatar_style: 'normal' }

  const res = await fetch(`${HEYGEN_BASE}/v2/video/generate`, {
    method: 'POST',
    headers: {
      'X-Api-Key': apiKey,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      video_inputs: [
        {
          character,
          voice: { type: 'text', input_text: narration, voice_id: voiceId },
          background: { type: 'color', value: '#2C1810' },
        },
      ],
      dimension: { width: 1280, height: 720 },
    }),
  })

  const data = await res.json().catch(() => null)
  if (!res.ok || !data?.data?.video_id) {
    console.error('HeyGen generate error:', res.status, JSON.stringify(data))
    return NextResponse.json(
      { error: data?.error?.message || `HeyGen request failed (${res.status})` },
      { status: 502 }
    )
  }

  return NextResponse.json({ videoId: data.data.video_id })
}

export async function GET(request: Request) {
  const apiKey = process.env.HEYGEN_API_KEY
  if (!apiKey) {
    return NextResponse.json({ error: 'HEYGEN_API_KEY is not configured' }, { status: 503 })
  }

  const videoId = new URL(request.url).searchParams.get('videoId')
  if (!videoId) {
    return NextResponse.json({ error: 'videoId query parameter is required' }, { status: 400 })
  }

  const res = await fetch(
    `${HEYGEN_BASE}/v1/video_status.get?video_id=${encodeURIComponent(videoId)}`,
    { headers: { 'X-Api-Key': apiKey } }
  )

  const data = await res.json().catch(() => null)
  if (!res.ok || !data?.data) {
    console.error('HeyGen status error:', res.status, JSON.stringify(data))
    return NextResponse.json({ error: `HeyGen status check failed (${res.status})` }, { status: 502 })
  }

  return NextResponse.json({
    status: data.data.status, // "pending" | "processing" | "completed" | "failed"
    videoUrl: data.data.video_url || null,
    error: data.data.error || null,
  })
}
