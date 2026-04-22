"""Canonical context signature — v1.0 RC CP7.

The features of the current situation that fix which framework
protocol applies here. Written into every hash-chained protocol
record at synthesis time; queried at future ops by CP9's active-
guidance surface. This module owns the **substrate** (dict shape
+ deterministic build); CP9 owns the **match logic** (which
signature fields to overlap and with what threshold).

## The conservative six-field shape (CP7 plan Q3)

```
{
  "project_name":    "episteme",
  "project_tier":    "python",
  "blueprint":       "fence_reconstruction",
  "op_class":        "fence:constraint-removal",
  "constraint_head": "core/hooks/_grounding.py:32" | null,
  "runtime_marker":  "governed" | "ad_hoc"
}
```

Profile-axis folding (``risk_tolerance``, ``dominant_lens``, etc.)
is intentionally deferred to CP9. Over-specifying here brittles
every prior protocol match against axis tweaks; under-specifying
collapses toward Doxa at match time. At CP7 the signature carries
only features that are structurally stable across axis drift.

## Determinism guarantees

Same inputs → byte-identical dict (after canonical serialization at
the chain envelope). String fields lowercased, whitespace-collapsed,
length-bounded. Tier detection uses the Layer 3 project fingerprint
warm cache so back-to-back calls don't re-walk the tree.

Spec: ``docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`` § Blueprint A ·
Axiomatic Judgment synthesis arm (``context_signature`` field); also
Pillar 3 substrate.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


_HOOKS_DIR = Path(__file__).resolve().parent
if str(_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOKS_DIR))


# ---------------------------------------------------------------------------
# Field normalization helpers
# ---------------------------------------------------------------------------


_CONSTRAINT_HEAD_MAX = 120
_WHITESPACE_RE = re.compile(r"\s+")


def _normalize_string(value: str | None, *, max_len: int | None = None) -> str | None:
    """Lowercase + whitespace-collapse + trim. None stays None."""
    if value is None:
        return None
    collapsed = _WHITESPACE_RE.sub(" ", value.strip().lower())
    if not collapsed:
        return None
    if max_len is not None and len(collapsed) > max_len:
        collapsed = collapsed[:max_len]
    return collapsed


def _detect_project_tier(cwd: Path) -> str:
    """Return one of {python, node, rust, go, java, mixed, unknown}.

    Tier detection uses the Layer 3 fingerprint cache when available
    — tolerant of missing / unreadable project trees. A repo
    carrying signals from 2+ tiers classifies as ``mixed``.
    """
    try:
        from _grounding import (  # type: ignore  # pyright: ignore[reportMissingImports]
            _load_project_fingerprint as _fingerprint,
        )
    except ImportError:
        return "unknown"
    try:
        filenames, _ = _fingerprint(cwd)
    except Exception:
        return "unknown"

    tier_signals: set[str] = set()
    if "pyproject.toml" in filenames or any(n.endswith(".py") for n in list(filenames)[:500]):
        tier_signals.add("python")
    if "package.json" in filenames or "pnpm-lock.yaml" in filenames or "yarn.lock" in filenames:
        tier_signals.add("node")
    if "Cargo.toml" in filenames or "Cargo.lock" in filenames:
        tier_signals.add("rust")
    if "go.mod" in filenames or "go.sum" in filenames:
        tier_signals.add("go")
    if "pom.xml" in filenames or "build.gradle" in filenames or "build.gradle.kts" in filenames:
        tier_signals.add("java")

    if not tier_signals:
        return "unknown"
    if len(tier_signals) == 1:
        return next(iter(tier_signals))
    return "mixed"


def _detect_runtime_marker(cwd: Path) -> str:
    """``"governed"`` when the project ships AGENTS.md OR a ``.claude/``
    directory — signals a kernel-governed environment. ``"ad_hoc"``
    otherwise."""
    try:
        agents = (cwd / "AGENTS.md").is_file()
        claude_dir = (cwd / ".claude").is_dir()
    except OSError:
        return "ad_hoc"
    return "governed" if (agents or claude_dir) else "ad_hoc"


# ---------------------------------------------------------------------------
# ContextSignature dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ContextSignature:
    project_name: str
    project_tier: str
    blueprint: str
    op_class: str
    constraint_head: str | None
    runtime_marker: str

    def as_dict(self) -> dict:
        """Canonical dict for inclusion in hash-chained records.

        The dict is canonicalized by ``_chain.canonical_payload_bytes``
        at write time; this method preserves explicit key order for
        readers that dump records by hand. Key order is
        informational; the chain hash uses sort_keys regardless.
        """
        return {
            "project_name": self.project_name,
            "project_tier": self.project_tier,
            "blueprint": self.blueprint,
            "op_class": self.op_class,
            "constraint_head": self.constraint_head,
            "runtime_marker": self.runtime_marker,
        }


def build(
    cwd: Path,
    blueprint_name: str,
    op_class: str,
    constraint_head: str | None = None,
) -> ContextSignature:
    """Build a deterministic context signature for the current op.

    Parameters
    ----------
    cwd
        Project working directory. Used for project_name (basename)
        and tier/runtime detection.
    blueprint_name
        The blueprint that fired (e.g. ``"fence_reconstruction"``).
        Pass ``"generic"`` when no named blueprint applies.
    op_class
        HIGH_IMPACT_BASH label (e.g. ``"git push"``) OR a blueprint-
        specific class marker (e.g. ``"fence:constraint-removal"``).
    constraint_head
        Fence-specific: the first line of ``constraint_identified``,
        length-bounded. None for non-Fence signatures.

    Returns a ``ContextSignature`` whose ``as_dict`` output is
    suitable as a payload field in any hash-chained record.
    """
    project_name = _normalize_string(cwd.resolve().name) or "unknown_project"
    project_tier = _detect_project_tier(cwd)
    runtime_marker = _detect_runtime_marker(cwd)

    blueprint = _normalize_string(blueprint_name) or "generic"
    op_normalized = _normalize_string(op_class) or "unknown_op"
    head_normalized = _normalize_string(
        constraint_head, max_len=_CONSTRAINT_HEAD_MAX
    )

    return ContextSignature(
        project_name=project_name,
        project_tier=project_tier,
        blueprint=blueprint,
        op_class=op_normalized,
        constraint_head=head_normalized,
        runtime_marker=runtime_marker,
    )


# ---------------------------------------------------------------------------
# Match logic stub — CP9 ships the production tuning
# ---------------------------------------------------------------------------


def field_overlap(
    candidate: ContextSignature, framework_entry: dict
) -> int:
    """Count the number of signature fields that match between the
    candidate (current-op signature) and a framework record's stored
    signature dict. CP9's guidance-query reads this count to rank
    candidates; CP7 exposes it for unit-testable determinism.

    ``None == None`` counts as a match (both signatures lack a
    constraint_head → structurally equivalent).
    """
    stored = framework_entry.get("context_signature")
    if not isinstance(stored, dict):
        return 0
    candidate_dict = candidate.as_dict()
    return sum(
        1 for key, value in candidate_dict.items() if stored.get(key) == value
    )
