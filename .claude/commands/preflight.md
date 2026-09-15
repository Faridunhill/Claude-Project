---
description: Full pre-push check — lint, types, build, and a trust pass on the diff
---

Run every gate before this branch is pushed. Do not stop at the first failure —
collect all of them, fix them, then re-run.

1. `npm run lint`
2. `npm run typecheck`
3. `npm run build`
4. Read `git diff origin/main...HEAD` and check it against the truth rules in
   `CLAUDE.md`: no invented reviews or heritage claims, no service promised that
   is not wired up, currency consistent, no price trusted from the client, no
   secret or key added, no unescaped user input reaching an HTML email.
5. If the diff touches `app/api/checkout/` or `app/api/webhook/`, say so
   explicitly and list what needs manual testing against Stripe test keys.

Report each gate as pass or fail with the actual output. Do not report "done"
while any gate is red.
