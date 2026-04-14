import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.hooks import context_guard


class ContextGuardTests(unittest.TestCase):
    def test_safe_session_id_strips_path_chars(self):
        cleaned = context_guard._safe_session_id("../../evil\\name:123")
        self.assertNotIn("/", cleaned)
        self.assertNotIn("\\", cleaned)
        self.assertTrue(cleaned)

    def test_malicious_session_id_does_not_escape_tmp(self):
        with tempfile.TemporaryDirectory() as td:
            with patch("tempfile.gettempdir", return_value=td):
                sid = context_guard._safe_session_id("../../pwned")
                p = context_guard._state_file(sid)
                self.assertTrue(str(p).startswith(str(Path(td))))

    def test_invalid_or_empty_payload_is_noop(self):
        with patch("sys.stdin", new=io.StringIO("{}")), patch("sys.stdout", new=io.StringIO()) as fake_out:
            rc = context_guard.main()
        self.assertEqual(rc, 0)
        self.assertEqual(fake_out.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
