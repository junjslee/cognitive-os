import io
import json
import unittest
from unittest.mock import patch

from core.hooks import workflow_guard


class WorkflowGuardTests(unittest.TestCase):
    def test_malformed_tool_input_does_not_crash(self):
        payload = {
            "tool_name": "Write",
            "tool_input": "not-a-dict",
            "session_type": "main",
        }
        raw = json.dumps(payload)

        with patch("sys.stdin", new=io.StringIO(raw)), patch("sys.stdout", new=io.StringIO()) as fake_out:
            rc = workflow_guard.main()

        self.assertEqual(rc, 0)
        self.assertEqual(fake_out.getvalue(), "")

    def test_camelcase_toolinput_subagent_is_skipped(self):
        payload = {
            "tool_name": "Write",
            "toolInput": {
                "path": "src/example.py",
                "is_subagent": True,
            },
            "session_type": "main",
        }
        raw = json.dumps(payload)

        with patch("sys.stdin", new=io.StringIO(raw)), patch("sys.stdout", new=io.StringIO()) as fake_out:
            rc = workflow_guard.main()

        self.assertEqual(rc, 0)
        self.assertEqual(fake_out.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
