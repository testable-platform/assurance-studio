"""Tests for GitHub auth error mapping."""

import unittest

from lib.github_auth import (
    _write_access_error_message,
    check_app_repo_access,
    github_app_contents_write_help,
)


class WriteAccessErrorMessageTests(unittest.TestCase):
    def test_integration_error_for_app_user_shows_app_help(self):
        body = '{"message":"Resource not accessible by integration","status":"403"}'
        msg = _write_access_error_message(
            body,
            "shihafmohammed1/Tool_Testing",
            token="ghu_testtoken",
        )
        self.assertIn("Contents: Read & write", msg)
        self.assertIn("App permissions", msg)
        self.assertNotIn("fine-grained", msg.lower())

    def test_integration_error_for_pat_shows_generic_403(self):
        body = '{"message":"Resource not accessible by integration","status":"403"}'
        msg = _write_access_error_message(
            body,
            "owner/repo",
            token="ghp_classic",
        )
        self.assertIn("integration", msg.lower())
        self.assertNotIn("fine-grained PAT checklist", msg)

    def test_app_contents_help_mentions_permissions_url(self):
        msg = github_app_contents_write_help("owner/repo")
        self.assertIn("/permissions", msg)
        self.assertIn("Contents", msg)


class CheckAppRepoAccessMessageTests(unittest.TestCase):
    def test_probe_failure_for_app_user_needs_install(self):
        from unittest.mock import patch

        with patch("lib.github_auth.app_repo_install_status", return_value=(True, True, "ok")):
            with patch("lib.github_auth.check_repo_access", return_value=(True, "ok", {"permissions": {"push": True}})):
                with patch("lib.github_api.probe_api_write", return_value=(False, "blocked")):
                    ok, needs_install, detail = check_app_repo_access("ghu_x", "owner/repo")
        self.assertFalse(ok)
        self.assertTrue(needs_install)
        self.assertIn("Contents: Read & write", detail)


if __name__ == "__main__":
    unittest.main()
