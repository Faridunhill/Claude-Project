# The Council roster — Farid's slate, checked (2026-09-11)

Farid proposed seven seats and a model for each. Every model was verified on OpenRouter
today under Law 7. **Five of seven confirmed as proposed. Two corrected. One seat's
reasoning was wrong even though the model is real.**

## Verdict table
| Seat | Farid's pick | Verdict | My call |
|---|---|---|---|
| Chair | ChatGPT 5.6 Sol | **CONFIRMED** — `openai/gpt-5.6-sol`, released 2026-07-09, flagship of the 5.6 line, served by OpenAI + Bedrock + Azure | **keep** |
| Engineer | DeepSeek V4 | **CONFIRMED with a choice to make** — two SKUs: `deepseek/deepseek-v4-flash` ($0.068/$0.168 per M) and `deepseek/deepseek-v4-pro` ($0.87/$1.74 per M). Both 1M context | **keep — use V4 Pro.** The Engineer reads real code; Flash is for volume, Pro is for judgement. Still ~7× cheaper than the Chair |
| QC | Gemini 3.1 Pro | **WRONG NAME** — no Gemini 3.1 **Pro** on OpenRouter. The Flash line carries video+audio: 3.7 Flash (2026-08-13) and **3.8 Flash (2026-09-02)**, both text+image+**video+audio** in, $0.75/$3.75 per M (intro rate to 2026-12-31, then $1.50/$7.50) | **`google/gemini-3.8-flash`** — newest, same price, biggest gain on long multi-step work, which is what checking a whole render against 8 criteria is |
| Researcher | Perplexity | **CONFIRMED** — `perplexity/sonar-pro` on OpenRouter, $3/$15 per M, **live web search and citations included in every SKU, no per-query fee**, and citation tokens stopped being billed in 2026 | **keep — Sonar Pro.** Plain `sonar` ($1/$1) for cheap checks |
| Art director | Gemini 3.7 Flash | **CONFIRMED, but do not pair it with QC on the same family** — see the correlation rule below | **switch to `x-ai/grok-4.6`** (vision, $2/$6) **or** keep 3.7 Flash and move the Pipe expert off Grok. One of the two must move |
| Doubter | Kimi K3 | **WRONG REASON** — `moonshotai/kimi-k3` is real (2026-07-16, 2.8T, 1M context, $2.40/$12 on OpenRouter), but Farid's reason was "invents the fewest false facts" and the independent benchmark says the **opposite**: on Artificial Analysis Omniscience its hallucination rate rose 39% → 51% as accuracy rose 33% → 46%. It answers more and invents more | **keep the model, change the job.** K3 is a fine attacker — imagining failures is where confident invention costs nothing. But the Doubter may **never** assert a fact; every claim it makes goes to the Researcher. Written into the charter |
| Pipe expert | Grok | **CONFIRMED** — `x-ai/grok-4.6` (2026-08-12), $2/$6, 500K context. Note there is **no Grok 5**; 4.6 is current | **keep**, unless Art director takes Grok (see above) |

## The one structural fix
Two seats on the same family = one vote, not two (Apple's nine-judges study, already in
COUNCIL_SPEC §1). Farid's slate puts **Gemini on both QC and Art director**. Fix by moving
one. My preference: **QC = Gemini 3.8 Flash** (it is the only seat that must watch video and
hear audio, and Gemini is the cheapest model that does both), **Art director = Grok 4.6**,
**Pipe expert = Kimi K3**, **Doubter = Claude** (any Anthropic model Farid can reach) — or,
if he wants no Anthropic seat, Doubter stays Kimi and Pipe expert moves to `gpt-5.6-terra-pro`.

## The roster I would run
| Seat | Model | OpenRouter id | Price in/out per M |
|---|---|---|---|
| Chair | GPT-5.6 Sol | `openai/gpt-5.6-sol` | flagship tier |
| Engineer | DeepSeek V4 Pro | `deepseek/deepseek-v4-pro` | $0.87 / $1.74 |
| QC (sees + hears) | Gemini 3.8 Flash | `google/gemini-3.8-flash` | $0.75 / $3.75 |
| Researcher | Perplexity Sonar Pro | `perplexity/sonar-pro` | $3 / $15, search included |
| Art director | Grok 4.6 | `x-ai/grok-4.6` | $2 / $6 |
| Doubter | Kimi K3 | `moonshotai/kimi-k3` | $2.40 / $12 |
| Pipe expert | GPT-5.6 Terra Pro **or** an Anthropic model | `openai/gpt-5.6-terra-pro` | — |
Families: OpenAI · DeepSeek · Google · Perplexity · xAI · Moonshot = **six families for
seven seats.** That is the strongest independence any slate here can buy.

## Cost note (Farid has ~$17 OpenRouter credit)
One session ≈ 7 seats × 2 rounds × ~8K in / 2K out ≈ 110K in / 30K out. At this mix that is
roughly **$1.20–$2.00 a session**, dominated by Sonar Pro and Kimi. Eight to twelve sessions
on the current credit. Cheapening move if needed: Researcher on plain `sonar` ($1/$1) and
Engineer on `deepseek-v4-flash` for routine passes.

## Charter changes this forces (add to COUNCIL_SPEC §6)
1. **Doubter (Kimi K3):** "You describe failure modes; you never assert a fact. Every factual
   claim in your report is passed to the Researcher and marked UNVERIFIED until it returns."
2. **QC (Gemini 3.8 Flash):** must receive the actual file — video with audio, or an image at
   ≥512 px on the face. A described artifact is an automatic UNVERIFIED.
3. **No two seats from one family**, ever. If a model is unavailable, the seat moves family
   rather than doubling up.

## Sources (2026-09-11)
[GPT-5.6 Sol](https://openrouter.ai/openai/gpt-5.6-sol) · [DeepSeek V4 Pro](https://openrouter.ai/deepseek/deepseek-v4-pro) · [DeepSeek V4 Flash](https://openrouter.ai/deepseek/deepseek-v4-flash) · [Gemini 3.8 Flash](https://openrouter.ai/google/gemini-3.8-flash) · [Gemini 3.7 Flash](https://openrouter.ai/google/gemini-3.7-flash) · [Sonar Pro](https://openrouter.ai/perplexity/sonar-pro) · [Perplexity API pricing 2026](https://www.cloudzero.com/blog/perplexity-api-pricing/) · [Kimi K3](https://openrouter.ai/moonshotai/kimi-k3) · [Kimi K3 hallucination analysis](https://kili-technology.com/blog/kimi-k3s-benchmarks-and-hallucinations----what-that-tells-us-about-ai-evaluation) · [Grok 4.6](https://openrouter.ai/x-ai/grok-4.6) · [xAI pricing Sep 2026](https://mem0.ai/blog/xai-grok-api-pricing)
