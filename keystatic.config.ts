import { config, collection, fields } from '@keystatic/core'

export default config({
  storage: {
    kind: 'github',
    repo: {
      owner: 'faridunhill',
      name: 'Claude-Project',
    },
  },

  ui: {
    brand: { name: 'Faridunhill CMS' },
    navigation: {
      Products: ['products'],
      Blog: ['posts'],
    },
  },

  collections: {
    products: collection({
      label: 'Products',
      slugField: 'name',
      path: 'content/products/*',
      format: { data: 'yaml' },
      schema: {
        name: fields.slug({ name: { label: 'Name', validation: { isRequired: true } } }),
        brand: fields.text({ label: 'Brand' }),
        department: fields.select({
          label: 'Department',
          options: [
            { label: 'Tobacco Pipes', value: 'tobacco-pipes' },
            { label: 'Pipe Tobacco', value: 'pipe-tobacco' },
            { label: 'Cigars', value: 'cigars' },
            { label: 'Pipe Accessories', value: 'pipe-accessories' },
            { label: 'Cigar Accessories', value: 'cigar-accessories' },
            { label: 'Leather Bags & Cases', value: 'leather-bags' },
            { label: 'Vaping & E-Liquids', value: 'vaping' },
            { label: 'Lighters & Matches', value: 'lighters' },
            { label: 'Gift Sets & Samplers', value: 'gift-sets' },
            { label: 'Sale & Clearance', value: 'sale' },
          ],
          defaultValue: 'tobacco-pipes',
        }),
        category: fields.text({ label: 'Category' }),
        price: fields.text({ label: 'Price (£) — e.g. 19.99', validation: { isRequired: true } }),
        originalPrice: fields.text({ label: 'Original Price (£) — leave blank if not on sale' }),
        sku: fields.text({ label: 'SKU' }),
        images: fields.array(
          fields.text({ label: 'Image URL' }),
          { label: 'Images', itemLabel: (props) => props.value || 'Image' }
        ),
        featured: fields.checkbox({ label: 'Featured on homepage', defaultValue: false }),
        inStock: fields.checkbox({ label: 'In Stock', defaultValue: true }),
        rating: fields.text({ label: 'Rating (0–5) — e.g. 4.5', defaultValue: '4.5' }),
        reviewCount: fields.integer({ label: 'Review Count', defaultValue: 0 }),
        description: fields.text({ label: 'Description', multiline: true }),
        tags: fields.array(
          fields.text({ label: 'Tag' }),
          { label: 'Tags', itemLabel: (props) => props.value || 'Tag' }
        ),
        specs: fields.array(
          fields.object({
            key: fields.text({ label: 'Spec name (e.g. Material)' }),
            value: fields.text({ label: 'Spec value (e.g. Briar wood)' }),
          }),
          { label: 'Specifications', itemLabel: (props) => props.fields.key.value || 'Spec' }
        ),
        size: fields.text({ label: 'Size' }),
        vitola: fields.text({ label: 'Vitola (cigars)' }),
        origin: fields.text({ label: 'Origin / Country' }),
        wrapper: fields.text({ label: 'Wrapper (cigars)' }),
        contents: fields.array(
          fields.text({ label: 'Item' }),
          { label: 'Contents (gift sets)', itemLabel: (props) => props.value || 'Item' }
        ),
      },
    }),

    posts: collection({
      label: 'Blog Posts',
      slugField: 'title',
      path: 'content/blog/*',
      format: { data: 'yaml' },
      schema: {
        title: fields.text({ label: 'Title', validation: { isRequired: true } }),
        author: fields.text({ label: 'Author', defaultValue: 'The Faridunhill Editors' }),
        publishedAt: fields.date({ label: 'Published Date' }),
        category: fields.select({
          label: 'Category',
          options: [
            { label: 'Pipe Culture', value: 'Pipe Culture' },
            { label: 'Tobacco Reviews', value: 'Tobacco Reviews' },
            { label: 'Cigar Reviews', value: 'Cigar Reviews' },
            { label: "Buyer's Guides", value: "Buyer's Guides" },
            { label: 'History & Heritage', value: 'History & Heritage' },
            { label: 'How-To', value: 'How-To' },
            { label: 'New Arrivals', value: 'New Arrivals' },
          ],
          defaultValue: 'Pipe Culture',
        }),
        excerpt: fields.text({ label: 'Excerpt', multiline: true }),
        image: fields.text({ label: 'Featured Image URL' }),
        tags: fields.array(
          fields.text({ label: 'Tag' }),
          { label: 'Tags', itemLabel: (props) => props.value || 'Tag' }
        ),
        content: fields.text({ label: 'Content (Markdown)', multiline: true }),
      },
    }),
  },
})
