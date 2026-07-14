# Pipe Dating Directory — Blueprint

## The Collector's Identification System

A structured reference that lets a collector **date and identify an estate pipe
from the physical evidence on the pipe itself** — the country stamp, the silver
hallmark, the patent number, the logo form, the fitment.

### The one rule that governs every design decision

There is a person we build for. Call him **the appraiser**. Someone hands him a
pipe and he asks ten questions — _What does the shank stamp read? Is there a
silver band? Does it carry a hallmark? Is there a patent number? What does the
logo look like?_ — and then he spends real effort and real time going away and
coming back with **part** of the dating evidence.

That round-trip is the system's failure. Every time the appraiser has to work
hard, dig through scattered notes, or come back with an incomplete answer, the
system has failed him.

> **Success is measured by how easy the appraiser's job becomes.**
> If he can answer his ten questions in a single pass, reading straight down one
> cabinet, and walk away with a defensible date — the system has succeeded.

Everything below serves that one measure.

## How a cabinet works

A **cabinet** is one maker (Peterson, Dunhill, Barling, GBD, …). Inside it, the
appraiser's ten questions become an ordered list of **markers** — each marker is
one question, the place on the pipe to look, and a table of **readings** that map
what he sees to a date range and a confidence level.

Markers are ordered by **decisiveness**, not by convenience:

1. **Primary markers** move the date the most (country-of-manufacture stamp).
2. **Precision markers** pin an exact year when present (silver hallmark).
3. **Corroborating markers** narrow within an era (logo form, patent number,
   fitment, finish).

The appraiser reads top to bottom. The first primary marker sets the broad era;
a precision marker, if present, overrides it with an exact year; corroborating
markers narrow and cross-check. He never has to leave the cabinet.

### Evidence overrides estimate

A stamp gives an era; a **hallmark or patent number gives a fact**. When physical
evidence conflicts with a stamp-based estimate, the physical evidence wins, and
the cabinet says so explicitly. We never present a guess with the confidence of a
fact.

## Data model

One YAML file per cabinet in `content/dating/`, editable in the CMS as the
**Dating Cabinets** collection. Shape:

```yaml
maker: <slug>              # url + filename, e.g. "peterson"
displayName: <string>
aka: [<string>, ...]        # alternate names / abbreviations
country: <string>
founded: <string>
status: active | defunct
summary: <string>           # what the maker is, in one paragraph
howToUse: <string>          # how to read this specific cabinet
markers:
  - id: <slug>
    label: <string>         # short name of the marker
    question: <string>      # the appraiser's actual question
    whereToLook: <string>   # where on the pipe to find it
    priority: <int>         # 1 = read first
    weight: primary | precision | corroborating
    readings:
      - reads: <string>     # what the evidence literally shows
        indicates: <string> # human-readable date range
        from: <int|null>    # numeric range for sorting/UI
        to: <int|null>
        confidence: high | medium | low
        note: <string>      # caveats, disambiguation
quickFlow: [<string>, ...]   # the ordered decision path, plain language
sources: [<string>, ...]     # references the readings are drawn from
```

## Roadmap

- [x] Blueprint + data model
- [x] **Peterson cabinet** (first cabinet — the reference implementation)
- [x] `/dating` directory index + `/dating/[maker]` cabinet page
- [ ] Dunhill cabinet (date code / suffix system — highly precise, great fit)
- [ ] Barling cabinet (family-era vs Transition vs Corporation)
- [ ] GBD, Comoy's, Sasieni, Charatan
- [ ] Cross-link cabinets from matching estate-pipe product pages
- [ ] Optional guided wizard UI that walks the quickFlow question by question

## A note on accuracy

Year boundaries encode **collector consensus**, not certainty — the literature
itself disagrees at the edges, and the cabinet records that with confidence
levels and notes. The directory is built to be corrected and extended in the CMS
as better evidence surfaces. It is a research aid, not an appraisal or a
certificate of authenticity.
