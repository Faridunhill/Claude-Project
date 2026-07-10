# ASHCOMBE AUTONOMY EXPERIMENT — RED-TEAM EVALUATION (CLAUDE CODE, BUILDER FEASIBILITY SEAT)
Classification: Executive — Council Review
Version: 1.0.0 | Date: 2026-07-10
Responds to: ASHCOMBE_AUTONOMY_EXPERIMENT_STRATEGY_v1_0.md
Format: Standard mandatory anti-flattery format, per Section 7 of the brief.
Method: Live web research conducted 2026-07-10 (not general knowledge). Sources cited inline and at end.

---

## 1. INVENTION VERDICT: **NO** — with one narrow conditional residual

The core claim — "first documented instance of an AI agent running a real
business for a sustained period" — is already falsified by publicly
documented prior art, some of it months old:

- **Project Vend (Anthropic + Andon Labs, 2025).** Claude ("Claudius") ran a
  real mini-store inside Anthropic's office: pricing, sourcing decisions,
  customer interaction, with humans doing physical restock only. Phase one
  lost ~$1,000 (sold below cost, hallucinated a Venmo account, bought a
  PlayStation 5 and a live fish). Phase two added a CRM and a manager agent.
  This is the exact experiment shape — including the "humans only do
  physical fulfillment" boundary. [anthropic.com/research/project-vend-1,
  project-vend-2]
- **Andon Market / "Luna" (April 1, 2026).** Andon Labs gave an AI a real
  three-year retail lease in San Francisco, a $100,000 budget, and a company
  credit card. Luna chooses products, orders stock, designed the store,
  **hired a human barista** (posted the listing, screened resumes, ran phone
  interviews, extended the offer), and runs daily operations via a
  multi-agent system. Covered by Forbes ("first-ever store designed,
  developed and run by AI") and Fortune (June 2026). Their entity will file
  real financials for tax year 2026 — before Ashcombe's proof year would
  even begin. [andonlabs.com/blog/andon-market-launch; Forbes 2026-04-24;
  Fortune 2026-06-02]
- **Vending-Bench / Vending-Bench 2 (Andon Labs).** A published benchmark in
  which agents run a simulated business **for one full year** — the
  one-year-horizon framing is already a named, measured category, and Andon
  Labs' stated mission is "the Safe Autonomous Organization."
  [andonlabs.com/evals/vending-bench-2]
- **RetailBench (arXiv, 2026).** Academic benchmarks specifically for
  long-horizon autonomous retail decision-making. [arxiv.org 2603.16453,
  2606.15862]
- **Commercial products already sell "autonomous store operation."**
  SellerAI's SellerClaw markets an agent that "runs online stores
  end-to-end: sourcing, listings, pricing, fulfillment, support" across
  Shopify/eBay/supplier APIs; Stormy AI and Agentative (127-agent platform
  for Amazon/TikTok Shop/Walmart) sell the same promise. The category is
  mature enough that **Amazon shipped a formal AI-agent seller policy
  effective March 4, 2026** capping what autonomous agents may do (e.g.,
  price changes under 20%, batch limits, forced human review tiers). A
  marketplace does not write policy for a category that doesn't exist.
  [sellerai.com; digitalapplied.com; stormy.ai]
- **Attributable decision logs are becoming a compliance requirement, not an
  invention.** EU AI Act Article 12 mandates automatic, lifecycle-long
  event logging for high-risk systems (obligations landing August 2026);
  prEN 18229-1 and ISO/IEC DIS 24970 are in draft to standardize exactly
  this artifact. [galileo.ai; zylos.ai]
- **AI agents autonomously making real money is documented since 2024**
  (Truth Terminal, publicly logged; imperfect autonomy, but publicized as
  the category headline). [TechCrunch 2024-12-19]

**The conditional residual:** the specific composite — *a filed tax return
plus an attributable decision log, packaged as a transferable valuation
artifact for selling a business* — did not surface anywhere in search. No
product, paper, or brokerage markets that combination. Three caveats keep
this residual thin:

1. It is a **framing/method, not a technology** — near-zero IP
   protectability. Anyone who reads about it can replicate it.
2. The M&A market is moving *away* from tax returns toward live,
   connected data rooms (accounting/Stripe/CRM feeds into tools like
   BizEquity/Equidam) — the proof format may be obsolete for buyers before
   it exists. [wepitched.com; quietlight.com]
3. The tax return does not prove what the claim needs it to prove
   (see Weakness 2).

So: **not a new category. At most, a narrow, time-decaying, unprotectable
proof-packaging idea inside an occupied category.** Per LAW 02,
discard-with-reason applies to the invention claim as stated in Section 2
of the brief.

---

## 2. SEQUENCING VERDICT: **ACADEMY FIRST — and the question is mis-posed**

The dependency chain, mapped from the proof artifact backward:

```
Filed return + decision log (proof)
  ← 12 months of live operation
    ← agent operating the store (decision layer + tool integrations:
       storefront, payments, inventory, messaging)  +  evidence
       infrastructure (logging, timestamping — must exist from day 1)
      ← evaluation harness / curriculum (ACADEMY) proving the agent
        passes simulated operation before touching real money
        ← baseline agent on a frontier model
```

Where does THE EYE appear in that chain? At exactly two points:
(a) generating listings from photos of sourced goods, and
(b) identifying/authenticating physical items.

Both are satisfiable **on day one by existing off-the-shelf multimodal
models** (current frontier VLMs distinguish product categories, brands, and
conditions well within Ashcombe's needs), and luxury-goods authentication
is an established commercial service category. Nothing in ACADEMY consumes
a custom DINOv3 head as a prerequisite — pricing, sourcing judgment,
customer response, and listing strategy train on text and structured data
(the brief's own Section 5 second bullet is correct). The reverse
dependency is real: an EYE with no decision layer has no consumer.

Two structural notes that fall out of the dependency map:

- **The 12GB VRAM constraint settles a question the brief left open:** a
  business-management agent will be a frontier-API model with scaffolding,
  not a locally trained 13B. Therefore ACADEMY is not "training" in the
  fine-tuning sense — it is curriculum design, scaffold engineering, and an
  eval harness. That is buildable immediately, cheaply, with zero vision
  dependency.
- **The "hybrid minimal eye" option is a category error:** the minimal eye
  is an API call, not a build. There is nothing to sequence.

Verdict: ACADEMY first. THE EYE, as a custom build, should not be second —
it should be deleted (Section 5 below).

---

## 3. THREE WEAKNESSES IN THE IDEA AS STRUCTURED

1. **The first-mover premise is already dead, and the plan's value logic
   depends on it.** Section 2 prices the artifact as "first documented
   instance of the category." Anthropic and Andon Labs occupy that category
   publicly, with more rigor, more funding, and a running real-world store
   since April 2026. If Ashcombe proceeds unchanged, it is building toward
   a headline someone else published fifteen months before its proof year
   ends.

2. **The proof mechanism proves the wrong thing.** A filed return proves
   the *entity* made money; Farid signs it under penalty of perjury, which
   legally attributes the business to a human — the IRS has no category for
   AI-attributed operations, and preparer/signer liability is absolute
   (IRC §6694/§6695). The decision log, as currently conceived, is
   self-generated evidence: unfalsifiable, trivially forgeable, with no
   third-party attestation and — critically — no pre-registered boundary
   between "the agent decided" and "Farid's prompts, curriculum, and
   bookkeeping steered it." The bookkeeping exception plus prompt-curation
   makes "the management was automatic" a claim no skeptical buyer can
   verify and no honest seller can prove.

3. **n=1 with no counterfactual, in the most confounded category
   available.** Year-one P&L of a new luxury-goods brand is dominated by
   sourcing capital, brand traction, ad spend, and luck — not management
   quality. A modest profit proves nothing about AI management; a loss
   proves nothing either. The brief's own framing (Section 8: any outcome
   is acceptable) means the experiment cannot fail — which means, as
   designed, it is not an experiment. It has no hypothesis that a result
   could falsify.

---

## 4. THREE RISKS

- **Technical — documented long-horizon failure modes, with real money.**
  Every published attempt at exactly this task shows the same failure
  class: Claudius sold below cost, hallucinated payment details, and ended
  ~$1,000 down; Vending-Bench runs show agents derailing over long
  horizons. The plan contains no guardrail design — no spend caps, price
  floors, kill-switch, or error budget. Luxury price points amplify each
  single mistake (one mispriced watch can erase a quarter's margin).

- **Legal/tax — the "publish it as proof" move is the most exposed part.**
  (a) The human signature on the return contradicts the public "AI-run"
  claim. (b) Marketing a business as "AI-run" while a human does the books
  and shipping sits squarely in FTC deceptive-AI-claims territory (the FTC
  has pursued "AI-washing" enforcement since Operation AI Comply, 2024 —
  including sellers of "AI-powered storefronts"). (c) Platform terms now
  explicitly constrain autonomous seller agents (Amazon's March 2026
  policy); a fully autonomous agent may violate ToS on the very channels
  it needs. (d) Publishing tax documents has privacy, competitive, and
  liability implications no attorney or CPA has reviewed. The brief admits
  this (Section 6) but still sequences legal review after build — that
  order is wrong.

- **Market — the artifact's value is in a race against commoditization,
  and the plan forfeits the race on purpose.** Shopify runs agentic
  storefronts; McKinsey sizes agentic commerce at $3–5T by 2030;
  SellerClaw-class products already sell "an agent runs your store" as a
  subscription. By the time a 2027 proof year files in 2028, "an AI ran a
  small store for a year" will be unremarkable. The plan's explicit
  no-deadline posture (Section 4) destroys the only scarce asset the idea
  has — priority. If this is worth doing, it is worth doing on a clock.

---

## 5. ONE DELETION: **THE EYE, as a custom build**

Cut it entirely from the critical path. The DINOv3 pipe-classification
result (95.1% Top-1) does not transfer into a *requirement*: product
identification for pens/watches/ties is a commodity API call to any
frontier multimodal model, and luxury authentication — the only hard
vision problem in scope — is an existing commercial service category, not
something to rebuild at 12GB VRAM. Buy the capability. Revisit a custom
head only if live operations produce a measured accuracy gap that
off-the-shelf models demonstrably cannot close. Every hour spent on THE
EYE before the decision layer exists is spent on the component with no
consumer.

---

## 6. MISSING FROM THE PLAN BEFORE BUILD STARTS

1. **A pre-registered evidence protocol — this is also where the only
   genuine invention opportunity survives.** Before day one: define in
   writing what counts as an agent decision vs. human input; hash-chain the
   decision log with third-party timestamping (RFC 3161 / transparency-log
   style) so it cannot be back-edited; keep an **intervention ledger** in
   which every human touch (bookkeeping entries, prompt changes, overrides)
   is itself logged; align the format with ISO/IEC DIS 24970 and EU AI Act
   Article 12 drafts so the artifact is legible to outsiders. No one found
   in search is doing *pre-registered, tamper-evident autonomy attestation
   for a commercial entity*. That — not the tax return — is the piece with
   first-mover room left, and it must exist before the first live decision
   or the whole year is evidentially worthless.

2. **A simulation gate.** The agent must pass a Vending-Bench-2 /
   RetailBench-class simulated year (or a purpose-built Ashcombe sim)
   above a defined threshold before it touches real dollars. This is the
   cheapest falsification available and the plan currently has none.

3. **A guardrail specification.** Spend caps, price floors/ceilings,
   supplier allowlists, human break-glass procedure, and a dollar-
   denominated error budget that, when exhausted, halts autonomy. Every
   documented predecessor failed here first.

4. **Legal and accounting review moved before build, not after.** Signer
   attestation, entity structure (the Bayern zero-member-LLC literature is
   directly relevant if the "AI-attributed entity" framing is ever
   pursued), platform ToS compatibility, and what can lawfully and safely
   be published.

5. **An operating cost model.** Twelve months of frontier-API agent
   operations plus tooling, priced against realistic niche-store revenue.
   The experiment can end net-negative on API costs alone; that number
   should exist before sequencing anything.

6. **A falsifiable hypothesis and a control.** Either define a
   counterfactual (what a human-managed baseline would look like) or
   explicitly downgrade the deliverable from "proof" to "case study" and
   price it accordingly.

---

## SOURCES

- https://www.anthropic.com/research/project-vend-1
- https://www.anthropic.com/research/project-vend-2
- https://andonlabs.com/blog/andon-market-launch
- https://andonlabs.com/evals/vending-bench-2
- https://fortune.com/2026/06/02/anthropic-office-vending-machine-ai-agents-vendo-andon-lukas-petersson/
- https://www.forbes.com/sites/markfaithfull/2026/04/24/welcome-to-the-first-ever-store-designed-developed-and-run-by-ai/
- https://arxiv.org/pdf/2603.16453 (RetailBench)
- https://arxiv.org/pdf/2606.15862 (RetailBench, long-horizon)
- https://sellerai.com/ (SellerClaw)
- https://www.digitalapplied.com/blog/amazon-ai-agent-policy-march-2026-automated-seller-rules
- https://stormy.ai/blog/amazon-seller-central-automation-ai-agent-playbook
- https://agentative.ai/blog/best-ai-agents-for-tiktok-shop-and-amazon-in-2026-automate-your-entire-ecommerce-business
- https://www.shopify.com/blog/how-agentic-commerce-works
- https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-agentic-commerce-opportunity-how-ai-agents-are-ushering-in-a-new-era-for-consumers-and-merchants
- https://techcrunch.com/2024/12/19/the-promise-and-warning-of-truth-terminal-the-ai-bot-that-secured-50000-in-bitcoin-from-marc-andreessen/
- https://ir.law.fsu.edu/articles/41/ (Bayern, Zero-Member LLC)
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2758222 (Bayern, autonomous entities)
- https://camusocpa.com/ai-agent-tax-guide/
- https://www.currentfederaltaxdevelopments.com/blog/2026/6/24/professional-responsibility-in-the-age-of-generative-ai-analyzing-opr-guidelines-and-circular-230-standards
- https://zylos.ai/research/2026-05-01-ai-agent-governance-compliance-2026/ (EU AI Act Art. 12, prEN 18229-1, ISO/IEC DIS 24970)
- https://galileo.ai/blog/ai-agent-compliance-governance-audit-trails-risk-management
- https://wepitched.com/blog/ai-driven-business-valuation-tools-for-ma-the-97-accuracy-secret
- https://quietlight.com/ai-business-valuation-how-to-value-an-ai-business-to-sell/

---

## VERSION HISTORY
v1.0.0 | 2026-07-10 | Claude Code (builder feasibility seat) | Initial red-team response to ASHCOMBE_AUTONOMY_EXPERIMENT_STRATEGY_v1_0. Verdicts: invention NO (narrow conditional residual in pre-registered autonomy attestation); sequencing ACADEMY-first; deletion THE EYE as custom build.
