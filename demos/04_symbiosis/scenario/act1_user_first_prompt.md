# Act 1 — The underspecified prompt

The user is on-call. PagerDuty has been firing for 20 minutes about p95 latency on `/api/orders` exceeding the SLO. The user opens Claude Code and types:

> *"the /api/orders endpoint is slow under load. add a Redis cache to fix it."*

## What's wrong with this prompt

Nothing — on the surface. It is concrete, actionable, and names a specific remediation. A fluent agent would accept the framing and produce a plausible Redis integration plan within seconds.

## The hidden premise

The prompt conflates *diagnosis* with *fix*. It assumes:

1. The bottleneck is cache-shaped (i.e., the same row is read repeatedly).
2. Redis has lower per-read latency than the underlying datastore *for this query pattern*.
3. The cache invalidation strategy is solvable inside the scope of "fix it."

None of those assumptions are tested. They are inherited from the most common shape of the answer the user has seen before — Stack Overflow threads, Postgres-and-Redis blog posts, the canonical "we 10x'd our throughput with caching" architecture diagrams that pattern-match to "slow endpoint" without examining whether the read pattern is actually cache-amenable.

In this scenario, the actual cause is an N+1 ORM query: each `/api/orders` call triggers one SELECT for the orders table and N more SELECTs for the related items. Caching the response would mask the symptom under low load and amplify the failure under high load — at exactly the moment when the page-fan-out pattern ought to converge.

## Why the agent would accept this without the kernel

LLMs are trained on text where confident, fluent, plausible-shaped answers were rewarded. The training distribution has many "add a cache to fix slow endpoints" examples and very few "stop and ask whether the bottleneck is cache-shaped." A fluent agent answers the question that was asked; it does not refuse the question's premise unless something forces it to.

That something is the kernel.

## What needs to happen next

Before the agent can run any high-impact tool — `git push`, `kubectl apply`, an `ALTER TABLE`, even an ORM-level edit — the file-system hook demands a Reasoning Surface. The Reasoning Surface schema requires the agent to make the cache premise *explicit* and to commit, in advance, to a falsifiable disconfirmation condition.

That is Act 2.
