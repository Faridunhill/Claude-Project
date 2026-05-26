import { createClient } from '@sanity/client'
import imageUrlBuilder from '@sanity/image-url'

const projectId = process.env.NEXT_PUBLIC_SANITY_PROJECT_ID
const dataset = process.env.NEXT_PUBLIC_SANITY_DATASET || 'production'

export const hasSanity = Boolean(projectId)

export const sanityClient = hasSanity
  ? createClient({
      projectId: projectId!,
      dataset,
      apiVersion: '2024-01-01',
      useCdn: true,
    })
  : null

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const builder = sanityClient ? imageUrlBuilder(sanityClient) : null

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function urlFor(source: any) {
  if (!builder) throw new Error('Sanity image builder not configured')
  return builder.image(source)
}
