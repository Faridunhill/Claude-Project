import { NextResponse } from 'next/server'
import Anthropic from '@anthropic-ai/sdk'

export const runtime = 'nodejs'
export const maxDuration = 300

const SCRIPT_SCHEMA = {
  type: 'object' as const,
  properties: {
    title: { type: 'string', description: 'Encyclopedia entry title, concise and specific' },
    slug: { type: 'string', description: 'URL-friendly kebab-case slug derived from the title' },
    category: {
      type: 'string',
      enum: [
        'History',
        'Science & Nature',
        'Arts & Culture',
        'Craft & Technique',
        'People & Places',
        'Language & Ideas',
      ],
    },
    summary: { type: 'string', description: 'One or two sentence summary for cards and SEO' },
    narration: {
      type: 'string',
      description:
        'The spoken presenter script, written to be read aloud on camera. Plain prose, no headings, no stage directions, no markdown.',
    },
    article: {
      type: 'string',
      description:
        'The written encyclopedia article in markdown. Use ## and ### headings, bold for key terms. Deeper than the narration.',
    },
    tags: { type: 'array', items: { type: 'string' } },
  },
  required: ['title', 'slug', 'category', 'summary', 'narration', 'article', 'tags'],
  additionalProperties: false,
}

export async function POST(request: Request) {
  if (!process.env.ANTHROPIC_API_KEY) {
    return NextResponse.json(
      { error: 'ANTHROPIC_API_KEY is not configured. Add it to .env.local — see ENCYCLOPEDIA.md.' },
      { status: 503 }
    )
  }

  let body: { topic?: string; audience?: string; lengthMinutes?: number; notes?: string }
  try {
    body = await request.json()
  } catch {
    return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 })
  }

  const topic = (body.topic || '').trim()
  if (!topic) {
    return NextResponse.json({ error: 'A topic is required' }, { status: 400 })
  }

  const audience = body.audience || 'curious adults'
  const lengthMinutes = Math.min(Math.max(body.lengthMinutes || 3, 1), 10)
  // ~140 spoken words per minute is a comfortable presenter pace
  const targetWords = lengthMinutes * 140

  const client = new Anthropic()

  try {
    const response = await client.messages.create({
      model: 'claude-opus-4-8',
      max_tokens: 16000,
      thinking: { type: 'adaptive' },
      system:
        'You write encyclopedia entries that are delivered as short presenter-led learning videos. ' +
        'The narration is spoken by a single on-screen presenter (an avatar of the author), so it must ' +
        'sound natural read aloud: contractions, short sentences, a warm direct-to-camera tone, a hook ' +
        'in the first two sentences, and a closing line that lands. Never include headings, bullet ' +
        'points, bracketed directions, or citations in the narration. The written article is a separate, ' +
        'richer treatment of the same topic. Be factually careful; prefer well-established facts and ' +
        'say "historians believe" or similar when something is contested.',
      messages: [
        {
          role: 'user',
          content:
            `Topic: ${topic}\n` +
            `Audience: ${audience}\n` +
            `Target narration length: about ${lengthMinutes} minute(s) — roughly ${targetWords} spoken words.\n` +
            (body.notes ? `Extra guidance from the author: ${body.notes}\n` : '') +
            'Produce the encyclopedia entry.',
        },
      ],
      output_config: { format: { type: 'json_schema', schema: SCRIPT_SCHEMA } },
    })

    if (response.stop_reason === 'refusal') {
      return NextResponse.json(
        { error: 'The model declined to write this entry. Try rephrasing the topic.' },
        { status: 422 }
      )
    }

    const textBlock = response.content.find((b) => b.type === 'text')
    if (!textBlock || textBlock.type !== 'text') {
      return NextResponse.json({ error: 'Empty response from model' }, { status: 502 })
    }

    return NextResponse.json(JSON.parse(textBlock.text))
  } catch (err) {
    if (err instanceof Anthropic.AuthenticationError) {
      return NextResponse.json({ error: 'Invalid ANTHROPIC_API_KEY' }, { status: 503 })
    }
    if (err instanceof Anthropic.RateLimitError) {
      return NextResponse.json({ error: 'Rate limited — try again shortly' }, { status: 429 })
    }
    console.error('Script generation failed:', err)
    return NextResponse.json({ error: 'Script generation failed' }, { status: 502 })
  }
}
