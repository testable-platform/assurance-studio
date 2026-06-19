"""Tests for SCM OAuth state storage."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from lib.scm.store import create_oauth_state, peek_oauth_state, consume_oauth_state


class PeekOauthStateTests(unittest.TestCase):
    def test_peek_does_not_consume(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "scm.db"
            with patch.dict("os.environ", {"SCM_DB_PATH": str(db_path)}):
                state = create_oauth_state("user@test.com", login_hint="hint")
                peeked = peek_oauth_state(state)
                self.assertIsNotNone(peeked)
                self.assertEqual(peeked.app_user, "user@test.com")
                self.assertEqual(peeked.login_hint, "hint")

                consumed = consume_oauth_state(state)
                self.assertEqual(consumed.app_user, "user@test.com")

    def test_peek_missing_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "scm.db"
            with patch.dict("os.environ", {"SCM_DB_PATH": str(db_path)}):
                self.assertIsNone(peek_oauth_state("missing-state-token"))


if __name__ == "__main__":
    unittest.main()
