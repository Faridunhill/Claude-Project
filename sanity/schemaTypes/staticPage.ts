import { defineField, defineType } from 'sanity'

export const staticPageType = defineType({
  name: 'staticPage',
  title: 'Static Page',
  type: 'document',
  fields: [
    defineField({
      name: 'title',
      title: 'Page Title',
      type: 'string',
      validation: (R) => R.required(),
    }),
    defineField({
      name: 'slug',
      title: 'URL Slug',
      description: 'e.g. "about", "shipping", "returns", "privacy"',
      type: 'slug',
      options: {
        source: 'title',
        slugify: (input: string) => input.toLowerCase().replace(/\s+/g, '-'),
      },
      validation: (R) => R.required(),
    }),
    defineField({
      name: 'headline',
      title: 'Page Headline',
      type: 'string',
    }),
    defineField({
      name: 'body',
      title: 'Page Content (Markdown)',
      description: 'Write in Markdown. Use ## for sections, **bold**, - for lists.',
      type: 'text',
      rows: 30,
    }),
    defineField({
      name: 'seoDescription',
      title: 'SEO Meta Description',
      type: 'text',
      rows: 2,
    }),
  ],
  preview: {
    select: {
      title: 'title',
      subtitle: 'slug.current',
    },
    prepare({ title, subtitle }: { title: string; subtitle: string }) {
      return { title, subtitle: `/${subtitle}` }
    },
  },
})
