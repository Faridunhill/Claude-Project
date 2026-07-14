import { createReader } from '@keystatic/core/reader'
import keystatic from '@/keystatic.config'

export type Confidence = 'high' | 'medium' | 'low'
export type MarkerWeight = 'primary' | 'precision' | 'corroborating'

export interface Reading {
  reads: string
  indicates: string
  from: number | null
  to: number | null
  confidence: Confidence
  note: string
}

export interface Marker {
  id: string
  label: string
  question: string
  whereToLook: string
  priority: number
  weight: MarkerWeight
  readings: Reading[]
}

export interface Cabinet {
  maker: string
  displayName: string
  aka: string[]
  country: string
  founded: string
  status: 'active' | 'defunct'
  summary: string
  howToUse: string
  markers: Marker[]
  quickFlow: string[]
  sources: string[]
}

function getReader() {
  return createReader(process.cwd(), keystatic)
}

/* eslint-disable @typescript-eslint/no-explicit-any */
function mapCabinet(slug: string, entry: any): Cabinet {
  return {
    maker: slug,
    displayName: entry.displayName ?? slug,
    aka: (entry.aka as string[]) ?? [],
    country: entry.country ?? '',
    founded: entry.founded ?? '',
    status: entry.status ?? 'active',
    summary: entry.summary ?? '',
    howToUse: entry.howToUse ?? '',
    markers: ((entry.markers as any[]) ?? [])
      .map((m) => ({
        id: m.id ?? '',
        label: m.label ?? '',
        question: m.question ?? '',
        whereToLook: m.whereToLook ?? '',
        priority: (m.priority as number) ?? 99,
        weight: (m.weight as MarkerWeight) ?? 'corroborating',
        readings: ((m.readings as any[]) ?? []).map((r) => ({
          reads: r.reads ?? '',
          indicates: r.indicates ?? '',
          from: (r.from as number) ?? null,
          to: (r.to as number) ?? null,
          confidence: (r.confidence as Confidence) ?? 'medium',
          note: r.note ?? '',
        })),
      }))
      .sort((a, b) => a.priority - b.priority),
    quickFlow: (entry.quickFlow as string[]) ?? [],
    sources: (entry.sources as string[]) ?? [],
  }
}
/* eslint-enable @typescript-eslint/no-explicit-any */

export async function getAllCabinets(): Promise<Cabinet[]> {
  try {
    const reader = getReader()
    const entries = await reader.collections.cabinets.all()
    return entries
      .map((e) => mapCabinet(e.slug, e.entry))
      .sort((a, b) => a.displayName.localeCompare(b.displayName))
  } catch (err) {
    console.error('Keystatic cabinet read failed:', err)
    return []
  }
}

export async function getCabinetBySlug(slug: string): Promise<Cabinet | undefined> {
  const cabinets = await getAllCabinets()
  return cabinets.find((c) => c.maker === slug)
}

export const weightMeta: Record<MarkerWeight, { label: string; blurb: string }> = {
  primary: { label: 'Primary', blurb: 'Moves the date the most' },
  precision: { label: 'Precision', blurb: 'Pins an exact year when present' },
  corroborating: { label: 'Corroborating', blurb: 'Narrows and cross-checks' },
}
