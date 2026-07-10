# ASHCOMBE — COMMANDER BRIEF
Classification: Executive — Action Order
Version: 1.0.0 | Date: 2026-07-10
Author: Claude Code (builder seat) | Approved direction: Farid Hadid
KB Tag: farid:
Basis: ASHCOMBE_AUTONOMY_REDTEAM_CLAUDE_v1_0.md (v1.1, council-agreed)
Status: LOCKED decisions + first build steps. Simple language on purpose.

---

## 1. WHAT WE ARE BUILDING (THE FINAL PRODUCT)

Three pieces. Together they are the product:

1. **THE AGENT** — the AI manager. Runs the store: pricing, listings,
   sourcing choices, customer replies.
2. **ACADEMY** — the school + report card. Tests the agent, catches
   mistakes, feeds corrections back. Over time it improves the whole
   system. This loop is the core of the build.
3. **THE PROOF LOG** — a sealed, tamper-proof record showing the AI made
   the decisions. Filed tax return + this log = the proof artifact.
   **This is the invention. Nobody has this yet. The clock is running**
   (Andon Labs can file for FY2026 — move with urgency).

## 2. LOCKED DECISIONS (COUNCIL 5/5 — DO NOT REOPEN)

- **Build order: ACADEMY first.** The brain before the eye.
- **The brain runs on frontier cloud API**, not the local 12GB machine.
  Local machine is for the EYE side experiment only.
- **Bookkeeping gets automated too** (Avalara/Kintsugi-class tool).
  No human touching the books = no hole in the autonomy claim.
- **Vision for daily operations is BOUGHT, not built** — the agent calls
  a frontier multimodal model to identify products from photos.

## 3. THE EYE — SIDE EXPERIMENT (AGREED)

- THE EYE continues as a **side lab, off the critical path**. The DINOv3
  pipeline (95.1% on pipes) keeps evolving on the local 12GB machine.
- Goal of the side lab: find the "secret" in identification — what makes
  luxury goods recognizable/authenticatable beyond what the big models do.
- Rule: the main system NEVER waits for the EYE. If the side lab one day
  beats the bought vision API on Ashcombe items (measured, not felt),
  it gets promoted to a tool the agent calls. Until then: experiment.

## 4. HOW FULL AUTOMATIC WORKS (SIMPLE)

1. Agent reads store data: sales, stock, messages, photos.
2. Agent decides: price / listing / reorder / reply.
3. Every decision is written to the sealed log (hash-chained, timestamped).
4. Guardrails check it: spending caps, price floors/ceilings.
   Inside limits → executes alone. Outside limits → asks Farid.
   Every human touch goes into an INTERVENTION LEDGER (also sealed).
5. ACADEMY reviews outcomes, corrects mistakes, agent improves.
6. After a full year: filed return + sealed log = the proof.

Farid's only jobs: shipping + rare out-of-limits approvals.

## 5. CONNECTING TO THE EXISTING SYSTEM (EASY BY DESIGN)

The agent is a layer ON TOP of what already exists — nothing gets rebuilt:

- **Supabase (Gate B done: RLS + admin)** → becomes the agent's memory.
  Add tables: `decision_log` (append-only, hash-chained),
  `intervention_ledger`, `guardrail_limits`, `academy_results`.
- **Existing storefront (this repo, Next.js)** → agent manages products/
  prices through the same admin API routes that already exist. No new
  storefront.
- **Stripe (next gate)** → wire it as planned; the agent reads
  transactions, never holds keys with unlimited power (restricted key +
  spend cap).
- **DINOv3 pipeline (local)** → untouched, becomes the EYE side lab.
- **Reasoning** → cloud API (Claude/frontier) with tool-calling into the
  above. The agent is prompts + tools + logs, not a trained local model.

## 6. FIRST STEPS WHEN BACK AT PC (IN ORDER)

1. **Evidence first (before any agent code):** create the `decision_log`
   and `intervention_ledger` tables in Supabase — append-only + hash chain.
   Write the one-page rule: what counts as a DECISION vs. an EXECUTION.
2. **Guardrail file:** spend cap, price floor/ceiling, daily loss limit.
3. **ACADEMY v0:** a simulation harness — fake store data, agent makes a
   week of decisions, we score them. No real money until it passes.
4. **Pre-register the protocol:** one document, dated and hashed, saying
   what the experiment claims and how it's measured. Sign it before day 1.
5. **Legal/CPA call** (before live money): who signs the return, what can
   be published, platform rules.
6. EYE side lab continues in parallel, no dependency.

## 7. WHAT SUCCESS LOOKS LIKE, ONE LINE

A year of store decisions made by the agent, provable by a sealed log a
stranger can verify, attached to a filed return — built as a thin layer
on the Supabase/Stripe/Next.js stack that already exists.

---

## VERSION HISTORY
v1.0.0 | 2026-07-10 | Claude Code | Commander brief after council v1.1 agreement: ACADEMY-first locked, EYE kept as side experiment, bookkeeping automated, evidence layer built first.
