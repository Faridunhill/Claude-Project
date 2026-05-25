import { createClient } from 'next-sanity'
import imageUrlBuilder from '@sanity/image-url'
import type { SanityImageSource } from '@sanity/image-url/lib/types/types'

const projectId = process.env.NEXT_PUBLIC_SANITY_PROJECT_ID
const dataset = process.env.NEXT_PUBLIC_SANITY_DATASET || 'production'

export const sanityClient = projectId
  ? createClient({
      projectId,
      dataset,
      apiVersion: '2024-01-01',
      useCdn: true,
    })
  : null

const builder = projectId ? imageUrlBuilder({ projectId, dataset }) : null

export function urlFor(source: SanityImageSource) {
  if (!builder) throw new Error('Sanity image builder not configured')
  return builder.image(source)
}

export const hasSanity = !!projectId
