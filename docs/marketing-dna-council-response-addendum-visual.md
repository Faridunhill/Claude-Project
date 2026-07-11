# COUNCIL RESPONSE — MARKETING DNA (Addendum: Visual Generation)

Brief: Addendum to Round 2, Advisor F (CODE) — automated visual
generation as a planned EXPRESSION-layer generator
Respondent: Advisor F
Date: 2026-07-11
Scope: V1–V4 only. Synthesis v1.0 reviewed; it records my positions
accurately and I raise no corrections to it.

---

## Position in one line

The architecture absorbs this capability without modification — that is
what the expression layer is *for* — and the honest answer to half of
this addendum is the one your scope-discipline note invited: **most of
it needs nothing until the first generator is built.** What cannot wait
is exactly three things: one placement law, one control-file block, and
one enum value. Everything else is deferral with a trigger.

---

## V1 — GENOME IMPLICATIONS

**Zero new genome fields.** Applying convergence point 4 ruthlessly,
every candidate fails the test of being a *fact about the object* with a
named consumer that doesn't already have what it needs:

| Candidate | Verdict | Where it actually lives |
|---|---|---|
| Brand visual-style tokens | **Reject as genome.** Not a fact about any object — it is generator *configuration*, and it is per-business, not per-item or per-cohort. | One `style.yaml` per business (palette, mood, composition rules, forbidden motifs). Consumer: the prompt assembler of every visual generator. Versioned like code, because it is code. |
| Negative constraints ("never depict smoking") | **Reject as field.** Already derivable: `compliance.smoking_related: true` exists in the genome. A constraint stored per-item is a rule denormalized 500 times. | One rule in the existing compliance rules engine: `smoking_related → never depict consumption, never depict a person using the product`. Consumer: prompt assembler + post-generation checker. |
| Per-item visual hooks | **Reject.** `why_special` already carries the per-item hook (V2 ruling, fields-vs-spend). | Exists. |
| Reference imagery for conditioning | **Already present.** `media[]` with roles is the conditioning source; a generator that wants "the actual pipe" reads genome photos. | Exists. |

The generators need only what exists, plus one business-level config
file that was always going to exist the moment any generator ran.

**The one law that must be written now** (a placement rule, not a
field): **generated imagery may never occupy a listing-image slot for a
unique physical item.** For one-of-ones, listing images are genome
photographs only — the buyer is buying the exact object, and a synthetic
image in that context is misrepresentation regardless of intent.
Generated visuals are legal only on corpus surfaces (hub pages, sold
archive, social, email) and in contexts a reasonable buyer cannot read
as "this is the item." Enforced in the channel adapters, same lock
pattern as the QA gate: the adapter refuses `is_synthetic` assets for
listing slots. This costs one `if` statement now and prevents the single
worst reputational accident available to this system.

## V2 — THE GENERATED-ASSET MANIFEST

Minimal record, one per generated asset, expression layer. Ten fields;
each names its consumer:

```yaml
asset_id: gen-2026-000123            # join key — everything downstream
markets: cohort:estate/dublin        # sku:… | cohort:… | page:… | business:…
                                     # consumer: placement engine; regeneration scope
purpose: hub_banner                  # enum: archive_hero / hub_banner /
                                     #   social_cohort / email / lifestyle
                                     # consumer: placement rules + compliance check
source_refs: [FH-TP-034/media/2, style.yaml@v3]
                                     # genome inputs used — consumer: regeneration,
                                     #   truthfulness audit (was real flaw data respected?)
generator: {vendor: "…", model: "…", version: "…"}
                                     # consumer: license lookup; vendor-deprecation sweeps;
                                     #   quality regression by model version
prompt: {template_id, template_version, resolved_hash}
                                     # consumer: exact regeneration; template A/B later
license: {vendor_terms_version, commercial_ok, attribution_required, exclusive}
                                     # consumer: placement engine — platform eligibility
                                     #   is a license question as much as a content one
synthetic: {is_synthetic: true, disclosure_label: "…", provenance_mark: c2pa|none}
                                     # consumer: channel adapters — platforms increasingly
                                     #   REQUIRE AI-content labeling; this is the flag they read
depicts: {person: false, smoking: false, product_likeness: true}
                                     # content FACTS, not per-platform verdicts —
                                     #   the rules engine derives eligibility (core rule kept)
cost: {amount: 0.35, currency: USD}  # consumer: spend-guard ledger (V4)
status: live                         # draft / approved / live / retired
placements: [{channel: own_store, url: …, ts: …}]
                                     # consumer: takedown/retirement — when a license or
                                     #   platform rule changes, remediation is a query,
                                     #   not archaeology
```

The two fields photographs never needed — `license` and `synthetic` —
are the ones that bite years later. A vendor changes terms, or a
platform starts penalizing unlabeled AI imagery retroactively: with
`generator.vendor` + `placements[]`, finding every affected live asset
is one query. Without them it is a manual audit of everything ever
published. These two fields are the entire reason the manifest exists;
the rest is regeneration convenience.

Per-platform compliance *verdicts* stay out of the record, consistent
with the core rule: store content facts (`depicts`), derive eligibility
in the rules engine, because platform rules change faster than assets.

## V3 — THE FIREWALL QUESTION

**Confirmed — with one break flagged and one enforcement added.**

Maps cleanly: the visual-generation *method* (pipeline code, prompt
templates, the `style.yaml` schema, the manifest schema above) is the
version-pinned shared library from Round 1 Q6, under the Gemini E3 guard
already adopted — each business pins its version explicitly, no
auto-upgrades. Per business and never shared: vendor accounts, API keys,
spend ceilings and ledgers, generated-asset storage, and the *values* in
each `style.yaml`.

**Where it breaks — vendor-side commingling.** The firewall can be
breached by a third party even when your infrastructure is clean: one
vendor account serving two businesses leaks through workspace history,
shared seeds, billing, and above all **fine-tunes** — a custom style or
model trained on Business A's data and invoked by Business B is
infrastructure leakage laundered through the vendor. The rule
"credentials are not shared" must be stated more broadly: **no
vendor-side artifact (account, workspace, fine-tune, custom style,
uploaded reference set) is ever referenced by more than one business.**

**Enforcement, cheap:** the shared template library must contain no
business-specific values — templates take `style.yaml` as input, and a
lint check in the library's CI greps templates for brand names, domain
names, and account identifiers. A shared template with "Faridunhill"
hardcoded in it is the firewall leak in its larval stage.

## V4 — THE SPEND GUARD

Three numbers, same sacred class as `floor_price`, living in
`control.yaml` beside the ad guards (§8 of the synthesis), readable by
machines and writable only by the founder:

```yaml
visual_generation:
  max_cost_per_asset: 2.00      # USD — hard refusal above this; video and
                                #   premium models need a manual, logged,
                                #   per-SKU override (trophy tier only)
  monthly_ceiling: 50.00        # USD — across ALL vendors and businesses'
                                #   pipelines run from shared method; each
                                #   business carries its own ceiling in its
                                #   own control.yaml
  max_attempts_per_asset: 3     # generation + 2 retries, then human review
```

Why the third number is the important one: generation spend does not
fail by big purchases — it fails by **loops**. An agent judging its own
output "not good enough yet" and regenerating is a while-loop with a
credit card. The per-asset cap bounds one call, the ceiling bounds the
month, but `max_attempts_per_asset` bounds the failure mode nobody
prices in. After three attempts the asset goes to a human queue, which
is also a quality signal: anything the generator can't get right in
three tries is telling you about the template, not the seed.

Breach behavior mirrors the audit rule already adopted: ceiling hit →
generation pauses, founder gets one email. No silent throttling — silent
is how guards stop being read.

**Starting posture on the numbers:** $50/month funds roughly 100–500
image assets at current market rates — more corpus imagery than the hub
pages and sold archive can absorb monthly anyway. Start tight; a guard
loosened after evidence is governance, a guard set loose at birth is
decoration.

---

## Deferral statement (invited by the scope note, given plainly)

Build **now**: the placement law (one adapter check), the
`visual_generation` block in `control.yaml`, and `is_synthetic` as a
reserved concept in the expression-layer spec. Build **with the first
generator, not before**: the manifest, `style.yaml`, the depicts-checker,
the template lint. Nothing else. A manifest built before the first
generator exists will be designed against imagined vendors and rebuilt
anyway — the sockets above are the only parts that must predate the
plug.

---

## MANDATORY OUTPUT

### THREE WEAKNESSES of these answers

1. **The spend numbers are priors squared.** $2 per asset, $50 monthly,
   three attempts — invented not only ahead of the model's calibration
   (as in Round 2) but ahead of even *vendor selection*. If the chosen
   platform prices video at $8 a shot, the per-asset cap forbids the
   asset class the founder may most want; if it prices images at $0.02,
   the ceiling is so slack it guards nothing. These numbers must be
   re-set the week a vendor is chosen, and nothing in my answer forces
   that re-visit to happen.
2. **`license.commercial_ok` is a boolean wearing a lawyer's costume.**
   Real AI-vendor terms are volatile, ambiguous about indemnity and
   training-data provenance, and change retroactively. The manifest
   records the terms *version*, which makes remediation queryable — but
   a boolean gives false confidence that someone has actually read the
   terms, and nobody re-reads terms. The field is honest only if
   updating `vendor_terms_version` is somebody's named job.
3. **"Zero new genome fields" relocates bloat rather than killing it.**
   The complexity I kept out of the genome now lives in `style.yaml` and
   the rules engine — outside the schema, where governance-lite's three
   rules don't watch. A style manifest can grow forty tokens nobody
   consumes just as easily as a schema can, and my answer builds no
   fence around it. Convergence point 4 must be declared to apply to
   config files, or this answer has a hole in it.

### THREE RISKS the founder should watch

1. **Synthetic imagery bleeding into listings** is the one catastrophic
   accident this addendum makes possible. One generated "hero
   illustration" attached to a live one-of-one listing is
   misrepresentation of the exact item a buyer is paying for — a
   returns-feedback-forum-thread event in a business whose product is
   appraisal integrity. The adapter lock must exist before the first
   generator runs, and the weekly audit should include one synthetic-
   asset placement check. Treat any breach as a sev-1, not a bug.
2. **Retroactive platform rules on AI imagery.** Marketplaces, ad
   platforms, and search engines are actively tightening AI-content
   labeling — assets published compliantly today can be penalized under
   next year's rules. The `placements[]` index is the remediation tool;
   if it is allowed to go stale (assets republished by hand, channels
   added ad hoc), takedown becomes archaeology precisely when a deadline
   is running.
3. **Aesthetic drift at machine speed.** Generation is cheap, so volume
   will grow to fill the ceiling; without human sampling, the corpus
   fills with competent-but-generic imagery that quietly contradicts the
   connoisseur brand the estate business depends on. Fold one generated
   asset into the existing weekly 15-minute audit's five-product check —
   zero new process, and the drift gets caught while it is still a
   template fix.

### ONE DELETION

**Per-item generated visuals — cut the entire class.** If forced to
simplify, remove `archive_hero` and every per-SKU generation path, and
keep generation only at cohort level and above (hub banners, cohort
social, email headers), where one asset serves many items. The sold
archive already owns the most persuasive imagery possible for each item:
the genome photographs of the actual object. A generated illustration
beside them adds near-zero value at a cost that scales with the catalog
— it is the expression layer's version of the per-item persona field.
Cutting it also removes most of the spend-guard pressure and most of the
listing-bleed risk in one stroke.

---

FARID OS — Council Response — Addendum, Advisor F (CODE)
