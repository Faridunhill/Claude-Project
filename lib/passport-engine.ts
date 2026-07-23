import Anthropic from '@anthropic-ai/sdk'

export const VIEW_LABELS: Record<string, string> = {
  left: 'Left Profile',
  right: 'Right Profile',
  top: 'Top (Bowl Rim)',
  bottom: 'Bottom (Heel)',
  stampA: 'Stamping Close-up A',
  stampB: 'Stamping Close-up B',
}

export const REQUIRED_VIEWS = ['left', 'right', 'top', 'bottom', 'stampA']

export interface PassportPhotoInput {
  view: string
  /** raw base64 JPEG, no data: prefix */
  base64: string
}

export interface PassportMeta {
  brandGuess?: string
  stampText?: string
  length?: string
  notes?: string
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

/**
 * Run one pipe through the identification engine.
 * Exactly one pipe per call — accuracy over throughput; bulk runs
 * parallelize calls, they never mix pipes in one analysis.
 */
export async function analyzePipe(
  photos: PassportPhotoInput[],
  meta: PassportMeta = {}
): Promise<PassportAssessment> {
  const client = new Anthropic()

  const imageBlocks: Anthropic.ImageBlockParam[] = photos.map((p) => ({
    type: 'image',
    source: {
      type: 'base64',
      media_type: 'image/jpeg',
      data: p.base64,
    },
  }))

  const ownerContext = [
    `Photo order: ${photos.map((p) => VIEW_LABELS[p.view] ?? p.view).join(', ')}.`,
    `Owner's brand guess: ${meta.brandGuess || 'none given'}.`,
    `Stamping as the owner reads it: ${meta.stampText || 'none given'}.`,
    `Length: ${meta.length || 'not given'}.`,
    `Owner's notes: ${meta.notes || 'none'}.`,
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
    throw new Error('Analysis was refused')
  }

  const textBlock = response.content.find((b): b is Anthropic.TextBlock => b.type === 'text')
  if (!textBlock) {
    throw new Error('Analysis returned no result')
  }

  return JSON.parse(textBlock.text) as PassportAssessment
}
