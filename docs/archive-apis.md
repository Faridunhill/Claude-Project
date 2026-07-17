# Archive APIs for Maker Identification Research

Research notes for identifying makers of estate items (pipes, leather cases,
Solingen cutters) using national archive APIs. Covers the German archive
(Deutsche Digitale Bibliothek) reply of July 2026 and the English equivalents.

## 1. German archive — Deutsche Digitale Bibliothek (DDB)

The DDB confirmed by email that their **API 2.0 no longer requires an API
key** and is "largely identical" to the old API.

| | Old API (v1) | New API 2.0 |
|---|---|---|
| Base URL | `https://api.deutsche-digitale-bibliothek.de/` | `https://api.deutsche-digitale-bibliothek.de/2/` |
| API key | Required (register at "Meine DDB") | **Not required** |
| Docs | `https://api.deutsche-digitale-bibliothek.de/OpenAPI` | `https://labs.deutsche-digitale-bibliothek.de/app/ddbapi/?url=https%3A%2F%2Fapi.deutsche-digitale-bibliothek.de%2F2%2Fq%2Fopen` |

### Endpoints (same shape as v1)

- `GET /2/search?query=<solr query>&rows=<n>&offset=<n>&sort=<field>` — full-text search
- `GET /2/search/facets/{facetName}` — facet values (e.g. `provider_fct`, `place_fct`, `time_fct`)
- `GET /2/items/{id}` — full item record (id is a 32-char BASE32 SHA1)
- `GET /2/items/{id}/edm` — Europeana Data Model metadata (RDF/XML)
- `GET /2/items/{id}/binaries` — digitised images for the item
- `GET /2/search/person` / `GET /2/search/organization` — entity search (useful for maker firms)

Responses are JSON by default. Metadata is CC0; image rights vary per
institution — check per record before reusing photos.

### Useful queries for our catalogue

The `query` parameter takes Solr syntax, so exact phrases and boolean
operators work:

```
/2/search?query="Pfeifenfabrik"&rows=10
/2/search?query=Solingen AND Zigarrenabschneider
/2/search?query="Offenbach" AND Lederwaren
/2/search/organization?query=Lederwarenfabrik Offenbach
```

Offenbach am Main was the centre of the German leather-goods industry — the
DDB holds records from the Deutsches Ledermuseum (Offenbach), which is the
single most promising source for our unmarked German leather cases.

### Verification note

The DDB API servers reject requests from cloud/automated clients (HTTP 403),
so the endpoints could not be exercised from the CI sandbox. Run
`node scripts/check-archive-apis.mjs` from a normal machine to verify — it
queries API 2.0 without a key and prints hit counts per maker.

## 2. English archive — The National Archives (UK) Discovery API

For the England side, the equivalent open API is **Discovery** from The
National Archives (Kew). It requires **no API key**.

- Base: `https://discovery.nationalarchives.gov.uk/API/`
- Search: `GET /API/search/records?sps.searchQuery=<terms>&sps.resultsPageSize=<n>`
- Record detail: `GET /API/records/v1/details/{id}`
- Send `Accept: application/json` for JSON responses.
- Sandbox/docs: `https://discovery.nationalarchives.gov.uk/API/sandbox/index`

Discovery indexes registered company records (BT 31 dissolved-company files),
trademark registrations, and design registrations (BT 42–BT 53) — the primary
sources for dating English pipe and leather-goods firms (Charatan, Comoy's,
Darvil, etc.).

## 3. Cross-European fallback — Europeana

Europeana aggregates both DDB and UK collections in one API. It needs a
free key (instant, by email) — worth having as a fallback:

- `GET https://api.europeana.eu/record/v2/search.json?wskey=<key>&query=<terms>`

## 4. Identified vs. outstanding makers

Catalogue snapshot (264 products in `content/products/`):

- **Finished / identified:** the known-maker items are done — Dunhill(-style),
  Peterson-era attributions, Charatan of London, Comoy's of London, Georg
  Jensen, Stanwell, Ser Jacopo, Tsuge, Kirsch, and the other named workshops.
- **Outstanding (≈10 items, mostly German):** "Anonymous Atelier" hard
  leather travel cases, unmarked Solingen V-cut cutter, unbranded utility
  cases, unsigned c.1900 meerschaum — these are the DDB / Discovery research
  targets.

### Schema gap

Identification currently lives only in the product **name** string. The
Keystatic schema already has `brand` and `origin` fields, but only 2 of 264
product files populate `brand`. When archive research confirms a maker,
record it in `brand`/`origin` (and `specs`) rather than only rewriting the
title — that keeps identification queryable and lets the shop filter by
maker later.
