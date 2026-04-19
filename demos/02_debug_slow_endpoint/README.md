# Demo 02 — Debugging a slow API endpoint

The kernel applied to a real engineering decision that isn't self-audit: an endpoint p95 latency spiked from 80ms to 1.1s overnight. A fluent-without-kernel answer ("obviously add a cache") would have been confidently wrong. This demo walks the four canonical artifacts and shows which kernel counter catches which failure mode in the real flow.

## Premise

- Service: `search-api` (FastAPI + Postgres, ~20 RPS baseline).
- Signal: p95 latency for `GET /search?q=…` climbed from ~80ms to ~1.1s between 2026-04-17 23:40 UTC and 2026-04-18 02:10 UTC.
- On-call hypothesis in the Slack thread: *"Postgres is slow under load; let's cache results in Redis."*
- That hypothesis fails the kernel's first check — it substitutes a treatment (`cache`) for a diagnosis (*why is it slow*).

## Artifacts in this directory

| File                                             | What it captures                                                |
|--------------------------------------------------|-----------------------------------------------------------------|
| [`reasoning-surface.json`](./reasoning-surface.json) | Core Question + Knowns / Unknowns / Assumptions / Disconfirmation |
| [`decision-trace.md`](./decision-trace.md)       | Options considered, because-chain, load-bearing concepts         |
| [`verification.md`](./verification.md)           | Check against Core Question, assumption results, disconfirmation |
| [`handoff.md`](./handoff.md)                     | What shipped, what's open, what the next session needs           |

Open them in order. The demo's value is not the fix — it's the sequence of what the kernel *forced the operator to ask* before any edit was made.

## Which failure modes the kernel caught

| Mode            | How it showed up here                                                              | Counter artifact         |
|-----------------|------------------------------------------------------------------------------------|--------------------------|
| substitution    | "Add a cache" substituted for "Why is it slow"                                     | Core Question            |
| WYSIATI         | Only looked at the endpoint code; missed that a new index was dropped in migration | Unknowns                 |
| anchoring       | First framing ("Postgres is slow") stuck even as EXPLAIN output contradicted it    | Disconfirmation          |
| overconfidence  | "Tests pass, cache will fix it" — no pre-stated disconfirmation target             | Disconfirmation          |

## Outcome

Root cause was a dropped composite index (`(tenant_id, created_at)`), removed during an unrelated migration on 2026-04-17 23:30 UTC. Restoring the index returned p95 to 78ms within 4 minutes of rollout. A Redis cache would have shipped in 2 days, improved the symptom temporarily, and left the real bug in place.

The fluent-without-kernel answer was wrong in the direction the kernel is designed to catch.
