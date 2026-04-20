"""Tests for phase 11 — semantic-tier promotion job.

Kernel reference: kernel/MEMORY_ARCHITECTURE.md (promotion contract).

Invariants under test:
1. Promotion never writes to the semantic tier; proposals land only in
   the reflective tier.
2. Re-running on the same episodic records produces the same proposals
   (deterministic ids, deterministic ordering).
3. Clusters below the minimum size are silently dropped.
4. Clusters with no observed exit codes are silently dropped (no
   calibration signal).
5. Empty / missing episodic dir returns an empty report, not a crash.
6. The CLI never blocks — malformed lines in episodic files are skipped.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from episteme import _memory_promote as mp


def _rec(
    *,
    rec_id: str,
    pattern: str = "git push",
    domain: str = "Complicated",
    exit_code: int | None = 0,
    with_surface: bool = True,
) -> dict:
    details: dict = {
        "tool": "Bash",
        "command": f"{pattern} origin master",
        "cwd": "/tmp/test",
        "exit_code": exit_code,
        "status": "success" if exit_code == 0 else "error",
        "high_impact_patterns_matched": [pattern],
    }
    if with_surface:
        details["reasoning_surface"] = {
            "core_question": "Will migration hold?",
            "unknowns": ["does caller hold a lock on the target?"],
            "assumptions": ["green tests locally"],
            "disconfirmation": "pipeline fails within 3m of push",
            "domain": domain,
            "tacit_call": False,
            "timestamp": "2026-04-20T12:00:00Z",
        }
    return {
        "id": rec_id,
        "memory_class": "episodic",
        "summary": f"bash: {pattern}",
        "details": details,
        "provenance": {
            "source_type": "agent",
            "source_ref": "core/hooks/episodic_writer.py",
            "captured_at": "2026-04-20T12:00:00Z",
            "captured_by": "episodic_writer",
            "confidence": "high",
            "evidence_refs": [],
        },
        "status": "active",
        "version": "memory-contract-v1",
        "tags": ["high-impact", "bash", pattern],
        "session_id": "sess-test",
        "event_type": "action",
    }


def _write_episodic(tmp: Path, records: list[dict]) -> Path:
    episodic = tmp / "episodic"
    episodic.mkdir(parents=True)
    path = episodic / "2026-04-20.jsonl"
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    return episodic


class LoadAndClusterTests(unittest.TestCase):

    def test_missing_dir_returns_empty(self):
        with tempfile.TemporaryDirectory() as td:
            records = mp.load_episodic_records(Path(td) / "nope")
            self.assertEqual(records, [])

    def test_malformed_lines_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            ep_dir = Path(td) / "episodic"
            ep_dir.mkdir()
            path = ep_dir / "2026-04-20.jsonl"
            path.write_text(
                "{ not json\n"
                + json.dumps(_rec(rec_id="r1")) + "\n"
                + "\n"
                + json.dumps({"memory_class": "project", "id": "wrong"}) + "\n"
            )
            records = mp.load_episodic_records(ep_dir)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["id"], "r1")

    def test_signature_requires_pattern(self):
        r = _rec(rec_id="r1")
        del r["details"]["high_impact_patterns_matched"]
        self.assertIsNone(mp.signature_of(r))

    def test_signature_domain_defaults_to_unknown(self):
        r = _rec(rec_id="r1")
        r["details"].pop("reasoning_surface")
        sig = mp.signature_of(r)
        self.assertIsNotNone(sig)
        self.assertEqual(sig.domain, "Unknown")
        self.assertEqual(sig.action_pattern, "git push")

    def test_cluster_groups_by_signature(self):
        records = [
            _rec(rec_id=f"p{i}", pattern="git push") for i in range(3)
        ] + [
            _rec(rec_id=f"n{i}", pattern="npm publish") for i in range(2)
        ]
        groups = mp.cluster_records(records)
        self.assertEqual(len(groups), 2)
        sizes = sorted(len(v) for v in groups.values())
        self.assertEqual(sizes, [2, 3])


class ProposalShapeTests(unittest.TestCase):

    def test_typical_success_labeled_typically_succeeds(self):
        records = [_rec(rec_id=f"r{i}", exit_code=0) for i in range(4)]
        proposals = mp.build_proposals(records, min_cluster_size=3)
        self.assertEqual(len(proposals), 1)
        p = proposals[0]
        self.assertEqual(p["stability"], "typically-succeeds")
        self.assertEqual(p["success_rate"], 1.0)
        self.assertEqual(p["sample_size"], 4)

    def test_typical_failure_labeled_typically_fails(self):
        records = [_rec(rec_id=f"r{i}", exit_code=1) for i in range(4)]
        proposals = mp.build_proposals(records, min_cluster_size=3)
        self.assertEqual(proposals[0]["stability"], "typically-fails")

    def test_mixed_outcome_labeled_mixed(self):
        records = [_rec(rec_id="a", exit_code=0),
                   _rec(rec_id="b", exit_code=1),
                   _rec(rec_id="c", exit_code=0)]
        proposals = mp.build_proposals(records, min_cluster_size=3)
        self.assertEqual(proposals[0]["stability"], "mixed")

    def test_below_min_cluster_dropped(self):
        records = [_rec(rec_id=f"r{i}") for i in range(2)]
        proposals = mp.build_proposals(records, min_cluster_size=3)
        self.assertEqual(proposals, [])

    def test_cluster_with_no_observed_exits_dropped(self):
        records = [_rec(rec_id=f"r{i}", exit_code=None) for i in range(3)]
        proposals = mp.build_proposals(records, min_cluster_size=3)
        self.assertEqual(proposals, [])

    def test_proposal_shape_conforms_to_contract(self):
        records = [_rec(rec_id=f"r{i}", exit_code=0) for i in range(3)]
        proposal = mp.build_proposals(records, min_cluster_size=3)[0]
        for field in ("id", "memory_class", "kind", "signature",
                      "sample_size", "success_rate", "stability",
                      "proposed_semantic_entry", "evidence_refs",
                      "status", "version"):
            self.assertIn(field, proposal)
        self.assertEqual(proposal["memory_class"], "reflective")
        self.assertEqual(proposal["kind"], "semantic-promotion-proposal")
        self.assertEqual(proposal["status"], "pending-review")
        self.assertEqual(proposal["version"], "memory-contract-v1")
        self.assertTrue(proposal["id"].startswith("prop_"))

    def test_evidence_refs_sorted_deterministic(self):
        records = [_rec(rec_id=x) for x in ("zeta", "alpha", "beta")]
        proposal = mp.build_proposals(records, min_cluster_size=3)[0]
        self.assertEqual(proposal["evidence_refs"], ["alpha", "beta", "zeta"])


class DeterminismTests(unittest.TestCase):
    """Re-running on identical input must produce identical output."""

    def test_proposal_id_stable_across_calls(self):
        records = [_rec(rec_id=f"r{i}", exit_code=0) for i in range(3)]
        p1 = mp.build_proposals(records, min_cluster_size=3)
        p2 = mp.build_proposals(records, min_cluster_size=3)
        self.assertEqual([p["id"] for p in p1], [p["id"] for p in p2])

    def test_proposal_order_stable(self):
        records = (
            [_rec(rec_id=f"p{i}", pattern="git push") for i in range(3)]
            + [_rec(rec_id=f"n{i}", pattern="npm publish") for i in range(4)]
        )
        proposals = mp.build_proposals(records, min_cluster_size=3)
        # Sort key: sample_size desc, action_pattern asc
        patterns = [p["signature"]["action_pattern"] for p in proposals]
        self.assertEqual(patterns, ["npm publish", "git push"])


class WriteDisciplineTests(unittest.TestCase):
    """Proposals land only in reflective/. Semantic tier is untouched."""

    def test_writes_to_reflective_not_semantic(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            ep_dir = _write_episodic(
                tmp, [_rec(rec_id=f"r{i}", exit_code=0) for i in range(3)])
            refl_dir = tmp / "reflective"
            sem_dir = tmp / "semantic"
            report, count, path = mp.run_promote(
                episodic_dir=ep_dir,
                reflective_dir=refl_dir,
            )
            self.assertEqual(count, 1)
            self.assertIsNotNone(path)
            self.assertTrue((refl_dir / "semantic_proposals.jsonl").exists())
            self.assertFalse(sem_dir.exists(),
                             "semantic tier must not be created by promote")

    def test_empty_promotion_writes_nothing(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            ep_dir = tmp / "episodic"
            ep_dir.mkdir()
            refl_dir = tmp / "reflective"
            report, count, path = mp.run_promote(
                episodic_dir=ep_dir, reflective_dir=refl_dir)
            self.assertEqual(count, 0)
            self.assertIsNone(path)
            self.assertFalse((refl_dir / "semantic_proposals.jsonl").exists(),
                             "no proposals ⇒ no file created")

    def test_output_path_writes_markdown(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            ep_dir = _write_episodic(
                tmp, [_rec(rec_id=f"r{i}", exit_code=0) for i in range(3)])
            refl_dir = tmp / "reflective"
            out_path = tmp / "report.md"
            mp.run_promote(
                episodic_dir=ep_dir,
                reflective_dir=refl_dir,
                output_path=out_path,
            )
            self.assertTrue(out_path.exists())
            md = out_path.read_text()
            self.assertIn("# Semantic-Tier Promotion Report", md)
            self.assertIn("git push", md)


class ReportRenderingTests(unittest.TestCase):

    def test_empty_proposals_renders_no_candidates_message(self):
        report = mp.render_promotion_report(
            [], total_records=0, min_cluster_size=3)
        self.assertIn("No promotion candidates yet", report)

    def test_proposal_rendered_with_id_and_stability(self):
        records = [_rec(rec_id=f"r{i}", exit_code=0) for i in range(3)]
        proposals = mp.build_proposals(records, min_cluster_size=3)
        report = mp.render_promotion_report(
            proposals, total_records=3, min_cluster_size=3)
        self.assertIn("typically-succeeds", report)
        self.assertIn(proposals[0]["id"], report)
        self.assertIn("git push", report)


if __name__ == "__main__":
    unittest.main()
