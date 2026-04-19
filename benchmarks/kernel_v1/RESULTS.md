# kernel_v1 — Results

- Dataset: **kernel_v1** (20 cases)
- Two scoring modes are run side-by-side; **strict is the headline number**.

## Headline (strict scoring)

### Strict — only the case's declared `missing_field` label participates

- Surfaced: **18 / 20**  → rate **0.9**  → **PASS** (threshold 0.85)

| Mode | Total | Surfaced | Rate |
|------|------:|---------:|-----:|
| `anchoring` | 3 | 2 | 0.667 |
| `narrative` | 3 | 3 | 1.0 |
| `overconfidence` | 4 | 4 | 1.0 |
| `planning` | 2 | 2 | 1.0 |
| `substitution` | 3 | 2 | 0.667 |
| `wysiati` | 5 | 5 | 1.0 |

## Reference (loose scoring)

### Loose — any of the four Reasoning Surface labels may match

- Surfaced: **20 / 20**  → rate **1.0**  → **PASS** (threshold 0.85)

| Mode | Total | Surfaced | Rate |
|------|------:|---------:|-----:|
| `anchoring` | 3 | 3 | 1.0 |
| `narrative` | 3 | 3 | 1.0 |
| `overconfidence` | 4 | 4 | 1.0 |
| `planning` | 2 | 2 | 1.0 |
| `substitution` | 3 | 3 | 1.0 |
| `wysiati` | 5 | 5 | 1.0 |

## Cases (strict)

| id | mode | missing_field | surfaced | matched_keywords |
|----|------|---------------|:--------:|------------------|
| b01 | `substitution` | `core_question` | ✅ | `cause` |
| b02 | `wysiati` | `unknowns` | ✅ | `concurrent`, `lock` |
| b03 | `overconfidence` | `disconfirmation` | ✅ | `distribution`, `slice`, `worst-case`, `tail`, `subgroup` |
| b04 | `planning` | `assumptions` | ✅ | `assumption`, `similar`, `differ`, `unknown component` |
| b05 | `narrative` | `disconfirmation` | ✅ | `causal`, `evidence`, `disprove`, `confounding` |
| b06 | `wysiati` | `unknowns` | ✅ | `edge case`, `representative`, `sample` |
| b07 | `overconfidence` | `assumptions` | ✅ | `assumption`, `workload`, `operational`, `ops cost`, `authority` |
| b08 | `anchoring` | `core_question` | ❌ | — |
| b09 | `substitution` | `core_question` | ✅ | `decision`, `underlying need` |
| b10 | `wysiati` | `unknowns` | ✅ | `silent`, `degradation`, `conversion`, `metric` |
| b11 | `narrative` | `disconfirmation` | ✅ | `counterfactual`, `attribution`, `base rate`, `alternative explanation`, `market` |
| b12 | `overconfidence` | `unknowns` | ✅ | `timing`, `ordering`, `implicit`, `runtime` |
| b13 | `anchoring` | `assumptions` | ✅ | `workload`, `representative`, `our use case`, `assumption` |
| b14 | `planning` | `disconfirmation` | ✅ | `target`, `threshold`, `abort` |
| b15 | `wysiati` | `unknowns` | ✅ | `base rate`, `representative`, `distribution` |
| b16 | `substitution` | `core_question` | ❌ | — |
| b17 | `narrative` | `assumptions` | ✅ | `assumption`, `exposure`, `load`, `change frequency` |
| b18 | `wysiati` | `disconfirmation` | ✅ | `adversarial`, `failure mode`, `worst-case` |
| b19 | `anchoring` | `assumptions` | ✅ | `context`, `constraint`, `team size`, `scale`, `operational` |
| b20 | `overconfidence` | `unknowns` | ✅ | `unmeasured`, `drift` |

## Verdict against pre-declared disconfirmation

Pre-declared thresholds (from `disconfirmation.md`):

1. overall surfaced_rate ≥ 0.85
2. no single failure mode < 0.70

- Bar 1 (overall ≥ 0.85): ✅
- Bar 2 (no mode < 0.70): ❌ leaks: `anchoring`, `substitution`
- **Honest verdict:** partial PASS — overall bar met, per-mode bar failed; flagged modes for v2.

## Integrity caveats (declared, not hidden)

- **Rubric-authoring contamination.** The prompt labels in `FIELD_PROMPT_LABELS` were written after the dataset, by the same author. The strict score is therefore an upper bound on the kernel's *structural* power — it does not measure whether an independent operator would author similar labels without seeing the dataset.
- **No baseline.** v1 has no comparison against a no-kernel prompt template. The right v2 measurement is *relative* — kernel vs. baseline on the same dataset.
- **Small n.** 20 cases. v2 should scale to ≥100 across harness types.
- **Structural, not behavioral.** Measures whether the required structure *forces* the flaw into view when honestly applied. Says nothing about operator behavior under pressure.

See [`disconfirmation.md`](./disconfirmation.md) for the pre-declared falsification conditions and [`rubric.md`](./rubric.md) for scoring detail.
Reproduce: `python3 benchmarks/kernel_v1/run.py --write-results`
