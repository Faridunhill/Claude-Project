import { defineField, defineType } from 'sanity'

export default defineType({
  name: 'product',
  title: 'Product',
  type: 'document',
  fields: [
    defineField({ name: 'name', title: 'Name', type: 'string', validation: (r) => r.required() }),
    defineField({ name: 'brand', title: 'Brand', type: 'string' }),
    defineField({ name: 'slug', title: 'Slug', type: 'slug', options: { source: 'name' }, validation: (r) => r.required() }),
    defineField({
      name: 'department', title: 'Department', type: 'string',
      options: {
        list: [
          { value: 'tobacco-pipes', title: 'Tobacco Pipes' },
          { value: 'pipe-tobacco', title: 'Pipe Tobacco' },
          { value: 'cigars', title: 'Cigars' },
          { value: 'pipe-accessories', title: 'Pipe Accessories' },
          { value: 'cigar-accessories', title: 'Cigar Accessories' },
          { value: 'leather-bags', title: 'Leather Bags & Cases' },
          { value: 'vaping', title: 'Vaping & E-Liquids' },
          { value: 'lighters', title: 'Lighters & Matches' },
          { value: 'gift-sets', title: 'Gift Sets & Samplers' },
          { value: 'sale', title: 'Sale & Clearance' },
        ],
      },
      validation: (r) => r.required(),
    }),
    defineField({ name: 'category', title: 'Category', type: 'string' }),
    defineField({ name: 'price', title: 'Price', type: 'number', validation: (r) => r.required().min(0) }),
    defineField({ name: 'originalPrice', title: 'Original Price', type: 'number' }),
    defineField({ name: 'sku', title: 'SKU', type: 'string' }),
    defineField({ name: 'images', title: 'Images', type: 'array', of: [{ type: 'image', options: { hotspot: true } }] }),
    defineField({ name: 'featured', title: 'Featured', type: 'boolean', initialValue: false }),
    defineField({ name: 'inStock', title: 'In Stock', type: 'boolean', initialValue: true }),
    defineField({ name: 'rating', title: 'Rating', type: 'number', initialValue: 4.5 }),
    defineField({ name: 'reviewCount', title: 'Review Count', type: 'number', initialValue: 0 }),
    defineField({ name: 'description', title: 'Description', type: 'text' }),
    defineField({ name: 'tags', title: 'Tags', type: 'array', of: [{ type: 'string' }] }),
    defineField({
      name: 'specs', title: 'Specs', type: 'array',
      of: [{ type: 'object', fields: [
        { name: 'key', type: 'string', title: 'Key' },
        { name: 'value', type: 'string', title: 'Value' },
      ]}],
    }),
    defineField({ name: 'size', title: 'Size', type: 'string' }),
    defineField({ name: 'vitola', title: 'Vitola', type: 'string' }),
    defineField({ name: 'origin', title: 'Origin', type: 'string' }),
    defineField({ name: 'wrapper', title: 'Wrapper', type: 'string' }),
    defineField({ name: 'contents', title: 'Contents', type: 'array', of: [{ type: 'string' }] }),
  ],
  preview: {
    select: { title: 'name', subtitle: 'brand', media: 'images.0' },
  },
})
