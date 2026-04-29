"""Tests for CP-TEMPORAL-INTEGRITY-EXPANSION-01 Item 1 (Event 82) —
profile axis history hash-chained stream at
~/.episteme/memory/reflective/profile_history.jsonl.

Coverage:
- axis_name validation (must be one of 16 declared schema axes)
- reason validation (lazy-token + min-char rejection)
- old_value / new_value validation (must be non-empty strings)
- record_change writes valid cp7-chained-v1 envelope
- walk_axis_history returns chronological trajectory for axis
- list_axes_with_history returns set of axes with at least one entry
- chain integrity across multiple writes
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from episteme import _profile_history as ph


class ValidateAxisNameTests(unittest.TestCase):
    def test_valid_axis_accepted(self):
        ph.validate_axis_name("asymmetry_posture")
        ph.validate_axis_name("planning_strictness")
        ph.validate_axis_name("expertise_map")
        # Should NOT raise

    def test_unknown_axis_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            ph.validate_axis_name("not_a_real_axis")
        self.assertIn("unknown axis_name", str(ctx.exception))

    def test_empty_axis_rejected(self):
        with self.assertRaises(ValueError):
            ph.validate_axis_name("")
        with self.assertRaises(ValueError):
            ph.validate_axis_name("   ")

    def test_non_string_axis_rejected(self):
        with self.assertRaises(ValueError):
            ph.validate_axis_name(None)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            ph.validate_axis_name(123)  # type: ignore[arg-type]


class ValidateReasonTests(unittest.TestCase):
    def test_lazy_token_n_a_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            ph.validate_reason("n/a")
        self.assertIn("lazy-token", str(ctx.exception))

    def test_lazy_token_korean_rejected(self):
        with self.assertRaises(ValueError):
            ph.validate_reason("해당 없음")

    def test_short_reason_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            ph.validate_reason("too short")
        self.assertIn("at least", str(ctx.exception))

    def test_substantive_reason_accepted(self):
        ph.validate_reason("Re-elicited after lived-behavior closure across Events 65-67.")
        # Should NOT raise

    def test_non_string_reason_rejected(self):
        with self.assertRaises(ValueError):
            ph.validate_reason(None)  # type: ignore[arg-type]


class RecordChangeTests(unittest.TestCase):
    def test_record_change_writes_valid_envelope(self):
        with tempfile.TemporaryDirectory() as td:
            envelope = ph.record_change(
                "asymmetry_posture",
                old_value="inferred:loss-averse@2026-04-13",
                new_value="elicited:loss-averse@2026-04-27 with lived-behavior",
                reason="Re-elicit; lived-behavior closure across Events 65-67.",
                evidence_refs=["Event 65", "Event 66", "Event 67"],
                recorder="testuser",
                reflective_dir=Path(td),
            )
            self.assertEqual(envelope["schema_version"], "cp7-chained-v1")
            payload = envelope["payload"]
            self.assertEqual(payload["type"], "profile_axis_change")
            self.assertEqual(payload["axis_name"], "asymmetry_posture")
            self.assertEqual(payload["old_value"], "inferred:loss-averse@2026-04-13")
            self.assertEqual(payload["new_value"], "elicited:loss-averse@2026-04-27 with lived-behavior")
            self.assertEqual(payload["recorder"], "testuser")
            self.assertEqual(payload["evidence_refs"], ["Event 65", "Event 66", "Event 67"])
            self.assertIn("recorded_at", payload)
            self.assertTrue(envelope["entry_hash"].startswith("sha256:"))

    def test_record_change_invalid_axis_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                ph.record_change(
                    "fake_axis",
                    "old", "new",
                    "Substantive reason text here.",
                    reflective_dir=Path(td),
                )

    def test_record_change_invalid_reason_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                ph.record_change(
                    "asymmetry_posture",
                    "old", "new",
                    "tbd",  # lazy
                    reflective_dir=Path(td),
                )

    def test_record_change_empty_value_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                ph.record_change(
                    "asymmetry_posture",
                    "", "new",  # empty old
                    "Substantive reason text here.",
                    reflective_dir=Path(td),
                )
            with self.assertRaises(ValueError):
                ph.record_change(
                    "asymmetry_posture",
                    "old", "",  # empty new
                    "Substantive reason text here.",
                    reflective_dir=Path(td),
                )


class WalkAxisHistoryTests(unittest.TestCase):
    def test_walk_returns_empty_when_no_file(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(
                ph.walk_axis_history("asymmetry_posture", reflective_dir=Path(td)),
                [],
            )

    def test_walk_returns_chronological_trajectory(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            ph.record_change(
                "asymmetry_posture",
                "inferred", "elicited:loss-averse@2026-04-13",
                "Initial elicitation from cognitive_profile evidence.",
                reflective_dir=d,
            )
            ph.record_change(
                "asymmetry_posture",
                "elicited:loss-averse@2026-04-13",
                "elicited:loss-averse@2026-04-27 with lived-behavior",
                "Re-elicit after Events 65-67 closed the audit drift.",
                evidence_refs=["Event 65", "Event 66", "Event 67"],
                reflective_dir=d,
            )
            history = ph.walk_axis_history("asymmetry_posture", reflective_dir=d)
            self.assertEqual(len(history), 2)
            self.assertEqual(history[0]["payload"]["old_value"], "inferred")
            self.assertEqual(history[1]["payload"]["new_value"], "elicited:loss-averse@2026-04-27 with lived-behavior")

    def test_walk_filters_other_axes(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            ph.record_change(
                "asymmetry_posture",
                "old1", "new1",
                "Substantive reason text here.",
                reflective_dir=d,
            )
            ph.record_change(
                "fence_discipline",
                "old2", "new2",
                "Different axis change reason here.",
                reflective_dir=d,
            )
            asymmetry_history = ph.walk_axis_history("asymmetry_posture", reflective_dir=d)
            self.assertEqual(len(asymmetry_history), 1)
            self.assertEqual(asymmetry_history[0]["payload"]["axis_name"], "asymmetry_posture")


class ListAxesWithHistoryTests(unittest.TestCase):
    def test_list_returns_distinct_axes(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            ph.record_change("asymmetry_posture", "a", "b", "Substantive reason text.", reflective_dir=d)
            ph.record_change("fence_discipline", "c", "d", "Substantive reason text.", reflective_dir=d)
            ph.record_change("asymmetry_posture", "b", "e", "Substantive reason text.", reflective_dir=d)
            axes = ph.list_axes_with_history(reflective_dir=d)
            self.assertEqual(axes, {"asymmetry_posture", "fence_discipline"})

    def test_list_empty_when_no_file(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(ph.list_axes_with_history(reflective_dir=Path(td)), set())


class ChainIntegrityTests(unittest.TestCase):
    def test_chain_intact_after_multiple_writes(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            ph.record_change("planning_strictness", "v1", "v2", "Substantive reason.", reflective_dir=d)
            ph.record_change("risk_tolerance", "v1", "v2", "Substantive reason.", reflective_dir=d)
            ph.record_change("asymmetry_posture", "v1", "v2", "Substantive reason.", reflective_dir=d)
            verdict = ph.verify_chain(reflective_dir=d)
            self.assertTrue(verdict.intact)
            self.assertEqual(verdict.total_entries, 3)


if __name__ == "__main__":
    unittest.main()
