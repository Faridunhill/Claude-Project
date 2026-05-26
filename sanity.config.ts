import { defineConfig } from 'sanity'
import { structureTool } from 'sanity/structure'
import { visionTool } from '@sanity/vision'
import { schemaTypes } from '@/sanity/schemaTypes'

export default defineConfig({
  basePath: '/studio',
  // Fallback to known project ID so config is always valid at build time
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID || 'z16xm7xb',
  dataset: process.env.NEXT_PUBLIC_SANITY_DATASET || 'production',
  plugins: [structureTool(), visionTool()],
  schema: {
    types: schemaTypes,
  },
})
