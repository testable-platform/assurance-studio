"""Tests for GitHub OAuth URL building."""

import unittest
from urllib.parse import parse_qs, urlparse

from lib.scm import github_oauth


class BuildAuthorizationUrlTests(unittest.TestCase):
    def test_account_picker_does_not_add_prompt(self):
        url = github_oauth.build_authorization_url(
            client_id="test-client-id",
            redirect_uri="http://localhost:8501/",
            state="state-token",
            account_picker=True,
        )
        parsed = urlparse(url)
        self.assertEqual(parsed.path, "/login/oauth/authorize")
        qs = parse_qs(parsed.query)
        self.assertNotIn("prompt", qs)
        self.assertEqual(qs.get("client_id"), ["test-client-id"])

    def test_login_hint_included(self):
        url = github_oauth.build_authorization_url(
            client_id="cid",
            redirect_uri="http://localhost:8501/",
            state="s",
            login_hint="OtherUser",
        )
        qs = parse_qs(urlparse(url).query)
        self.assertEqual(qs.get("login"), ["OtherUser"])

    def test_authorize_url_has_required_params(self):
        url = github_oauth.build_authorization_url(
            client_id="test-client-id",
            redirect_uri="http://localhost:8501/",
            state="state-token-xyz",
        )
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        self.assertEqual(parsed.scheme + "://" + parsed.netloc + parsed.path, "https://github.com/login/oauth/authorize")
        self.assertEqual(qs.get("client_id"), ["test-client-id"])
        self.assertEqual(qs.get("redirect_uri"), ["http://localhost:8501/"])
        self.assertEqual(qs.get("state"), ["state-token-xyz"])
        self.assertNotIn("prompt", qs)


if __name__ == "__main__":
    unittest.main()
