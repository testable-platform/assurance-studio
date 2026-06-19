"""Tests for Testable login retry and UI error mapping."""

import io
import unittest
from unittest.mock import Mock, patch

import urllib.error

from lib.sa_qa import _is_transient_login_error, login


class TransientLoginErrorTests(unittest.TestCase):
    def test_http_520_is_transient(self):
        err = urllib.error.HTTPError("http://x", 520, "Bad", {}, None)
        self.assertTrue(_is_transient_login_error(err))

    def test_http_401_is_not_transient(self):
        err = urllib.error.HTTPError("http://x", 401, "Unauthorized", {}, None)
        self.assertFalse(_is_transient_login_error(err))


class LoginRetryTests(unittest.TestCase):
    def test_retries_transient_520_then_succeeds(self):
        calls = {"n": 0}

        def fake_urlopen(req, timeout=60):
            calls["n"] += 1
            if calls["n"] == 1:
                raise urllib.error.HTTPError(
                    req.full_url, 520, "Bad Gateway", {}, io.BytesIO(b"error code: 520")
                )
            resp = Mock()
            resp.headers = {"Set-Cookie": "session_token=abc123; Path=/"}
            return resp

        with patch.dict("os.environ", {"AUTH_LOGIN_RETRIES": "3", "AUTH_LOGIN_RETRY_SEC": "0"}):
            with patch("lib.sa_qa.time.sleep"):
                with patch("lib.sa_qa.urllib.request.urlopen", side_effect=fake_urlopen):
                    token = login("https://identity.test", "user@test.com", "secret")
        self.assertEqual(token, "abc123")
        self.assertEqual(calls["n"], 2)

    def test_fails_fast_on_401(self):
        def fake_urlopen(req, timeout=60):
            raise urllib.error.HTTPError(
                req.full_url, 401, "Unauthorized", {}, io.BytesIO(b"invalid credentials")
            )

        with patch.dict("os.environ", {"AUTH_LOGIN_RETRIES": "3", "AUTH_LOGIN_RETRY_SEC": "0"}):
            with patch("lib.sa_qa.urllib.request.urlopen", side_effect=fake_urlopen):
                with self.assertRaises(RuntimeError) as ctx:
                    login("https://identity.test", "user@test.com", "bad")
        self.assertIn("Login failed", str(ctx.exception))
        self.assertNotIn("temporarily unavailable", str(ctx.exception).lower())

    def test_exhausted_retries_raise_clear_message(self):
        def fake_urlopen(req, timeout=60):
            raise urllib.error.HTTPError(
                req.full_url, 520, "Bad Gateway", {}, io.BytesIO(b"error code: 520")
            )

        with patch.dict("os.environ", {"AUTH_LOGIN_RETRIES": "2", "AUTH_LOGIN_RETRY_SEC": "0"}):
            with patch("lib.sa_qa.time.sleep"):
                with patch("lib.sa_qa.urllib.request.urlopen", side_effect=fake_urlopen):
                    with self.assertRaises(RuntimeError) as ctx:
                        login("https://identity.test", "user@test.com", "secret")
        self.assertIn("temporarily unavailable", str(ctx.exception).lower())
        self.assertIn("520", str(ctx.exception))


class FriendlyRunErrorTests(unittest.TestCase):
    def test_transient_520_message(self):
        from ui.app import _friendly_run_error

        msg = _friendly_run_error(RuntimeError("Login failed: error code: 520"))
        self.assertIn("temporary error", msg.lower())
        self.assertIn("520", msg)

    def test_auth_failure_message(self):
        from ui.app import _friendly_run_error

        msg = _friendly_run_error(RuntimeError("Login failed: invalid credentials"))
        self.assertIn("authentication failed", msg.lower())


if __name__ == "__main__":
    unittest.main()
