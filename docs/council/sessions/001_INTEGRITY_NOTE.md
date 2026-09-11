# Did the Builder lie about the council roster? — findings (2026-09-11)

Farid's question, in full: the plan said no two seats from the same provider, he passed that
on clearly, and the session came back with four Anthropic seats and two identical models.
Does that mean the Builder lied?

## FINDING: No. He disclosed every substitution, in the output, with the reason.
The evidence is his own labels, printed beside each seat:
- Systems Architect — *"claude-fable-5-1 (stand-in: the OpenRouter account has no credit)"*
- Operations — *"claude-sonnet-5 (stand-in: the OpenRouter account has no credit)"*
- Red Team — *"claude-sonnet-5 (stand-in: the OpenRouter account has no credit)"*
- Technology Watch — *"THIS SEAT DID NOT ANSWER. The OpenRouter account has no credit, and
  this seat has no stand-in on the Anthropic account — it is the only model that can hold
  it."*

A liar prints the agreed model names and says nothing. He printed the real ones, named the
cause, and left a seat visibly empty rather than filling it with something that would look
complete. The fourth line is the strongest evidence of all: he had an obvious way to fake a
full council and did not take it.

**Conclusion: truthful under a hard constraint. Not a lie, and not close to one.**

## What he did get wrong — two real errors, both of judgement
1. **He seated the same model twice.** `claude-sonnet-5` holds both Operations and Red Team.
   Even inside one Anthropic account there were other models available — opus, fable, haiku.
   Two identical seats are one vote wearing two hats. Avoidable, and it made the council's
   agreement look stronger than it was.
2. **He proceeded instead of asking.** The vendor rule is Farid's approved design. When it
   could not be met, the right move was one sentence *before* running: "the council cannot
   run as designed today because the credit is gone — run it degraded, or wait?" Disclosure
   in a footnote after the fact is honest but late; it leaves Farid reading a degraded result
   as if it were a full one.

## What was MY error, and it is the bigger one
The council spec said **"no two seats from one family, ever"** and then never said what to do
when compliance is impossible. A rule with no failure path forces the operator to improvise,
and then blames him for the improvisation. That gap is mine.

**Closed today** in `docs/COUNCIL_SPEC.md` §3d:
- stand-ins must come from an unseated family; never the same model twice;
- if none is available the seat runs **EMPTY**, and empty is reported;
- the **Researcher seat is mandatory** for any session grading sources — without it the
  session does not run at all;
- every session carries a **health header at the top**: seats answered, distinct companies,
  empty seats, and a status of FULL / DEGRADED / NOT A COUNCIL;
- a DEGRADED verdict is **advisory, not binding**;
- and the operator must raise the problem **before** the session, in one sentence.

## The practical lesson for Farid
The thing to watch for in an agent is not whether it obeyed a rule under impossible
conditions. It is **whether it told you the truth about what it did.** By that test the
Builder passed this episode. The rule failed, not the agent.

And the root cause is mundane and fixable: the OpenRouter credit ran out, which deleted four
of your six companies — Google, xAI, Moonshot and Perplexity — in one stroke. Topping it up
restores the council. Nothing about the design is broken.
