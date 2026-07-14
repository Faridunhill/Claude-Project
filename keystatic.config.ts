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
      'Dating Directory': ['cabinets'],
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
            { label: 'Estate Pipes', value: 'estate-pipes' },
            { label: 'New Pipes', value: 'new-pipes' },
            { label: 'Meerschaum', value: 'meerschaum' },
            { label: 'Rare & Collectible', value: 'rare-collectible' },
            { label: 'Leather Bags & Cases', value: 'leather-bags' },
            { label: 'Cigar & Smoking Accessories', value: 'cigar-smoking-accessories' },
            { label: 'Lighters & Matches', value: 'lighters' },
            { label: 'Sale & Clearance', value: 'sale' },
          ],
          defaultValue: 'estate-pipes',
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

    cabinets: collection({
      label: 'Dating Cabinets',
      slugField: 'maker',
      path: 'content/dating/*',
      format: { data: 'yaml' },
      schema: {
        maker: fields.slug({
          name: { label: 'Maker slug (e.g. peterson)', validation: { isRequired: true } },
        }),
        displayName: fields.text({ label: 'Display name', validation: { isRequired: true } }),
        aka: fields.array(fields.text({ label: 'Also known as' }), {
          label: 'Also known as',
          itemLabel: (props) => props.value || 'Name',
        }),
        country: fields.text({ label: 'Country' }),
        founded: fields.text({ label: 'Founded (year)' }),
        status: fields.select({
          label: 'Status',
          options: [
            { label: 'Active', value: 'active' },
            { label: 'Defunct', value: 'defunct' },
          ],
          defaultValue: 'active',
        }),
        summary: fields.text({ label: 'Summary', multiline: true }),
        howToUse: fields.text({ label: 'How to use this cabinet', multiline: true }),
        markers: fields.array(
          fields.object({
            id: fields.text({ label: 'Marker id (e.g. com-stamp)' }),
            label: fields.text({ label: 'Marker label' }),
            question: fields.text({ label: "Appraiser's question", multiline: true }),
            whereToLook: fields.text({ label: 'Where to look', multiline: true }),
            priority: fields.integer({ label: 'Priority (1 = read first)', defaultValue: 1 }),
            weight: fields.select({
              label: 'Weight',
              options: [
                { label: 'Primary (moves the date most)', value: 'primary' },
                { label: 'Precision (pins an exact year)', value: 'precision' },
                { label: 'Corroborating (narrows / cross-checks)', value: 'corroborating' },
              ],
              defaultValue: 'corroborating',
            }),
            readings: fields.array(
              fields.object({
                reads: fields.text({ label: 'What the evidence shows', multiline: true }),
                indicates: fields.text({ label: 'Indicates (date range)' }),
                from: fields.integer({ label: 'From year (optional)' }),
                to: fields.integer({ label: 'To year (optional)' }),
                confidence: fields.select({
                  label: 'Confidence',
                  options: [
                    { label: 'High', value: 'high' },
                    { label: 'Medium', value: 'medium' },
                    { label: 'Low', value: 'low' },
                  ],
                  defaultValue: 'medium',
                }),
                note: fields.text({ label: 'Note', multiline: true }),
              }),
              { label: 'Readings', itemLabel: (props) => props.fields.indicates.value || 'Reading' }
            ),
          }),
          { label: 'Markers', itemLabel: (props) => props.fields.label.value || 'Marker' }
        ),
        quickFlow: fields.array(fields.text({ label: 'Step', multiline: true }), {
          label: 'Quick flow (ordered decision path)',
          itemLabel: (props) => props.value || 'Step',
        }),
        sources: fields.array(fields.text({ label: 'Source' }), {
          label: 'Sources',
          itemLabel: (props) => props.value || 'Source',
        }),
      },
    }),
  },
})
