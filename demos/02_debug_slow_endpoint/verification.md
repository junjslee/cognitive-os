# Verification — search-api p95 regression

## Against the Core Question

**Core Question.** What caused p95 latency on GET /search to climb from ~80ms to ~1.1s between 2026-04-17 23:40 and 2026-04-18 02:10 UTC?

**Answer produced by the investigation.** The 23:28 migration contained a `DROP INDEX IF EXISTS idx_documents_tenant_created` statement that removed the `(tenant_id, created_at)` composite index. The migration was intended to rename the index, but the `CREATE INDEX` that would have re-created it with a new name was in a *subsequent* migration file that had not yet been applied. Between the two, `/search` fell back to a sequential scan with a filter, producing the observed latency and CPU behavior at 20 RPS.

**Evidence.**
- EXPLAIN ANALYZE before fix: `Seq Scan on documents` with estimated 4.2M rows filtered.
- EXPLAIN ANALYZE after fix: `Index Scan using idx_documents_tenant_created_v2` with estimated 240 rows filtered.
- Migration diff: `git show 2a7f3c1 -- migrations/20260417_2328_rename_docs_index.sql` shows the DROP without a matching CREATE in the same file.

## Against each assumption

| Assumption                                                                 | Result                                                                 |
|----------------------------------------------------------------------------|------------------------------------------------------------------------|
| 20 RPS too low for cache to be the first-order fix                        | Validated — seq scan at that RPS accounts for the CPU and latency.     |
| 23:28 migration is most likely causal touch-point                         | Validated — migration diff contained the DROP.                         |
| Tests passed because test DB row count is ~0.1% of prod                   | Validated — seq scan on 4,000 test rows is <1ms; tests never noticed. |

## Against each disconfirmation condition

| Condition                                                                           | Observed                                                                 | Outcome     |
|-------------------------------------------------------------------------------------|--------------------------------------------------------------------------|-------------|
| If EXPLAIN shows Index Scan on the same index as the old plan, pivot off migration  | EXPLAIN showed Seq Scan, not Index Scan                                  | Not triggered |
| If restoring the index doesn't return p95 to ≤100ms within one deploy cycle, pivot  | p95 returned to 78ms within 4 min of rollout; full return in <1 cycle    | Not triggered |
| If p95 was elevated before 23:30 at finer granularity, migration can't be cause     | Per-minute p95 was flat at 80ms through 23:28; began climbing at 23:31   | Not triggered |

Zero disconfirmation conditions fired. The hypothesis survived every pre-stated falsification test.

## Against the pre-rejected option (A — Redis cache)

Had Option A shipped:
- Cache hits would have masked the symptom.
- Cache misses would still have hit the seq scan (1.1s).
- Any new cold-cache deploy, cache eviction, or cache-invalidation bug would have re-exposed the same regression weeks or months later, with dead Redis infrastructure to maintain in perpetuity.

The rejection of A is itself a kernel-verifiable outcome: A had no disconfirmation condition attached in the Slack thread, which is the kernel's signal to refuse.

## Residual unknowns (honest)

- Why the migration author didn't catch the missing `CREATE INDEX` in review. Likely: the rename was split across two files and the PR diff viewer collapsed the second file. This is a team-process finding, not a service finding; queued for the next retro.
- Whether other recent renames have the same pattern. Queued for `tooling` backlog — a linter that refuses migration diffs with a DROP INDEX without a matching CREATE.

## Confidence

- Root-cause identification: **high** (direct evidence from EXPLAIN + migration diff).
- Reproducibility of the fix: **high** (applied in staging first with a prod-like row count, observed <100ms before production rollout).
- Coverage of the failure class: **medium** (the lint proposal is still a proposal; the same pattern could recur).
