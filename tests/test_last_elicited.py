"""Tests for the `last_elicited` metadata + stale-profile warning (Gap B)."""
from __future__ import annotations

import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from episteme import cli


class LastElicitedParserTests(unittest.TestCase):
    def _write_profile(self, td: Path, body: str) -> Path:
        p = td / "operator_profile.md"
        p.write_text(body, encoding="utf-8")
        return p

    def test_parses_simple_line(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._write_profile(Path(td), "# Title\n\nLast elicited: 2026-04-20\n")
            self.assertEqual(cli._read_last_elicited(path), date(2026, 4, 20))

    def test_parses_italicized_line(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._write_profile(Path(td), "# Title\n\n_Last elicited: 2026-04-13_\n")
            self.assertEqual(cli._read_last_elicited(path), date(2026, 4, 13))

    def test_parses_bullet_form(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._write_profile(Path(td), "# Title\n\n- Last elicited: 2026-02-02\n")
            self.assertEqual(cli._read_last_elicited(path), date(2026, 2, 2))

    def test_returns_none_when_absent(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._write_profile(Path(td), "# Title\n\nNo date here.\n")
            self.assertIsNone(cli._read_last_elicited(path))

    def test_returns_none_when_malformed(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._write_profile(Path(td), "# Title\n\nLast elicited: 2026-13-40\n")
            self.assertIsNone(cli._read_last_elicited(path))

    def test_returns_none_when_file_missing(self):
        self.assertIsNone(cli._read_last_elicited(Path("/nowhere/does/not/exist.md")))


class ProfileStalenessTests(unittest.TestCase):
    def _prof(self, td: Path, body: str) -> Path:
        p = td / "operator_profile.md"
        p.write_text(body, encoding="utf-8")
        return p

    def test_missing_profile(self):
        with tempfile.TemporaryDirectory() as td:
            status, age, elicited = cli._profile_staleness(
                profile_path=Path(td) / "nope.md",
                today=date(2026, 4, 20),
            )
            self.assertEqual(status, "missing")
            self.assertIsNone(age)
            self.assertIsNone(elicited)

    def test_unknown_when_no_date_line(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._prof(Path(td), "# Operator Profile\n\nNothing interesting.\n")
            status, age, elicited = cli._profile_staleness(
                profile_path=path,
                today=date(2026, 4, 20),
            )
            self.assertEqual(status, "unknown")
            self.assertIsNone(age)
            self.assertIsNone(elicited)

    def test_fresh_inside_window(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._prof(Path(td), "# p\n\nLast elicited: 2026-04-01\n")
            status, age, elicited = cli._profile_staleness(
                profile_path=path,
                today=date(2026, 4, 20),
            )
            self.assertEqual(status, "fresh")
            self.assertEqual(age, 19)
            self.assertEqual(elicited, date(2026, 4, 1))

    def test_stale_outside_window(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._prof(Path(td), "# p\n\nLast elicited: 2026-01-01\n")
            today = date(2026, 4, 20)
            status, age, elicited = cli._profile_staleness(profile_path=path, today=today)
            self.assertEqual(status, "stale")
            self.assertIsNotNone(age)
            assert age is not None  # for type checker
            self.assertGreater(age, cli.PROFILE_STALE_DAYS)
            self.assertEqual(elicited, date(2026, 1, 1))

    def test_fresh_profile_warning_is_none(self):
        out = cli._render_stale_profile_warning("fresh", 10, date(2026, 4, 10))
        self.assertIsNone(out)

    def test_stale_warning_mentions_age_and_date(self):
        out = cli._render_stale_profile_warning("stale", 45, date(2026, 3, 6))
        assert out is not None
        self.assertIn("Stale Context Warning", out)
        self.assertIn("2026-03-06", out)
        self.assertIn("45 days", out)
        self.assertIn("episteme profile hybrid", out)

    def test_unknown_warning_explains(self):
        out = cli._render_stale_profile_warning("unknown", None, None)
        assert out is not None
        self.assertIn("no `Last elicited:`", out)

    def test_missing_warning_fallback(self):
        out = cli._render_stale_profile_warning("missing", None, None)
        assert out is not None
        self.assertIn("No operator profile found", out)


class ClaudeAdapterSyncTests(unittest.TestCase):
    """Verifies the rendered CLAUDE.md includes the warning block when stale."""

    def test_fresh_profile_omits_warning_in_rendered_claude_md(self):
        from episteme.adapters import claude as claude_adapter

        # Point the staleness check at a fresh profile via monkey-patch.
        today = date.today()
        fresh = today - timedelta(days=1)

        orig = cli._profile_staleness
        cli._profile_staleness = lambda **_kw: ("fresh", 1, fresh)  # type: ignore[assignment]
        try:
            md = claude_adapter.render_user_claude_md()
        finally:
            cli._profile_staleness = orig  # type: ignore[assignment]

        self.assertNotIn("Stale Context Warning", md)

    def test_stale_profile_injects_warning_block(self):
        from episteme.adapters import claude as claude_adapter

        orig = cli._profile_staleness
        cli._profile_staleness = lambda **_kw: ("stale", 90, date(2026, 1, 20))  # type: ignore[assignment]
        try:
            md = claude_adapter.render_user_claude_md()
        finally:
            cli._profile_staleness = orig  # type: ignore[assignment]

        self.assertIn("Stale Context Warning", md)
        self.assertIn("2026-01-20", md)
        self.assertIn("90 days", md)


if __name__ == "__main__":
    unittest.main()
