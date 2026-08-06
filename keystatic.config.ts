import { config, collection, fields } from '@keystatic/core'
import { CONDITION_GRADES } from './lib/listing-standard.mjs'

/**
 * The condition ladder, as a CMS dropdown. Sourced from the standard itself so
 * the form and the auditor can never disagree about what the grades are.
 * Ordered best-first; the empty option means "not yet graded", which the
 * auditor scores as a failure rather than the CMS refusing the record.
 */
const CONDITION_OPTIONS = [
  { label: '—', value: '' },
  ...(CONDITION_GRADES as Array<{ code: string; label: string }>).map((g) => ({
    label: g.label,
    value: g.code,
  })),
]

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

        // ── THE LISTING STANDARD (draft v0.1) ────────────────────────────────
        // Spec: lib/listing-standard.mjs · Argument: docs/IDEA_A5_THE_STANDARD.md
        // Every field is optional at the CMS layer ON PURPOSE: the 264 records
        // already in content/products predate the standard and must keep
        // loading. Enforcement is the auditor's job (scripts/audit-listings.mjs),
        // which scores a listing rather than refusing to open it.
        model: fields.text({ label: 'Model / shape number — as stamped, or UNSTAMPED' }),
        countryStamped: fields.text({ label: 'Country AS STAMPED — what the pipe says, not what you believe' }),
        stampTranscription: fields.text({
          label: 'Stamp transcription — literal, line by line, including what makes no sense',
          multiline: true,
        }),
        dateBracket: fields.text({ label: 'Date bracket — from the dating engine. UNDATED is an honest answer' }),
        attributionEvidence: fields.text({ label: 'Evidence — which stamp, which rule', multiline: true }),

        components: fields.object(
          {
            briar: fields.select({ label: 'Bowl / briar', options: CONDITION_OPTIONS, defaultValue: '' }),
            rim: fields.select({ label: 'Rim', options: CONDITION_OPTIONS, defaultValue: '' }),
            stem: fields.select({ label: 'Stem', options: CONDITION_OPTIONS, defaultValue: '' }),
            stamps: fields.select({ label: 'Stamps', options: CONDITION_OPTIONS, defaultValue: '' }),
          },
          { label: 'Condition — graded in four parts. The headline grade is the LOWEST of these.' }
        ),
        conditionGrade: fields.select({
          label: 'Headline grade — must equal the lowest component above',
          options: CONDITION_OPTIONS,
          defaultValue: '',
        }),
        smoked: fields.select({
          label: 'Smoked?',
          options: [
            { label: '—', value: '' },
            { label: 'Unsmoked', value: 'UNSMOKED' },
            { label: 'Lightly smoked', value: 'LIGHTLY_SMOKED' },
            { label: 'Smoked', value: 'SMOKED' },
            { label: 'Unknown', value: 'UNKNOWN' },
          ],
          defaultValue: '',
        }),
        sanitised: fields.text({ label: 'Sanitised — state the method, or NO' }),
        refurbished: fields.text({ label: 'Refurbished — what was done, or NONE' }),
        repaired: fields.text({ label: 'Repaired — restemmed / banded / crack pinned, or NONE' }),

        lengthMm: fields.text({ label: 'Length (mm)' }),
        heightMm: fields.text({ label: 'Height (mm)' }),
        bowlOuterMm: fields.text({ label: 'Bowl outside diameter (mm)' }),
        chamberDiameterMm: fields.text({ label: 'Chamber diameter (mm)' }),
        chamberDepthMm: fields.text({ label: 'Chamber depth (mm)' }),
        weightG: fields.text({ label: 'Weight (g)' }),
        filter: fields.text({ label: 'Filter — NONE / 9MM / 6MM / ADAPTER' }),
        stemMaterial: fields.text({ label: 'Stem material — vulcanite / acrylic / amber / horn' }),
        mount: fields.text({ label: 'Mount or band — NONE / silver / gold / nickel (+ hallmark)' }),

        photoRoles: fields.object(
          {
            left: fields.text({ label: '1 · Left profile' }),
            right: fields.text({ label: '2 · Right profile' }),
            rim: fields.text({ label: '3 · Rim & chamber from above' }),
            underside: fields.text({ label: '4 · Underside / shank' }),
            stem: fields.text({ label: '5 · Stem & button, both faces' }),
            grain: fields.text({ label: '6 · Three-quarter / grain' }),
            stampA: fields.text({ label: '7 · Stamp close-up A' }),
            stampB: fields.text({ label: '8 · Stamp close-up B' }),
            defect: fields.text({ label: '9 · Defect close-up — required if any part is below Very Good' }),
            extras: fields.text({ label: '10 · Box, sock, papers or scale' }),
          },
          { label: 'Photograph roles — image URL per pose. Fixed order, never reordered silently.' }
        ),

        descriptionSource: fields.select({
          label: 'Description source',
          options: [
            { label: 'Typed by hand (does not meet the standard)', value: 'typed' },
            { label: 'Generated from this record', value: 'generated' },
          ],
          defaultValue: 'typed',
        }),
        note: fields.text({ label: 'The eye — opinion, kept separate from the facts', multiline: true }),
        noteAuthor: fields.text({ label: 'Signed by' }),
        sourceClass: fields.text({ label: 'Source class — estate lot / single owner / trade / new stock' }),
        workDone: fields.text({ label: 'Work done in our hands', multiline: true }),
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
