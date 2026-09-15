---
description: Add a product to the catalogue from a description or listing
argument-hint: [department] [description or listing text]
---

Add a product to `content/products/` as a Keystatic YAML entry.

Input: $ARGUMENTS

Rules:
- Match the schema of the existing files in `content/products/` exactly — read
  one first. Required: `id`, `name`, `brand`, `slug`, `department`, `category`,
  `price`, `sku`, `images`, `inStock`, `description`, `tags`.
- `rating: 0` and `reviewCount: 0`. Always. A new item has no reviews, and the
  UI correctly hides stars at zero — do not seed a number to make it look better.
- `price` in the store's currency (GBP today), a plain number, no symbol.
- `description` describes only what is evidenced in the source: maker, era,
  materials, measurements, condition including flaws. If the era or maker is
  inferred rather than marked, write "attributed" or "unmarked" — never assert it.
- `images` must be real photographs of this item on an allowed host from
  `next.config.mjs`. Never an Unsplash placeholder.
- `slug` is kebab-case and unique; check for collisions before writing.

If anything required is missing from the input, ask for it rather than inventing
it — a guessed provenance on a £400 estate pipe is a refund and a bad review.
