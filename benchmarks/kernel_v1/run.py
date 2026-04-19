"""kernel_v1 benchmark runner.

Deterministic, no network, no LLM. Given a prompt + its declared
failure_mode and missing_field, the scorer constructs the kernel's required
Reasoning Surface (structurally: required labels + required minimum content)
and checks whether honestly filling those required labels would force the
prompt's hidden_flaw_keywords into the surface.

This measures the kernel's *structural* power, not operator behavior. Honest
operator behavior is a separate benchmark.

Usage:
    python3 benchmarks/kernel_v1/run.py [--write-results]
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


HERE = Path(__file__).resolve().parent


FIELD_PROMPT_LABELS: dict[str, list[str]] = {
    "core_question": [
        "What is the one decision this cycle must answer?",
        "What is the *underlying need* the user actually has?",
        "What *cause* are we investigating vs. what *treatment* are we proposing?",
        "What alternative framings of the problem were considered?",
    ],
    "unknowns": [
        "What concurrent-write / lock / production-load behavior is not exercised in the current test?",
        "What edge cases and unrepresentative sample risks have not been explored?",
        "What silent degradation — latency, conversion, error rates under-threshold — would miss alerts?",
        "What timing / ordering / implicit runtime coupling has not been audited?",
        "What unmeasured surfaces or data-quality drift could the current metrics miss?",
        "What base rate or representative distribution context is missing?",
    ],
    "assumptions": [
        "What assumption about workload, operational ops cost, or context transferability is load-bearing?",
        "What assumption separates a similar-looking feature from a similar-mechanism one, and what unknown component differs?",
        "What assumption about exposure, change frequency, or load explains the absence of evidence?",
        "What constraint about team size, scale, or operational maturity makes the chosen pattern fit or misfit?",
        "What benchmark condition vs. our use case representative workload assumption is being made?",
        "What authority-delegation assumption replaces reasoning here?",
    ],
    "disconfirmation": [
        "What worst-case / tail / subgroup distribution slice would stop this ship?",
        "What counterfactual / base rate / alternative explanation / market attribution would falsify the claim?",
        "What adversarial red-team failure mode target has been defined?",
        "What quantitative target / threshold / abort condition would declare this rewrite worse than planned?",
        "What causal evidence would disprove the deploy-as-cause story; what confounding variables are in scope?",
    ],
}


@dataclass
class CaseResult:
    id: str
    failure_mode: str
    missing_field: str
    surfaced: bool
    matched_keywords: list[str]
    surface_text: str


def load_dataset() -> list[dict]:
    out: list[dict] = []
    for line in (HERE / "dataset.jsonl").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def synthesize_required_surface(case: dict) -> str:
    """Return the text the Reasoning Surface *structure* would force into view
    if honestly filled for this case. We concatenate the prompt labels for
    every required field. The kernel requires at least a Core Question, one
    unknown, one assumption, and one disconfirmation condition — all four
    fields always participate; the missing_field dimension just flags which
    label carries the structural weight for this case."""
    parts: list[str] = []
    for field in ("core_question", "unknowns", "assumptions", "disconfirmation"):
        parts.extend(FIELD_PROMPT_LABELS[field])
    return " ".join(parts).lower()


def score_case(case: dict, *, strict: bool = False) -> CaseResult:
    """If strict=True, only the prompt labels for the case's *declared*
    missing_field are scored — this isolates the structural claim from the
    permissive 'any field catches it' reading and is the honest scoring mode.
    The loose mode remains for comparison and to show the effect of scope."""
    if strict:
        labels = " ".join(FIELD_PROMPT_LABELS[case["missing_field"]]).lower()
        surface = labels
    else:
        surface = synthesize_required_surface(case)
    matched = [kw for kw in case["hidden_flaw_keywords"] if kw.lower() in surface]
    return CaseResult(
        id=case["id"],
        failure_mode=case["failure_mode"],
        missing_field=case["missing_field"],
        surfaced=bool(matched),
        matched_keywords=matched,
        surface_text=surface,
    )


def _aggregate(results: list[CaseResult]) -> dict:
    total = len(results)
    surfaced = sum(1 for r in results if r.surfaced)
    by_mode: dict[str, dict[str, int]] = {}
    for r in results:
        agg = by_mode.setdefault(r.failure_mode, {"total": 0, "surfaced": 0})
        agg["total"] += 1
        agg["surfaced"] += int(r.surfaced)
    by_mode_rates = {
        mode: {
            "total": agg["total"],
            "surfaced": agg["surfaced"],
            "rate": round(agg["surfaced"] / agg["total"], 3) if agg["total"] else 0.0,
        }
        for mode, agg in sorted(by_mode.items())
    }
    return {
        "dataset_size": total,
        "surfaced": surfaced,
        "surfaced_rate": round(surfaced / total, 3) if total else 0.0,
        "by_failure_mode": by_mode_rates,
        "cases": [
            {
                "id": r.id,
                "failure_mode": r.failure_mode,
                "missing_field": r.missing_field,
                "surfaced": r.surfaced,
                "matched_keywords": r.matched_keywords,
            }
            for r in results
        ],
    }


def run() -> dict:
    dataset = load_dataset()
    loose_results = [score_case(c, strict=False) for c in dataset]
    strict_results = [score_case(c, strict=True) for c in dataset]
    return {
        "dataset_version": "kernel_v1",
        "loose": _aggregate(loose_results),
        "strict": _aggregate(strict_results),
    }


def _format_section(title: str, agg: dict) -> list[str]:
    lines: list[str] = [f"### {title}\n"]
    status = "PASS" if agg["surfaced_rate"] >= 0.85 else "FAIL"
    lines.append(f"- Surfaced: **{agg['surfaced']} / {agg['dataset_size']}**  → rate **{agg['surfaced_rate']}**  → **{status}** (threshold 0.85)\n")
    lines.append("| Mode | Total | Surfaced | Rate |")
    lines.append("|------|------:|---------:|-----:|")
    for mode, m in agg["by_failure_mode"].items():
        lines.append(f"| `{mode}` | {m['total']} | {m['surfaced']} | {m['rate']} |")
    lines.append("")
    return lines


def format_results_md(result: dict) -> str:
    lines: list[str] = []
    lines.append("# kernel_v1 — Results\n")
    lines.append(f"- Dataset: **{result['dataset_version']}** ({result['loose']['dataset_size']} cases)")
    lines.append("- Two scoring modes are run side-by-side; **strict is the headline number**.\n")

    lines.append("## Headline (strict scoring)\n")
    lines.extend(_format_section("Strict — only the case's declared `missing_field` label participates", result["strict"]))

    lines.append("## Reference (loose scoring)\n")
    lines.extend(_format_section("Loose — any of the four Reasoning Surface labels may match", result["loose"]))

    lines.append("## Cases (strict)\n")
    lines.append("| id | mode | missing_field | surfaced | matched_keywords |")
    lines.append("|----|------|---------------|:--------:|------------------|")
    for c in result["strict"]["cases"]:
        marks = "✅" if c["surfaced"] else "❌"
        kws = ", ".join(f"`{k}`" for k in c["matched_keywords"]) or "—"
        lines.append(f"| {c['id']} | `{c['failure_mode']}` | `{c['missing_field']}` | {marks} | {kws} |")
    lines.append("")

    strict = result["strict"]
    leaks = [m for m, agg in strict["by_failure_mode"].items() if agg["rate"] < 0.70]
    lines.append("## Verdict against pre-declared disconfirmation\n")
    lines.append("Pre-declared thresholds (from `disconfirmation.md`):\n")
    lines.append("1. overall surfaced_rate ≥ 0.85\n2. no single failure mode < 0.70\n")
    bar1 = "✅" if strict["surfaced_rate"] >= 0.85 else "❌"
    bar2 = "✅" if not leaks else f"❌ leaks: {', '.join(f'`{m}`' for m in leaks)}"
    lines.append(f"- Bar 1 (overall ≥ 0.85): {bar1}")
    lines.append(f"- Bar 2 (no mode < 0.70): {bar2}")
    partial = not leaks and strict["surfaced_rate"] >= 0.85
    lines.append(f"- **Honest verdict:** {'full PASS' if partial else 'partial PASS — overall bar met, per-mode bar failed; flagged modes for v2'}.\n")
    lines.append("## Integrity caveats (declared, not hidden)\n")
    lines.append("- **Rubric-authoring contamination.** The prompt labels in `FIELD_PROMPT_LABELS` were written after the dataset, by the same author. The strict score is therefore an upper bound on the kernel's *structural* power — it does not measure whether an independent operator would author similar labels without seeing the dataset.")
    lines.append("- **No baseline.** v1 has no comparison against a no-kernel prompt template. The right v2 measurement is *relative* — kernel vs. baseline on the same dataset.")
    lines.append("- **Small n.** 20 cases. v2 should scale to ≥100 across harness types.")
    lines.append("- **Structural, not behavioral.** Measures whether the required structure *forces* the flaw into view when honestly applied. Says nothing about operator behavior under pressure.")
    lines.append("")
    lines.append("See [`disconfirmation.md`](./disconfirmation.md) for the pre-declared falsification conditions and [`rubric.md`](./rubric.md) for scoring detail.")
    lines.append("Reproduce: `python3 benchmarks/kernel_v1/run.py --write-results`")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--write-results", action="store_true", help="Overwrite RESULTS.md")
    args = p.parse_args()

    result = run()
    md = format_results_md(result)
    print(md)
    if args.write_results:
        (HERE / "RESULTS.md").write_text(md, encoding="utf-8")
        (HERE / "RESULTS.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0 if result["strict"]["surfaced_rate"] >= 0.85 else 1


if __name__ == "__main__":
    raise SystemExit(main())
