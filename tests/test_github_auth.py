"""Tests for GitHub auth error mapping."""

import unittest
from unittest.mock import patch

from lib.github_auth import (
    _write_access_error_message,
    app_repo_install_status,
    check_app_repo_access,
    github_app_contents_write_help,
    github_app_install_help,
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
        with patch("lib.github_auth.check_repo_access", return_value=(True, "ok", {"permissions": {"push": True}})):
            with patch("lib.github_api.probe_api_write", return_value=(False, "blocked")):
                ok, needs_install, detail = check_app_repo_access("ghu_x", "owner/repo")
        self.assertFalse(ok)
        self.assertTrue(needs_install)
        self.assertIn("Contents: Read & write", detail)

    def test_write_probe_ok_despite_missing_install_listing(self):
        """Real write access wins even when install listing does not include the repo."""
        with patch("lib.github_auth.check_repo_access", return_value=(True, "ok", {"permissions": {"push": True}})):
            with patch("lib.github_api.probe_api_write", return_value=(True, "Git Data API blob write OK")):
                with patch(
                    "lib.github_auth.app_repo_install_status",
                    return_value=(True, False, "not listed"),
                ) as install_check:
                    ok, needs_install, detail = check_app_repo_access(
                        "ghu_x", "owner/my-repo",
                    )
        install_check.assert_not_called()
        self.assertTrue(ok)
        self.assertFalse(needs_install)
        self.assertIn("read/write access", detail)

    def test_read_fail_not_installed_app_user(self):
        with patch("lib.github_auth.check_repo_access", return_value=(False, "not found", None)):
            with patch(
                "lib.github_auth.app_repo_install_status",
                return_value=(False, False, github_app_install_help("owner/repo")),
            ):
                ok, needs_install, detail = check_app_repo_access("ghu_x", "owner/repo")
        self.assertFalse(ok)
        self.assertTrue(needs_install)
        self.assertIn("App permissions", detail)

    def test_read_fail_installed_but_no_repo_access(self):
        with patch("lib.github_auth.check_repo_access", return_value=(False, "no access", None)):
            with patch(
                "lib.github_auth.app_repo_install_status",
                return_value=(True, False, github_app_install_help("owner/repo")),
            ):
                ok, needs_install, detail = check_app_repo_access("ghu_x", "owner/repo")
        self.assertFalse(ok)
        self.assertTrue(needs_install)


class AppRepoInstallStatusTests(unittest.TestCase):
    def test_finds_repo_on_second_page(self):
        token = "ghu_pagination_test"
        slug = "owner/page-two-repo"

        def fake_api_request(tok, path, method="GET", body=None):
            self.assertEqual(tok, token)
            if path == "/user/installations?per_page=100":
                return {
                    "installations": [
                        {"id": 99, "app_slug": "testable-assurance-studio"},
                    ],
                }
            if path == "/user/installations/99/repositories?per_page=100&page=1":
                return {
                    "repositories": [
                        {"full_name": "owner/other-repo"},
                    ] * 100,
                }
            if path == "/user/installations/99/repositories?per_page=100&page=2":
                return {
                    "repositories": [
                        {"full_name": slug},
                    ],
                }
            raise AssertionError("unexpected path: %s" % path)

        with patch("lib.github_auth._api_request", side_effect=fake_api_request):
            with patch("lib.github_auth._configured_app_slug", return_value="testable-assurance-studio"):
                installed, repo_in_install, detail = app_repo_install_status(token, slug)
        self.assertTrue(installed)
        self.assertTrue(repo_in_install)
        self.assertIn(slug, detail)


if __name__ == "__main__":
    unittest.main()
