# eBay sale logged → 2 items marked SOLD OUT on the storefront

**Date:** 2026-07-25 · **From:** Builder (cloud) · **Trigger:** Farid — "Builder continue. Sold in eBay" + Selling/Orders screenshot

## What sold (eBay order, buyer `zscho_60`, sold Jul 25, paid Jul 25, shipped — label created Jul 25)
Subtotal **$44.00** = 2 × $22.00, matches the catalog prices exactly.

| # | eBay title | Catalog file | SKU |
|---|-----------|--------------|-----|
| 1 | Vintage German Dual-Compartment Leather Pipe & Tobacco Pouch, NOS – 1970s-1990s | `content/products/vintage-german-dual-compartment-leather-pipe-tobacco-pouch-nos-1970s-1990s.yaml` | FH-LB-084 |
| 2 | German Leather Dual-Compartment Pipe & Tobacco Pouch, Humidity-Lined, NOS Estate | `content/products/german-leather-dual-compartment-pipe-tobacco-pouch-humidity-lined-nos-estate.yaml` | FH-LB-085 |

## Action taken (honesty law — never offer a sold piece)
Set `inStock: false` on both YAMLs. The storefront now shows them as **Sold Out**
(shop grid + featured tiles) and disables **Add to Cart** (renders "Out of Stock").
These are one-of-a-kind estate pieces, so sold = permanently off-market, not a restock.

## Matching note
Mapped by eBay title + price. eBay custom-label hashes (`…-7ab4e`, `…-93073`) are
eBay-side IDs and aren't stored in this repo, so the match is by title/price, which
is unambiguous here (only these two dual-compartment pouches at $22, and the $44
subtotal confirms it).

## For next time
When you sell on eBay, a screenshot of the Orders screen is enough — I'll match by
title + price and flip the piece to Sold Out. If you'd rather I also record a sale
date/buyer in a ledger, say so and I'll add a sales log.
