# Pipe Passport — Identification System Design

**Status:** Fully automated (AI vision assessment) — implemented.
Superseded decision: the original Phase 1 below planned manual expert review
by email; Farid requested full automation (no human in the loop), so the
service now runs on the Claude API (vision + structured output) and delivers
the assessment on-screen and by automated email. The Passport also moved
inside the Pipe Encyclopedia at `/encyclopedia/pipe-passport`.
**Owner:** Farid · Faridunhill
**Last updated:** 2026-07-21

This document records the design decisions for the Faridunhill pipe
identification system, including the evaluation of an external AI-generated
proposal ("Bloomberg Terminal of pipe collecting") and which parts of it we
adopt, defer, or reject.

---

## 1. The core thesis we adopt

The single best idea in the external proposal, and the foundation of this
system:

> **The free Pipe Passport is simultaneously the marketing funnel AND the
> training-data pipeline.**

Every free identification submission gives us three assets at once:

1. **A lead** — a collector with an estate pipe who now trusts Faridunhill.
2. **A labeled data row** — 6 standardized photos + structured metadata
   (brand guess, stamp transcription, measurements), which is exactly the
   dataset a future vision model needs.
3. **Authority** — a branded report the collector shares on forums and
   social media, which tobacco-ad bans cannot block because identification
   is not tobacco advertising.

This is why the submission form captures **structured fields, not just
photos**. Free-text-only submissions would be marketing leads but useless
as training labels.

## 2. The 6-photo protocol (adopted, standardized)

Every submission requires the same views so the dataset is uniform from
day one:

| Slot | View | Purpose |
|---|---|---|
| 1 | Left profile | Shape, bowl geometry, stem line |
| 2 | Right profile | Grain, fills, repairs |
| 3 | Top (bowl rim) | Chamber, rim condition, cake |
| 4 | Bottom (heel) | Shape number stamps, heel grain |
| 5 | Stamping close-up A | Nomenclature — shank left side |
| 6 | Stamping close-up B (optional) | Nomenclature — shank right side / stem logo |

Photos are downscaled client-side (max 1600 px, JPEG) before upload so the
whole submission stays under serverless request limits and mobile uploads
stay fast.

## 3. Legal framing (adopted verbatim in spirit)

- The word **"certificate" is never used**. The product is a *Pipe
  Passport*: an "identification and dating assessment".
- Standard disclaimer, shown on the page and included in every report:

  > The Faridunhill Pipe Passport is an identification and dating
  > assessment service based on comparative visual analysis, historical
  > catalogues, and market data. Results are provided as professional
  > opinions, not certificates of authenticity.

- Photos are used for identification and (with consent implied by the
  service terms shown on the form) for improving our reference database.
  GDPR note: submissions contain an email address; deletion requests must
  remove the email but may keep anonymized photos.

## 4. Phased plan (adapted — more honest timeline)

| Phase | What ships | Gate to next phase |
|---|---|---|
| **1 (now)** | `/pipe-passport` submission form → email to Farid → manual expert reply with reference ID. Free. | ~500 quality submissions collected |
| **2** | Structured storage (DB instead of email), internal review dashboard, PDF "Passport" report generation with branding + watermark | Steady weekly volume |
| **3** | RAG knowledge base over mirrored Pipedia/Pipephil + digitized catalogues; AI *assists* Farid (draft identifications he approves) | Assist accuracy proven on known pipes |
| **4** | Fine-tuned vision model (CLIP/ViT) on the by-then-labeled photo corpus; auto-ID for the big brands, human review for the rest. Premium tiers (express, provenance report, insurance valuation). | — |

The external proposal's "automate 60% of brands by month 6" is rejected as
a timeline: fine-tuning needs *cleaned, labeled* data, and the labels are
what Phases 1–2 produce. The architecture (multi-view fusion, OCR with
contrast enhancement for faint stamps, RAG over reference texts) is sound
and adopted for Phases 3–4.

## 5. Adopted / deferred / rejected — full verdict

**Adopt now (implemented in this repo):**
- Free Pipe Passport submission flow with 6-photo protocol
- Structured metadata capture (brand guess, stamp text, length, notes)
- "Assessment, not certificate" legal language
- Unique reference ID per submission (`FH-PP-…`) — this is the "digital
  provenance" idea done cheaply: a database ID, not a blockchain

**Adopt later (good ideas, wrong moment):**
- RAG over mirrored reference sites and catalogues (Phase 3)
- Vision model fine-tuned on the photo corpus; multi-view embedding fusion;
  faint-stamp image enhancement before OCR (Phase 4)
- Premium tiers: express ID, provenance report, restoration assessment,
  insurance valuation (Phase 4 — priced only after free volume proves demand)
- Consignment funnel: every passport reply can include "want us to sell it
  for you?" (can start manually any time)

**Rejected:**
- **Blockchain/NFT provenance** — the value is the database and the trust,
  not the token; a stable reference ID gives the same "Carfax" story with
  zero cost and no crypto-skeptic friction.
- **White-label API, insurance partnerships, authentication academy** —
  premature until the core service has volume and a track record.
- **Aggressive automation timeline** — see §4.

## 6. Phase 1 implementation (this repo)

- `app/pipe-passport/page.tsx` — public page: pitch, how-it-works, 6-photo
  upload form with client-side compression, legal disclaimer.
- `app/api/passport/route.ts` — validates the submission, generates the
  `FH-PP-` reference ID, and emails the full submission (photos attached)
  via Resend to the shop inbox; the reference ID is returned to the
  collector on the success screen.
- Navigation + footer link the page site-wide.

Phase 1 deliberately has **no database and no AI** — the deliverable is
Farid's expert reply, and the pipeline is designed so nothing collected now
is wasted later.
