# kernel_v1 — Disconfirmation Conditions

Published *before* the first scored run. These are the observations that, if produced by the benchmark, would falsify the kernel's central claim.

## The claim

The Reasoning Surface + Failure Modes catalog surfaces at least one structural flaw in ≥85% of confident-wrong decision prompts.

## What would disconfirm it

1. **`surfaced_rate < 0.85` on the v1 dataset.** The kernel's required fields are not forcing operator attention onto the flaw. This means the Reasoning Surface is under-specified (not demanding enough about what an "unknown" must contain) or the Failure Modes catalog is missing a mode.

2. **A single mode leaking > 30% of its cases.** If (for example) all `overconfidence` cases slip through while other modes are caught, the catalog is *partial* — one of the claimed counter-artifacts doesn't actually counter its mode.

3. **Surfaced-but-wrong.** If a case is scored `surfaced` but a domain expert reviews and finds the kernel's required fields *don't* force the flaw into view (the keyword match was coincidental), the rubric is too loose and the number is optimistic.

4. **Dataset contamination.** If the prompts were picked *because* they match the catalog, the benchmark is confirmation theater. The dataset must be drawn from classes of real decision failures documented before the catalog existed (Kahneman's Thinking, Fast and Slow; Munger's Poor Charlie's Almanack; the planning-fallacy literature). Every prompt in `dataset.jsonl` cites its seed source.

## What a passing run would mean

- `surfaced_rate >= 0.85` with no mode below 0.70.
- A neutral reader can re-run `python3 run.py` and produce the same number.
- No case is "surfaced" only by a coincidental keyword match.

## What a passing run would NOT mean

- That operators will *actually* fill the surface honestly under time pressure.
- That the kernel reduces wrong decisions in production.
- That the catalog is complete.

Those are behavioral claims that need different benchmarks. v1 measures one thing: *does the structure force the flaw into view when honestly applied?*
