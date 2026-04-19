# Handoff — search-api p95 regression

## What shipped

- **Index restored.** `CREATE INDEX CONCURRENTLY idx_documents_tenant_created_v2 ON documents (tenant_id, created_at);` deployed via canary at 2026-04-18 02:48 UTC.
- **Post-deploy p95.** 78ms (baseline 80ms) within 4 minutes. Held through the next 6 hours of traffic.
- **Migration patched.** The orphaned `CREATE INDEX` in the follow-up migration file was merged into the original rename migration and tagged `skip-if-exists` on the rename so a re-run is idempotent.

## What was decided not to ship (and why)

- **Redis cache.** Rejected at the decision-trace gate. The diagnosis showed caching would have masked a schema regression without fixing it.
- **Adding a connection pool alert.** Tempting scope creep — the pool was never the problem in this incident. Queued for backlog with an explicit "not blocking" tag so the next on-call sees it's not load-bearing.

## What's open

1. **Migration linter.** A CI check that refuses migration diffs containing `DROP INDEX` without a matching `CREATE INDEX` in the same file. Spec written, not implemented. Target: next week.
2. **Production query-plan telemetry.** We relied on on-demand EXPLAIN ANALYZE. A sampled, always-on `pg_stat_statements`-based regression detector would have caught the plan change at ~23:31 rather than waiting for the latency SLO to fire at 02:10. Scoped for next sprint.
3. **Test DB row count.** Tests never failed because the test DB has ~0.1% of production scale. Proposal: nightly performance-regression job against a 10% anonymized snapshot. Budget estimate open.

## What the next session needs to know

- Migration file `migrations/20260417_2328_rename_docs_index.sql` was amended — anyone inspecting that commit should also read the updated `CHANGELOG` entry.
- Do **not** try to "re-optimize" the query with a cache based on the pre-fix latency numbers. Those numbers are an artifact of the missing index, not a baseline.
- The on-call Slack thread from 2026-04-18 contains useful context but the "add a cache" proposal in it is explicitly rejected by this investigation — don't restart from that thread without reading `verification.md` first.

## Reasoning-surface artifacts

- Final surface with disconfirmation outcomes: [`reasoning-surface.json`](./reasoning-surface.json)
- Decision trace with load-bearing-concept citations: [`decision-trace.md`](./decision-trace.md)
- Verification with evidence per assumption + per disconfirmation: [`verification.md`](./verification.md)

## Kernel counters that earned their keep this cycle

| Mode caught        | Where                                                                           |
|--------------------|---------------------------------------------------------------------------------|
| question substitution | Refused to promote "add cache" from Slack into an action                       |
| WYSIATI            | Forced "what does EXPLAIN say now vs before" into the unknowns list              |
| anchoring          | Pre-committed pivot conditions prevented clinging to "Postgres is slow under load" |
| overconfidence     | Each hypothesis had a disconfirmation condition before any action                |

## Capture of durable lessons (promote candidates)

None of this incident's specifics (which index, which table) belong in global memory — they're project-scoped and live in the project's `docs/DECISION_STORY.md`. The *pattern* — "debug commands must produce a diagnosis before a treatment ships" — is already captured in `core/memory/global/workflow_policy.md` under "Risk and Autonomy Policy" and does not need a new entry.
