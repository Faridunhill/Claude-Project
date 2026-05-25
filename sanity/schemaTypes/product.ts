import { defineField, defineType } from 'sanity'

const DEPARTMENTS = [
  { title: 'Tobacco Pipes', value: 'tobacco-pipes' },
  { title: 'Pipe Tobacco', value: 'pipe-tobacco' },
  { title: 'Cigars', value: 'cigars' },
  { title: 'Pipe Accessories', value: 'pipe-accessories' },
  { title: 'Cigar Accessories', value: 'cigar-accessories' },
  { title: 'Leather Bags & Cases', value: 'leather-bags' },
  { title: 'Vaping & E-Liquids', value: 'vaping' },
  { title: 'Lighters & Matches', value: 'lighters' },
  { title: 'Gift Sets & Samplers', value: 'gift-sets' },
  { title: 'Sale & Clearance', value: 'sale' },
]

export const productType = defineType({
  name: 'product',
  title: 'Product',
  type: 'document',
  fields: [
    defineField({
      name: 'name',
      title: 'Product Name',
      type: 'string',
      validation: (R) => R.required(),
    }),
    defineField({
      name: 'brand',
      title: 'Brand',
      type: 'string',
      validation: (R) => R.required(),
    }),
    defineField({
      name: 'slug',
      title: 'URL Slug',
      type: 'slug',
      options: { source: 'name', maxLength: 96 },
      validation: (R) => R.required(),
    }),
    defineField({
      name: 'department',
      title: 'Department',
      type: 'string',
      options: { list: DEPARTMENTS },
      validation: (R) => R.required(),
    }),
    defineField({
      name: 'category',
      title: 'Category',
      type: 'string',
    }),
    defineField({
      name: 'price',
      title: 'Price (USD)',
      type: 'number',
      validation: (R) => R.required().min(0),
    }),
    defineField({
      name: 'originalPrice',
      title: 'Was / Original Price (USD)',
      description: 'Fill in only if this product is discounted',
      type: 'number',
    }),
    defineField({
      name: 'sku',
      title: 'SKU',
      type: 'string',
    }),
    defineField({
      name: 'images',
      title: 'Product Images',
      type: 'array',
      of: [{ type: 'image', options: { hotspot: true } }],
      validation: (R) => R.required().min(1),
    }),
    defineField({
      name: 'featured',
      title: 'Featured on Homepage',
      type: 'boolean',
      initialValue: false,
    }),
    defineField({
      name: 'inStock',
      title: 'In Stock',
      type: 'boolean',
      initialValue: true,
    }),
    defineField({
      name: 'rating',
      title: 'Rating (0–5)',
      type: 'number',
      validation: (R) => R.min(0).max(5),
      initialValue: 4.5,
    }),
    defineField({
      name: 'reviewCount',
      title: 'Number of Reviews',
      type: 'number',
      initialValue: 0,
    }),
    defineField({
      name: 'description',
      title: 'Description',
      type: 'text',
      rows: 4,
      validation: (R) => R.required(),
    }),
    defineField({
      name: 'tags',
      title: 'Tags',
      type: 'array',
      of: [{ type: 'string' }],
      options: { layout: 'tags' },
    }),
    defineField({
      name: 'specs',
      title: 'Specifications',
      description: 'Key/value pairs shown in the product specs table',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            { name: 'key', title: 'Specification Name', type: 'string' },
            { name: 'value', title: 'Value', type: 'string' },
          ],
          preview: { select: { title: 'key', subtitle: 'value' } },
        },
      ],
    }),
    defineField({ name: 'size', title: 'Size', type: 'string' }),
    defineField({ name: 'vitola', title: 'Vitola (Cigar Shape)', type: 'string' }),
    defineField({ name: 'origin', title: 'Country of Origin', type: 'string' }),
    defineField({ name: 'wrapper', title: 'Wrapper (Tobacco/Cigar)', type: 'string' }),
    defineField({
      name: 'contents',
      title: 'Gift Set Contents',
      type: 'array',
      of: [{ type: 'string' }],
    }),
  ],
  preview: {
    select: {
      title: 'name',
      subtitle: 'brand',
      media: 'images.0',
    },
  },
  orderings: [
    {
      title: 'Name A–Z',
      name: 'nameAsc',
      by: [{ field: 'name', direction: 'asc' }],
    },
    {
      title: 'Price: Low to High',
      name: 'priceLowHigh',
      by: [{ field: 'price', direction: 'asc' }],
    },
    {
      title: 'Price: High to Low',
      name: 'priceHighLow',
      by: [{ field: 'price', direction: 'desc' }],
    },
  ],
})
