// Sanity client — only active when NEXT_PUBLIC_SANITY_PROJECT_ID is set.
// Packages are installed separately; this file gracefully handles their absence.

export const hasSanity = false  // disabled until next-sanity packages are installed
export const sanityClient = null

export function urlFor(_source: unknown) {
  throw new Error('Sanity image builder not configured')
}
