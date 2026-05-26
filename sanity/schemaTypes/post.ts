import { defineField, defineType } from 'sanity'

export default defineType({
  name: 'post',
  title: 'Blog Post',
  type: 'document',
  fields: [
    defineField({ name: 'title', title: 'Title', type: 'string', validation: (r) => r.required() }),
    defineField({ name: 'slug', title: 'Slug', type: 'slug', options: { source: 'title' }, validation: (r) => r.required() }),
    defineField({ name: 'author', title: 'Author', type: 'string', initialValue: 'The Faridunhill Editors' }),
    defineField({ name: 'publishedAt', title: 'Published At', type: 'datetime' }),
    defineField({
      name: 'category', title: 'Category', type: 'string',
      options: {
        list: ['Pipe Culture', 'Tobacco Reviews', 'Cigar Reviews', "Buyer's Guides", 'History & Heritage', 'How-To', 'New Arrivals'],
      },
    }),
    defineField({ name: 'excerpt', title: 'Excerpt', type: 'text', rows: 3 }),
    defineField({ name: 'mainImage', title: 'Main Image', type: 'image', options: { hotspot: true } }),
    defineField({ name: 'tags', title: 'Tags', type: 'array', of: [{ type: 'string' }] }),
    defineField({ name: 'body', title: 'Body (Markdown)', type: 'text', rows: 20 }),
  ],
  preview: {
    select: { title: 'title', subtitle: 'author', media: 'mainImage' },
  },
})
