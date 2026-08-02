import holdings from '@/content/references/holdings.json'

export type ReferenceItem = {
  title: string
  year: number | null
  format: string
  pages?: number
}

export type ReferenceShelf = {
  key: string
  title: string
  blurb: string
  items: ReferenceItem[]
}

export type ReferenceMirror = {
  key: string
  title: string
  note: string
  files: number
  gigabytes: number
}

export type Holdings = {
  generated_from: string
  totals: {
    files: number
    gigabytes: number
    catalogued_items: number
    dated_span: [number, number] | null
  }
  mirrors: ReferenceMirror[]
  shelves: ReferenceShelf[]
}

/**
 * The reference library, generated from the ark manifest by
 * `scripts/build-references.mjs`. This is a bibliography: it says what we hold.
 * It never links to, serves, or reproduces a single held page — see LAW 2.
 */
export function getHoldings(): Holdings {
  return holdings as Holdings
}
