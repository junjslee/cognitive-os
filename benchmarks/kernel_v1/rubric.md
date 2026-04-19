# kernel_v1 — Scoring Rubric

## What this benchmark tests

**Hypothesis.** The Reasoning Surface (Knowns / Unknowns / Assumptions / Disconfirmation) and the Failure Modes catalog together expose at least one structural flaw in ≥85% of decision prompts that a fluent-without-kernel agent would answer confidently and wrong.

## How scoring works

The dataset is 20 prompts. Each prompt has:

- `id` — stable identifier
- `prompt` — the decision question a user might ask
- `failure_mode` — the Kahneman mode most likely to produce the wrong answer (`wysiati`, `substitution`, `anchoring`, `narrative`, `planning`, `overconfidence`)
- `missing_field` — which Reasoning Surface field would *structurally* catch the flaw (`unknowns`, `assumptions`, `disconfirmation`, `core_question`)
- `hidden_flaw` — a one-line description of what a fluent answer would miss
- `hidden_flaw_keywords` — a list of substrings. If **any** appears in a kernel-produced Reasoning Surface for this prompt, the case is scored `surfaced`.

## The scorer is deterministic and non-semantic

For each prompt, the scorer constructs a *minimum-viable* Reasoning Surface by applying the kernel's own rules: it enumerates what a Reasoning Surface *requires* the operator to declare (a Core Question, at least one unknown, at least one assumption, at least one disconfirmation condition). It then checks whether the template's required fields, when honestly filled for this prompt, must contain any `hidden_flaw_keywords`.

This is a structural check, not a semantic one:
- If the hidden flaw concerns concurrency behavior, the `unknowns` field cannot honestly omit "concurrent-write behavior" without the operator noticing — the field is required to be non-empty and specific.
- The scorer verifies this by pattern-matching the *required field labels* against the flaw keywords.

The rubric is intentionally conservative: it counts a case as surfaced only if the *required structure itself* forces the flaw into view, not if a very thorough operator *might* catch it.

## Pass threshold

- `surfaced_rate >= 0.85` → hypothesis supported for this cut of the dataset.
- `surfaced_rate <  0.85` → hypothesis weakened; investigate which modes leak.

## Disconfirmation conditions (the Popperian gate)

See [`disconfirmation.md`](./disconfirmation.md). These are the exact observations that would falsify the kernel's claim. They are published *before* the run, not reverse-engineered after.

## Known limits of this benchmark (honest)

- 20 prompts is small. Future revisions should scale to ≥100 across harness types.
- The scorer measures whether the kernel's *structure* surfaces flaws, not whether a human operator *will* fill the structure honestly. The latter is a behavioral question outside this benchmark's scope.
- No held-out comparison against a no-kernel baseline yet. v2 should run the same prompts through a baseline prompt template and compare flaw-surfacing rates.

These are listed here so a reader doesn't need to discover them.
