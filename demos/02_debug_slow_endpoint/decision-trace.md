# Decision Trace — search-api p95 regression

## Options considered

| # | Option                                                                 | First-order effect              | Second-order effect                                     | Reversibility |
|---|------------------------------------------------------------------------|---------------------------------|----------------------------------------------------------|---------------|
| A | Add Redis cache in front of `/search` results                          | Lower p95 for cache hits        | Masks the real regression; cache-miss latency still 1.1s; future regressions hide behind the cache | Partially reversible (cache code lingers) |
| B | Run EXPLAIN ANALYZE against prod; compare to last-known-good plan      | Produces a diagnosis            | Costs 5 min; no user-facing effect                       | Fully reversible |
| C | Diff the 23:28 migration for index/constraint/statistics changes       | Surfaces or rules out the most likely causal touch-point | Costs 5 min; no user-facing effect | Fully reversible |
| D | Restore suspected-missing index in staging with prod-like row count    | Reproduces the hypothesis safely | Costs 15 min; no user-facing effect                      | Fully reversible |
| E | Restore index in prod directly via canary                              | Fastest potential fix            | If wrong, no harm (index creation is additive); if right, p95 returns immediately | Fully reversible (DROP INDEX) |

## Because-chain

- **Observed signal:** p95 for one endpoint rose, other endpoints flat, CPU up, errors flat, connection count flat.
- **Inferred cause candidates:** (1) index / plan regression, (2) data shape shift, (3) pool saturation, (4) correlated deploy (ruled out: landed after spike).
- **Decision:** run B + C in parallel to produce a diagnosis *before* any treatment. Reject A (the Slack-proposed cache) at the gate — Core Question requires a cause, not a treatment.

## What the kernel forced into view

1. **Core Question** blocked Option A from being tried first. "Add a cache" answered a question nobody had yet asked.
2. **Unknowns** forced "what does the query plan look like NOW vs. before" into the top-5 — which is what actually produced the answer.
3. **Assumptions** named the load-bearing belief that "20 RPS shouldn't saturate a correctly-indexed Postgres" — making it falsifiable rather than silent.
4. **Disconfirmation** pre-committed to the pivot condition ("if restoring the index doesn't fix it within one deploy cycle, pivot") — removing the sunk-cost pull to keep chasing the wrong hypothesis.

## Load-bearing concepts in this decision

| Concept                | Source                                                   | Role here                                         |
|------------------------|----------------------------------------------------------|---------------------------------------------------|
| Question substitution  | Kahneman — *Thinking, Fast and Slow* Ch. 9               | Blocked "add cache" from substituting for diagnosis |
| Inversion              | Munger — *Poor Charlie's Almanack*                       | "What would definitely tell us it's NOT the migration?" → seeded disconfirmation conditions |
| OODA loop              | Boyd — *Patterns of Conflict*                            | Orient (plan diff + migration diff) before Decide  |
| Falsification          | Popper — *Conjectures and Refutations*                   | Every hypothesis in this trace has a pre-stated disconfirmation condition |

All four are cited in `kernel/REFERENCES.md`.

## Chosen path

**B + C in parallel → D → E**, with disconfirmation check gating each step. Rejected A entirely.
