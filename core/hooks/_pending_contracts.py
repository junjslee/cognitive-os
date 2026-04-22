"""Layer 6 pending-contracts stream — v1.0 RC CP7.

When a Reasoning Surface's ``verification_trace`` carries
``window_seconds``, the guard writes a *pending contract* to
``~/.episteme/state/pending_contracts.jsonl``. Phase 12's audit
(running at SessionStart) correlates each expired contract against
``~/.episteme/telemetry/*-audit.jsonl`` — did the named command /
test / dashboard actually fire within the declared window? — and
tags ``disconfirmation_unverified`` in the episodic tier when it
didn't. The hash chain makes retroactive "I did run it" edits
detectable.

CP7 scope: the **write** path + the **expiry-detection** path. The
audit correlation itself (read telemetry, match trace.command,
emit verdict) is Phase 12 / v1.0.1 scope — CP7 lands the queue, not
the verifier.

## Record shape

```json
{
  "type":              "pending_contract",
  "correlation_id":    "<tool_use_id or SHA-1 fallback>",
  "created_at":        "...",
  "expires_at":        "...",
  "op_label":          "git push",
  "blueprint":         "generic",
  "context_signature": {<ContextSignature.as_dict()>},
  "verification_trace": {
    "command": "...", "or_dashboard": "...", "or_test": "...",
    "window_seconds": 600, "threshold_observable": "..."
  },
  "surface_provenance": {
    "core_question": "...",
    "disconfirmation": "..."
  }
}
```

## TTL cap

Contracts strictly older than ``max(declared window)`` + 72h grace
are auto-archived to ``pending_contracts.archived.jsonl`` with
``status: "expired_without_audit"``. Prevents unbounded growth when
Phase 12 fails to run for an extended period.

## Separation from Fence pending marker

CP5 ships a **per-correlation-id JSON file** at
``~/.episteme/state/fence_pending/<id>.json`` for the
PreToolUse → PostToolUse synthesis handoff. That mechanism is
unchanged. The Fence marker is ephemeral — deleted at PostToolUse.

CP7's pending_contracts.jsonl is a **hash-chained append-only
queue** for Layer 6 audit. Different shape, different lifetime,
different consumer.

Spec: ``docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`` § Layer 6 ·
time-bound disconfirmation contract.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

_HOOKS_DIR = Path(__file__).resolve().parent
if str(_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOKS_DIR))

from _chain import (  # noqa: E402  # pyright: ignore[reportMissingImports]
    ChainError,
    ChainVerdict,
    append as _chain_append,
    iter_records as _chain_iter,
    verify_chain as _chain_verify,
    atomic_replace_file as _atomic_replace,
)


PENDING_CONTRACT_TYPE = "pending_contract"
ARCHIVED_CONTRACT_TYPE = "pending_contract_archived"

# Hard grace past the declared window before auto-archiving.
_GRACE_SECONDS = 72 * 60 * 60


def _episteme_home() -> Path:
    return Path(os.environ.get("EPISTEME_HOME") or (Path.home() / ".episteme"))


def _contracts_path() -> Path:
    return _episteme_home() / "state" / "pending_contracts.jsonl"


def _archived_path() -> Path:
    return _episteme_home() / "state" / "pending_contracts.archived.jsonl"


# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ContractWriteResult:
    correlation_id: str
    expires_at: str
    entry_hash: str


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def write_contract(
    *,
    correlation_id: str,
    op_label: str,
    blueprint: str,
    context_signature: dict,
    verification_trace: dict,
    surface_provenance: dict,
    path: Path | None = None,
    now: datetime | None = None,
) -> ContractWriteResult:
    """Append a pending-contract record. Raises ``ChainError`` on
    correlation-id collision (second write with a different payload
    for the same id) — the kernel refuses silent overwrites.

    ``verification_trace`` must carry ``window_seconds`` as a
    positive int; that is the contract's raison d'être. Traces
    without a window are NOT contracts (they're still valid at
    Layer 4; they just don't need async audit).
    """
    target = path if path is not None else _contracts_path()
    if not isinstance(correlation_id, str) or not correlation_id.strip():
        raise ChainError("correlation_id must be a non-empty string")
    window = verification_trace.get("window_seconds") if isinstance(verification_trace, dict) else None
    if not isinstance(window, int) or isinstance(window, bool) or window <= 0:
        raise ChainError(
            f"verification_trace.window_seconds required (positive int); got {window!r}"
        )

    now_dt = now or datetime.now(timezone.utc)
    created = _iso(now_dt)
    expires = _iso(now_dt + timedelta(seconds=window))

    # Collision check — if a prior record exists with the same
    # correlation_id and a DIFFERENT payload hash, refuse. Same
    # correlation_id with identical payload is a no-op (idempotent
    # re-write; can happen on hook retries).
    new_payload_core = {
        "op_label": op_label,
        "blueprint": blueprint,
        "context_signature": context_signature,
        "verification_trace": verification_trace,
        "surface_provenance": surface_provenance,
    }
    for rec in _chain_iter(target, verify=False):
        payload = rec.get("payload") if isinstance(rec, dict) else None
        if not isinstance(payload, dict):
            continue
        if payload.get("type") != PENDING_CONTRACT_TYPE:
            continue
        if payload.get("correlation_id") != correlation_id:
            continue
        # Same id; check payload equivalence.
        existing_core = {
            k: payload.get(k) for k in new_payload_core.keys()
        }
        if existing_core != new_payload_core:
            raise ChainError(
                f"correlation_id {correlation_id!r} already has a "
                f"different pending contract (refusing silent overwrite)"
            )
        # Idempotent re-write — return the existing record's hash.
        return ContractWriteResult(
            correlation_id=correlation_id,
            expires_at=str(payload.get("expires_at")),
            entry_hash=str(rec.get("entry_hash", "")),
        )

    payload = {
        "type": PENDING_CONTRACT_TYPE,
        "correlation_id": correlation_id,
        "created_at": created,
        "expires_at": expires,
        **new_payload_core,
    }
    envelope = _chain_append(target, payload)
    return ContractWriteResult(
        correlation_id=correlation_id,
        expires_at=expires,
        entry_hash=envelope["entry_hash"],
    )


# ---------------------------------------------------------------------------
# Read / expiry
# ---------------------------------------------------------------------------


def list_active(path: Path | None = None) -> list[dict]:
    """Return all pending contracts currently in the active file
    (not archived). Chain-verified — stops at first break. Entries
    are the full envelopes (caller accesses ``rec["payload"]`` for
    business fields)."""
    target = path if path is not None else _contracts_path()
    return [
        rec for rec in _chain_iter(target, verify=True)
        if isinstance(rec, dict)
        and isinstance(rec.get("payload"), dict)
        and rec["payload"].get("type") == PENDING_CONTRACT_TYPE
    ]


def sweep_expired(
    now: datetime | None = None,
    path: Path | None = None,
) -> list[dict]:
    """Return contracts whose ``expires_at`` is at or before ``now``.
    Does NOT delete — Phase 12 reads these, correlates against
    telemetry, emits ``disconfirmation_unverified`` tags, then calls
    ``archive_processed`` to move them off the active queue.
    """
    now_dt = now or datetime.now(timezone.utc)
    expired: list[dict] = []
    for rec in list_active(path=path):
        payload = rec["payload"]
        try:
            expires = datetime.fromisoformat(str(payload.get("expires_at", "")))
        except ValueError:
            continue
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires <= now_dt:
            expired.append(rec)
    return expired


def archive_processed(
    processed_correlation_ids: set[str],
    audit_verdicts: dict[str, str] | None = None,
    *,
    active_path: Path | None = None,
    archive_path: Path | None = None,
    now: datetime | None = None,
) -> int:
    """Archive the named contracts. Returns the number archived.

    Archive format: append a ``pending_contract_archived`` record
    (hash-chained) to ``archive_path``, then rewrite the active file
    with those correlation_ids removed. ``audit_verdicts`` maps
    correlation_id → verdict string (e.g. ``"verified"``,
    ``"unverified"``, ``"expired_without_audit"``).

    This does mean the active file gets rebuilt — so the active
    chain breaks by design each time. That's acceptable because the
    archive preserves the audit trail in its own durable chain.
    We write a ``chain_rotation`` genesis record as the new active
    head after rebuild, linking to the previous head for forensics.
    """
    active = active_path if active_path is not None else _contracts_path()
    archive = archive_path if archive_path is not None else _archived_path()
    audit_verdicts = audit_verdicts or {}

    active_records = list(_chain_iter(active, verify=False))
    kept_records = [
        rec for rec in active_records
        if isinstance(rec, dict)
        and isinstance(rec.get("payload"), dict)
        and rec["payload"].get("type") == PENDING_CONTRACT_TYPE
        and rec["payload"].get("correlation_id") not in processed_correlation_ids
    ]
    removed = [
        rec for rec in active_records
        if isinstance(rec, dict)
        and isinstance(rec.get("payload"), dict)
        and rec["payload"].get("type") == PENDING_CONTRACT_TYPE
        and rec["payload"].get("correlation_id") in processed_correlation_ids
    ]

    # Append archive records (chained on the archive file).
    archived_count = 0
    for rec in removed:
        payload = rec["payload"]
        cid = payload.get("correlation_id", "")
        verdict = audit_verdicts.get(cid, "archived")
        archive_payload = {
            "type": ARCHIVED_CONTRACT_TYPE,
            "correlation_id": cid,
            "archived_at": _iso(now or datetime.now(timezone.utc)),
            "verdict": verdict,
            "original_record": payload,
        }
        _chain_append(archive, archive_payload)
        archived_count += 1

    # Rewrite active file. A chain rotation: new genesis linking to
    # the previous head via a ``chain_rotation`` record. Walkers that
    # see this know the file continues an older chain that lives in
    # the archive.
    if removed:
        prev_head_verdict = _chain_verify(active)
        previous_head = prev_head_verdict.head_hash
        _atomic_replace(active, b"")
        rotation_payload = {
            "type": "chain_rotation",
            "reason": "archive_processed: moved expired/audited contracts",
            "previous_head": previous_head,
            "archived_count": archived_count,
            "rotation_ts": _iso(now or datetime.now(timezone.utc)),
        }
        _chain_append(active, rotation_payload)
        for rec in kept_records:
            # Re-append each kept record's payload (not envelope) so
            # the new chain re-computes entry_hashes from the
            # rotation genesis. The original entry_hash is superseded
            # by design; the archive holds the pre-rotation copy.
            payload = rec["payload"]
            ts = rec.get("ts")
            if isinstance(ts, str):
                _chain_append(active, payload, ts=ts)
            else:
                _chain_append(active, payload)

    return archived_count


def auto_archive_beyond_grace(
    now: datetime | None = None,
    *,
    active_path: Path | None = None,
    archive_path: Path | None = None,
) -> int:
    """Safety net: any contract whose ``expires_at`` is more than
    ``_GRACE_SECONDS`` in the past auto-archives with
    verdict ``expired_without_audit``. Prevents unbounded growth
    when Phase 12 fails to run for an extended period."""
    now_dt = now or datetime.now(timezone.utc)
    cutoff = now_dt - timedelta(seconds=_GRACE_SECONDS)
    beyond: set[str] = set()
    for rec in list_active(path=active_path):
        payload = rec["payload"]
        try:
            expires = datetime.fromisoformat(str(payload.get("expires_at", "")))
        except ValueError:
            continue
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires < cutoff:
            cid = payload.get("correlation_id")
            if isinstance(cid, str):
                beyond.add(cid)
    if not beyond:
        return 0
    return archive_processed(
        beyond,
        audit_verdicts={cid: "expired_without_audit" for cid in beyond},
        active_path=active_path,
        archive_path=archive_path,
        now=now_dt,
    )


# ---------------------------------------------------------------------------
# Chain verification (thin wrapper for Phase 12 precondition)
# ---------------------------------------------------------------------------


def verify_chain(path: Path | None = None) -> ChainVerdict:
    """Phase 12 calls this at SessionStart. Returns the verdict for
    the active contracts chain; the archive chain is checked
    separately via ``verify_archive``."""
    target = path if path is not None else _contracts_path()
    return _chain_verify(target)


def verify_archive(path: Path | None = None) -> ChainVerdict:
    target = path if path is not None else _archived_path()
    return _chain_verify(target)
