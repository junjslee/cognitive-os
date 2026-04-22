"""CP9 tests — Pillar 3 active guidance surface.

Covers:

- Query ranking (overlap threshold, ts tiebreak, project scope).
- Verdict filter (skip vapor-verdicted protocols).
- Hot-path integration (advisory fires, advisory silent below
  threshold, graceful degrade, advisory fires regardless of
  downstream reject).
- Min-overlap override (per-project file, clamping).
- CLI (list, --context, --since, --deferred, --json).
- SessionStart digest (protocol + deferred counts, since-last window,
  last_session.json update).
"""
from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from core.hooks import _guidance  # pyright: ignore[reportAttributeAccessIssue]
from core.hooks import _framework  # pyright: ignore[reportAttributeAccessIssue]
from core.hooks import _spot_check  # pyright: ignore[reportAttributeAccessIssue]
from core.hooks import _context_signature  # pyright: ignore[reportAttributeAccessIssue]
from core.hooks import reasoning_surface_guard as guard


class EphemeralHome:
    """Redirect EPISTEME_HOME for the duration of the test AND clear
    _guidance's warm cache so each test sees a fresh state."""
    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._orig = None

    def __enter__(self) -> Path:
        self._orig = os.environ.get("EPISTEME_HOME")
        os.environ["EPISTEME_HOME"] = self._tmp.name
        _guidance._clear_cache_for_tests()
        return Path(self._tmp.name)

    def __exit__(self, *a):
        _guidance._clear_cache_for_tests()
        if self._orig is None:
            os.environ.pop("EPISTEME_HOME", None)
        else:
            os.environ["EPISTEME_HOME"] = self._orig
        self._tmp.cleanup()


def _write_protocol(payload: dict, ts: str | None = None) -> dict:
    """Low-level test helper — appends a protocol record. Override ts
    via monkey-patching _chain.append is out of scope; use tight
    spacing via sleep if determinism is needed."""
    return _framework.write_protocol(payload)


def _sig_dict(
    project_name: str = "example",
    project_tier: str = "python",
    blueprint: str = "fence_reconstruction",
    op_class: str = "fence:constraint-removal",
    constraint_head: str | None = "core/hooks/x.py:10",
    runtime_marker: str = "governed",
) -> dict:
    return {
        "project_name": project_name,
        "project_tier": project_tier,
        "blueprint": blueprint,
        "op_class": op_class,
        "constraint_head": constraint_head,
        "runtime_marker": runtime_marker,
    }


def _candidate(**overrides) -> _context_signature.ContextSignature:
    defaults = dict(
        project_name="example",
        project_tier="python",
        blueprint="fence_reconstruction",
        op_class="fence:constraint-removal",
        constraint_head="core/hooks/x.py:10",
        runtime_marker="governed",
    )
    defaults.update(overrides)
    return _context_signature.ContextSignature(**defaults)


# ---------- Query ranking -----------------------------------------------


class QueryRanking(unittest.TestCase):
    def test_empty_framework_returns_none(self):
        with EphemeralHome():
            with tempfile.TemporaryDirectory() as cwd:
                result = _guidance.query(_candidate(), cwd=Path(cwd))
                self.assertIsNone(result)

    def test_below_threshold_returns_none(self):
        with EphemeralHome():
            # Protocol matches only on project_name + runtime_marker
            # (2/6) — below default min_overlap=4.
            _write_protocol({
                "blueprint": "other_blueprint",
                "correlation_id": "p1",
                "synthesized_protocol": "irrelevant protocol",
                "context_signature": _sig_dict(
                    blueprint="other_blueprint",
                    project_tier="node",
                    op_class="npm publish",
                    constraint_head=None,
                ),
            })
            with tempfile.TemporaryDirectory() as cwd:
                result = _guidance.query(_candidate(), cwd=Path(cwd))
                self.assertIsNone(result)

    def test_at_threshold_returns_match(self):
        with EphemeralHome():
            # 4/6 match — equal on project_name, project_tier,
            # blueprint, runtime_marker; differ on op_class + head.
            _write_protocol({
                "blueprint": "fence_reconstruction",
                "correlation_id": "p1",
                "synthesized_protocol": "threshold match",
                "context_signature": _sig_dict(
                    op_class="different_op",
                    constraint_head="different/head",
                ),
            })
            with tempfile.TemporaryDirectory() as cwd:
                result = _guidance.query(_candidate(), cwd=Path(cwd))
            self.assertIsNotNone(result)
            assert result is not None
            self.assertEqual(result.overlap, 4)

    def test_higher_overlap_ranks_above_lower(self):
        with EphemeralHome():
            _write_protocol({
                "blueprint": "fence_reconstruction",
                "correlation_id": "lower",
                "synthesized_protocol": "lower overlap",
                "context_signature": _sig_dict(
                    op_class="different",
                    constraint_head="different/head",
                ),
            })
            _write_protocol({
                "blueprint": "fence_reconstruction",
                "correlation_id": "higher",
                "synthesized_protocol": "higher overlap",
                "context_signature": _sig_dict(),  # all 6 match
            })
            with tempfile.TemporaryDirectory() as cwd:
                result = _guidance.query(_candidate(), cwd=Path(cwd))
            assert result is not None
            self.assertEqual(result.overlap, 6)
            self.assertEqual(result.correlation_id, "higher")

    def test_tie_broken_by_ts_desc(self):
        import time
        with EphemeralHome():
            _write_protocol({
                "blueprint": "fence_reconstruction",
                "correlation_id": "older",
                "synthesized_protocol": "older",
                "context_signature": _sig_dict(),
            })
            time.sleep(0.01)
            _write_protocol({
                "blueprint": "fence_reconstruction",
                "correlation_id": "newer",
                "synthesized_protocol": "newer",
                "context_signature": _sig_dict(),
            })
            with tempfile.TemporaryDirectory() as cwd:
                result = _guidance.query(_candidate(), cwd=Path(cwd))
            assert result is not None
            self.assertEqual(result.correlation_id, "newer")

    def test_project_scope_filter(self):
        with EphemeralHome():
            # Cross-project protocol with 5/6 overlap (everything
            # except project_name matches).
            _write_protocol({
                "blueprint": "fence_reconstruction",
                "correlation_id": "crossproject",
                "synthesized_protocol": "cross-project — should be filtered",
                "context_signature": _sig_dict(project_name="other_project"),
            })
            with tempfile.TemporaryDirectory() as cwd:
                result = _guidance.query(_candidate(), cwd=Path(cwd))
            # Must return None — cross-project match is suppressed by
            # the project-scope filter.
            self.assertIsNone(result)


# ---------- Verdict filter ----------------------------------------------


class VerdictFilter(unittest.TestCase):
    def _seed_vapor_verdict(self, cid: str, cwd: Path) -> None:
        """Seed a spot-check entry + vapor verdict for cid."""
        (cwd / ".episteme").mkdir(exist_ok=True)
        (cwd / ".episteme" / "spot_check_rate").write_text("1.0\n")
        _spot_check.maybe_sample(
            correlation_id=cid,
            op_label="git push",
            blueprint="fence_reconstruction",
            context_signature=_sig_dict(),
            surface_snapshot={
                "core_question": "q", "disconfirmation": "d",
                "unknowns": [], "hypothesis": "",
            },
            cwd=cwd,
        )
        _spot_check.write_verdict(
            correlation_id=cid,
            verdicts={"surface_validity": "vapor"},
        )

    def test_vapor_verdict_suppresses_protocol(self):
        with EphemeralHome():
            _write_protocol({
                "blueprint": "fence_reconstruction",
                "correlation_id": "vapor_cid",
                "synthesized_protocol": "vapor-verdicted protocol",
                "context_signature": _sig_dict(),
            })
            with tempfile.TemporaryDirectory() as td:
                cwd = Path(td)
                self._seed_vapor_verdict("vapor_cid", cwd)
                result = _guidance.query(_candidate(), cwd=cwd)
            self.assertIsNone(result)

    def test_useful_verdict_still_fires(self):
        with EphemeralHome():
            _write_protocol({
                "blueprint": "fence_reconstruction",
                "correlation_id": "good_cid",
                "synthesized_protocol": "useful protocol",
                "context_signature": _sig_dict(),
            })
            with tempfile.TemporaryDirectory() as td:
                cwd = Path(td)
                (cwd / ".episteme").mkdir(exist_ok=True)
                (cwd / ".episteme" / "spot_check_rate").write_text("1.0\n")
                _spot_check.maybe_sample(
                    correlation_id="good_cid",
                    op_label="git push",
                    blueprint="fence_reconstruction",
                    context_signature=_sig_dict(),
                    surface_snapshot={
                        "core_question": "q", "disconfirmation": "d",
                        "unknowns": [], "hypothesis": "",
                    },
                    cwd=cwd,
                )
                _spot_check.write_verdict(
                    correlation_id="good_cid",
                    verdicts={"surface_validity": "real"},
                )
                result = _guidance.query(_candidate(), cwd=cwd)
            assert result is not None
            self.assertEqual(result.correlation_id, "good_cid")

    def test_no_verdict_still_fires(self):
        with EphemeralHome():
            _write_protocol({
                "blueprint": "fence_reconstruction",
                "correlation_id": "unverdicted",
                "synthesized_protocol": "unverdicted protocol",
                "context_signature": _sig_dict(),
            })
            with tempfile.TemporaryDirectory() as cwd:
                result = _guidance.query(_candidate(), cwd=Path(cwd))
            assert result is not None
            self.assertEqual(result.correlation_id, "unverdicted")


# ---------- Min-overlap override ----------------------------------------


class MinOverlapOverride(unittest.TestCase):
    def test_no_override_returns_default(self):
        with tempfile.TemporaryDirectory() as cwd:
            self.assertEqual(
                _guidance.load_min_overlap(Path(cwd)),
                _guidance.MIN_OVERLAP_DEFAULT,
            )

    def test_valid_override_read(self):
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            (cwd / ".episteme").mkdir()
            (cwd / ".episteme" / "guidance_min_overlap").write_text("5\n")
            self.assertEqual(_guidance.load_min_overlap(cwd), 5)

    def test_override_clamped_to_range(self):
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            (cwd / ".episteme").mkdir()
            (cwd / ".episteme" / "guidance_min_overlap").write_text("99\n")
            self.assertEqual(_guidance.load_min_overlap(cwd), 6)
            (cwd / ".episteme" / "guidance_min_overlap").write_text("-5\n")
            self.assertEqual(_guidance.load_min_overlap(cwd), 0)

    def test_malformed_override_falls_back(self):
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            (cwd / ".episteme").mkdir()
            (cwd / ".episteme" / "guidance_min_overlap").write_text("not a number\n")
            self.assertEqual(
                _guidance.load_min_overlap(cwd),
                _guidance.MIN_OVERLAP_DEFAULT,
            )


# ---------- Advisory formatting -----------------------------------------


class AdvisoryFormat(unittest.TestCase):
    def test_header_format(self):
        match = _guidance.GuidanceMatch(
            protocol_payload={
                "blueprint": "fence_reconstruction",
                "synthesized_protocol": "test protocol",
                "correlation_id": "abc123def456ghi789",
            },
            overlap=5,
            synthesized_at="2026-04-21T12:00:00+00:00",
            correlation_id="abc123def456ghi789",
        )
        line = _guidance.format_advisory(match)
        self.assertIn("[episteme guide]", line)
        self.assertIn("2026-04-21", line)
        self.assertIn("fence_reconstruction", line)
        self.assertIn("overlap=5/6", line)
        self.assertIn("cid=abc123def456", line)
        self.assertIn("Protocol: test protocol", line)

    def test_long_protocol_truncated(self):
        long_text = "x" * 500
        match = _guidance.GuidanceMatch(
            protocol_payload={
                "blueprint": "generic",
                "synthesized_protocol": long_text,
                "correlation_id": "c1",
            },
            overlap=4,
            synthesized_at="2026-04-21T12:00:00+00:00",
            correlation_id="c1",
        )
        line = _guidance.format_advisory(match)
        self.assertIn("…", line)
        # Body should be bounded.
        self.assertLess(len(line), 500)


# ---------- Hot-path integration ----------------------------------------


def _run_guard(surface: dict, cwd: Path, command: str) -> tuple[int, str, str]:
    (cwd / ".episteme").mkdir(exist_ok=True)
    (cwd / ".episteme" / "reasoning-surface.json").write_text(
        json.dumps(surface), encoding="utf-8"
    )
    payload = {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(cwd)}
    raw = json.dumps(payload)
    with patch("sys.stdin", new=io.StringIO(raw)), \
         patch("sys.stdout", new=io.StringIO()) as fake_out, \
         patch("sys.stderr", new=io.StringIO()) as fake_err:
        rc = guard.main()
    return rc, fake_out.getvalue(), fake_err.getvalue()


def _base_surface(disconfirmation: str = "CI fails on main after push, tag verify rejects") -> dict:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "core_question": "does this pass guidance integration?",
        "knowns": ["tests pass"],
        "unknowns": [
            "if CI returns non-zero exit code on the push branch, "
            "local parity was false"
        ],
        "assumptions": ["hook runner is Claude Code"],
        "disconfirmation": disconfirmation,
        "verification_trace": {
            "or_test": "tests/test_guidance.py::test_smoke",
        },
    }


class HotPathIntegration(unittest.TestCase):
    def test_advisory_fires_on_matching_signature(self):
        with EphemeralHome():
            with tempfile.TemporaryDirectory() as td:
                cwd = Path(td)
                # Seed AGENTS.md so runtime_marker is governed (matches
                # the build() default under a cwd with it).
                (cwd / "AGENTS.md").write_text("# governed\n")
                (cwd / "pyproject.toml").write_text("[build-system]\n")
                from core.hooks import _grounding  # pyright: ignore[reportAttributeAccessIssue]
                _grounding._clear_cache_for_tests()
                # Build the signature the guard will compute.
                sig = _context_signature.build(
                    cwd, blueprint_name="generic", op_class="git push",
                )
                _write_protocol({
                    "blueprint": "generic",
                    "correlation_id": "seed_cid",
                    "synthesized_protocol": "contextual protocol for guidance",
                    "context_signature": sig.as_dict(),
                })
                rc, _out, err = _run_guard(
                    _base_surface(), cwd, "git push origin main"
                )
        self.assertEqual(rc, 0, f"stderr: {err}")
        self.assertIn("[episteme guide]", err)
        self.assertIn("contextual protocol for guidance", err)

    def test_advisory_silent_below_threshold(self):
        with EphemeralHome():
            with tempfile.TemporaryDirectory() as td:
                cwd = Path(td)
                # Protocol matches only on project_name — 1/6.
                _write_protocol({
                    "blueprint": "other",
                    "correlation_id": "mismatched",
                    "synthesized_protocol": "should not surface",
                    "context_signature": _sig_dict(
                        project_name=Path(cwd).name.lower(),
                        blueprint="other",
                        op_class="npm publish",
                        project_tier="node",
                        constraint_head=None,
                        runtime_marker="ad_hoc",
                    ),
                })
                rc, _out, err = _run_guard(
                    _base_surface(), cwd, "git push origin main"
                )
        self.assertEqual(rc, 0, f"stderr: {err}")
        self.assertNotIn("[episteme guide]", err)

    def test_advisory_silent_on_empty_framework(self):
        with EphemeralHome():
            with tempfile.TemporaryDirectory() as td:
                cwd = Path(td)
                rc, _out, err = _run_guard(
                    _base_surface(), cwd, "git push origin main"
                )
        self.assertEqual(rc, 0, f"stderr: {err}")
        self.assertNotIn("[episteme guide]", err)


# ---------- CLI ---------------------------------------------------------


def _run_cli(argv: list[str]) -> tuple[int, str]:
    from episteme import cli
    with patch("sys.stdout", new=io.StringIO()) as fake_out, \
         patch("sys.stderr", new=io.StringIO()):
        rc = cli.main(argv)
    return rc, fake_out.getvalue()


class GuideCli(unittest.TestCase):
    def test_guide_list_shows_protocols(self):
        with EphemeralHome():
            _write_protocol({
                "blueprint": "fence_reconstruction",
                "correlation_id": "c1",
                "synthesized_protocol": "keyword_alpha appears here",
                "context_signature": _sig_dict(),
            })
            rc, out = _run_cli(["guide"])
        self.assertEqual(rc, 0)
        self.assertIn("keyword_alpha", out)

    def test_guide_context_filter(self):
        with EphemeralHome():
            _write_protocol({
                "blueprint": "fence_reconstruction",
                "correlation_id": "c1",
                "synthesized_protocol": "keyword_alpha in first",
                "context_signature": _sig_dict(),
            })
            _write_protocol({
                "blueprint": "fence_reconstruction",
                "correlation_id": "c2",
                "synthesized_protocol": "keyword_beta in second",
                "context_signature": _sig_dict(),
            })
            rc, out = _run_cli(["guide", "--context", "alpha"])
        self.assertEqual(rc, 0)
        self.assertIn("keyword_alpha", out)
        self.assertNotIn("keyword_beta", out)

    def test_guide_since_filter_rejects_non_iso(self):
        with EphemeralHome():
            rc, _out = _run_cli(["guide", "--since", "yesterday"])
        self.assertEqual(rc, 2)

    def test_guide_deferred_lists_pending(self):
        with EphemeralHome():
            _framework.write_deferred_discovery({
                "flaw_classification": "doc-code-drift",
                "description": "test discovery",
                "observable": "grep -n phase_12 pending",
                "log_only_rationale": "out of scope this pass",
                "status": "pending",
            })
            rc, out = _run_cli(["guide", "--deferred"])
        self.assertEqual(rc, 0)
        self.assertIn("doc-code-drift", out)
        self.assertIn("test discovery", out)

    def test_guide_json_emits_structured(self):
        with EphemeralHome():
            _write_protocol({
                "blueprint": "fence_reconstruction",
                "correlation_id": "c1",
                "synthesized_protocol": "for json test",
                "context_signature": _sig_dict(),
            })
            rc, out = _run_cli(["guide", "--json"])
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertEqual(len(data), 1)
        self.assertIn("payload", data[0])


# ---------- SessionStart digest -----------------------------------------


class SessionStartDigest(unittest.TestCase):
    def test_digest_silent_when_both_zero(self):
        with EphemeralHome():
            from core.hooks import session_context as sc  # pyright: ignore[reportAttributeAccessIssue]
            line = sc._framework_digest_line()
        self.assertIsNone(line)

    def test_digest_shows_total_on_first_session(self):
        with EphemeralHome():
            _write_protocol({
                "blueprint": "fence_reconstruction",
                "correlation_id": "c1",
                "synthesized_protocol": "p1",
                "context_signature": _sig_dict(),
            })
            _write_protocol({
                "blueprint": "fence_reconstruction",
                "correlation_id": "c2",
                "synthesized_protocol": "p2",
                "context_signature": _sig_dict(),
            })
            from core.hooks import session_context as sc  # pyright: ignore[reportAttributeAccessIssue]
            line = sc._framework_digest_line()
        self.assertIsNotNone(line)
        assert line is not None
        # First session: since_last == total.
        self.assertIn("2 protocols synthesized since last session", line)
        self.assertIn("(2 total)", line)

    def test_digest_counts_only_new_since_last_session(self):
        with EphemeralHome() as home:
            from core.hooks import session_context as sc  # pyright: ignore[reportAttributeAccessIssue]
            # First protocol + first SessionStart — anchor last_session.
            _write_protocol({
                "blueprint": "fence_reconstruction",
                "correlation_id": "old",
                "synthesized_protocol": "old",
                "context_signature": _sig_dict(),
            })
            first_ts = datetime.now(timezone.utc).isoformat()
            sc._write_last_session_ts(first_ts)
            # Force-write a newer protocol by patching the append ts —
            # we rely on real time elapsing here.
            import time
            time.sleep(0.02)
            _write_protocol({
                "blueprint": "fence_reconstruction",
                "correlation_id": "new",
                "synthesized_protocol": "new",
                "context_signature": _sig_dict(),
            })
            line = sc._framework_digest_line()
        self.assertIsNotNone(line)
        assert line is not None
        self.assertIn("1 protocol synthesized since last session", line)
        self.assertIn("(2 total)", line)


if __name__ == "__main__":
    unittest.main()
