#!/usr/bin/env python3
"""Specificity classifier — moved from src/episteme/_profile_audit.py at v1.0 RC CP1.

Classifies a Reasoning Surface's `disconfirmation` field (and later, under the
v1.0 RC blueprint-polymorphic shape, any blueprint field whose contract
specifies "conditional trigger + specific observable") as one of:

- `fire` — a conditional trigger AND a specific observable are present.
- `absence` — the trigger is phrased as an absence condition (`if nothing
  breaks`, `no issues arise`). Routed away from `fire` because absence is the
  wrong shape for a failure-first operator.
- `tautological` — trigger without observable, or observable without trigger.
- `unknown` — empty / very-short content (< 10 chars). Declines to classify.

Priority: absence > fire > tautological > unknown.

Why this module exists (v1.0 RC CP1 rationale). Phase 12's profile-audit
loop defined the classifier inside `_profile_audit.py` because that was the
only caller at v0.11.0 ship time. The v1.0 RC spec (Pillar 1, Layer 2) makes
the classifier a shared asset: `reasoning_surface_guard.py` will call it in
the hot path against the selected blueprint's required fields (CP3). Moving
it out of the profile-audit module into a sibling hook module is the minimum
refactor that lets CP3 land without importing from `src/episteme/` (which
would violate the hook-self-contained convention).

Behavior is unchanged from the v0.11.0 implementation. Every rule set, every
pattern, and every priority decision is a verbatim move. `_profile_audit.py`
re-exports the names at module scope so existing `pa._classify_disconfirmation`
test access continues to work.

Kernel anchors:
- `kernel/REASONING_SURFACE.md` — the surface-polymorphic contract this
  classifier validates fields against.
- `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` § "Layer 2 · structural
  specificity classifier (blueprint-aware)" — the v1.0 RC contract.
- `docs/DESIGN_V0_11_PHASE_12.md` Axis A S2 — the retrospective audit this
  classifier originally served.
"""
from __future__ import annotations

import re
from typing import Any, Literal


# Classifier rule sets. Compiled once at module load. Absence checked
# FIRST so "if nothing unexpected happens" routes away from fire — the
# whole point of the axis is that absence-conditions are the wrong shape
# for a failure-first operator.
_ABSENCE_PATTERNS: tuple[re.Pattern, ...] = (
    re.compile(r"\bif\s+no(?:body|\s+one|\s+\w+)\s+(?:complain|object|notice|report|flag|raise|push\s+back)", re.I),
    re.compile(r"\bnothing\s+(?:unexpected|fails?|breaks?|changes|goes\s+wrong|surfaces?)", re.I),
    re.compile(r"\bno\s+(?:issues?|errors?|failures?|complaints?|problems?|regressions?)\s+(?:appear|arise|emerge|occur|surface|show\s+up)", re.I),
    re.compile(r"\b(?:everything|all)\s+(?:is|stays|remains|looks)\s+(?:fine|ok|okay|green|normal|healthy)", re.I),
    re.compile(r"\babsence\s+of\b", re.I),
    re.compile(r"\bno\s+one\s+(?:notices|complains|reports|pushes\s+back)", re.I),
    re.compile(r"\bif\s+no\s+alarm", re.I),
)

# Conditional triggers — the "if / when / should / once / after / unless"
# that opens a predicted-outcome clause.
_CONDITIONAL_TRIGGER_PATTERNS: tuple[re.Pattern, ...] = (
    re.compile(r"\bif\b", re.I),
    re.compile(r"\bwhen\b", re.I),
    re.compile(r"\bshould\b", re.I),
    re.compile(r"\bonce\b", re.I),
    re.compile(r"\bafter\b", re.I),
    re.compile(r"\bunless\b", re.I),
)

# Specific observables — numeric thresholds, metric references, failure
# verbs naming something that can be watched for.
_OBSERVABLE_PATTERNS: tuple[re.Pattern, ...] = (
    re.compile(r"\d+\s*%"),
    re.compile(r"\d+\s*(?:ms|sec|seconds?|min|minutes?|h|hours?|MB|GB|KB|rps|qps|errors?)\b", re.I),
    re.compile(r"\b(?:exceeds?|drops?|rises?|passes?|crosses?|hits?|reaches?|exceeds?)\s+\d"),
    re.compile(r"\b(?:fails?|errors?|times?\s*out|crashes?|exits?|panics?|throws?|rejects?|returns?\s+non-?zero|non-?zero\s+exit)\b", re.I),
    re.compile(r"\b(?:log\s+shows?|query[- ]log|telemetry|ci|pipeline|build|test\s+suite|audit\s+log)\b", re.I),
    re.compile(r"\bexit\s*code\b", re.I),
    re.compile(r"\bwithin\s+\d", re.I),
    re.compile(r"\b(?:p50|p90|p95|p99|latency|throughput|error\s+rate|regression)\b", re.I),
    re.compile(r"\b(?:returns?|responds?\s+with|produces?)\s+\S"),
)


DisconfirmationClass = Literal["fire", "absence", "tautological", "unknown"]


def _classify_disconfirmation(text: Any) -> DisconfirmationClass:
    """Syntactic classifier for a Reasoning Surface's `disconfirmation`
    field. Priority: absence > fire > tautological > unknown.

    - `unknown` reserved for empty / very-short content (< 10 chars) —
      we decline to classify rather than guess.
    - `absence` fires first so clauses like "if nothing breaks" do not
      get mis-classified as fire just because they contain 'breaks'.
    - `fire` requires a conditional trigger AND a specific observable —
      either alone is tautological.
    - everything else → `tautological` (pattern-matches the 'restates
      the knowns' case without a false-positive risk).
    """
    if not isinstance(text, str):
        return "unknown"
    stripped = text.strip()
    if len(stripped) < 10:
        return "unknown"

    low = stripped.lower()
    if any(pat.search(low) for pat in _ABSENCE_PATTERNS):
        return "absence"

    has_trigger = any(pat.search(low) for pat in _CONDITIONAL_TRIGGER_PATTERNS)
    has_observable = any(pat.search(low) for pat in _OBSERVABLE_PATTERNS)
    if has_trigger and has_observable:
        return "fire"
    return "tautological"
