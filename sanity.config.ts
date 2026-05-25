import { defineConfig } from 'sanity'
import { structureTool } from 'sanity/structure'
import { visionTool } from '@sanity/vision'
import { schemaTypes } from './sanity/schemaTypes'

const projectId = process.env.NEXT_PUBLIC_SANITY_PROJECT_ID!
const dataset = process.env.NEXT_PUBLIC_SANITY_DATASET || 'production'

export default defineConfig({
  basePath: '/studio',
  projectId,
  dataset,
  title: 'Faridunhill CMS',
  schema: {
    types: schemaTypes,
  },
  plugins: [
    structureTool({
      structure: (S) =>
        S.list()
          .title('Faridunhill Content')
          .items([
            S.listItem()
              .title('🪵 Products')
              .id('products')
              .child(S.documentTypeList('product').title('All Products')),
            S.divider(),
            S.listItem()
              .title('📰 Blog Posts')
              .id('posts')
              .child(S.documentTypeList('post').title('All Posts')),
            S.divider(),
            S.listItem()
              .title('📄 Static Pages')
              .id('staticPages')
              .child(S.documentTypeList('staticPage').title('Static Pages')),
          ]),
    }),
    visionTool(),
  ],
})
