"""Tests for GitHub OAuth connection completion keying."""

import unittest
from unittest.mock import patch

from lib.scm import github_oauth
from lib.scm.connection_service import GitHubConnectionService


_CONFIG_ENV = {
    "GITHUB_OAUTH_CLIENT_ID": "cid",
    "GITHUB_OAUTH_CLIENT_SECRET": "secret",
    "GITHUB_OAUTH_REDIRECT_URI": "http://localhost:8501/",
    "SCM_TOKEN_SECRET": "token-secret",
}


class CompleteConnectionKeyingTests(unittest.TestCase):
    def test_connection_keyed_by_github_username(self):
        token = github_oauth.OAuthTokenResult(access_token="ghu_abc", refresh_token="ghr_xyz")
        user = github_oauth.OAuthUserInfo(provider_user_id="42", username="octocat")

        with patch.dict("os.environ", _CONFIG_ENV):
            svc = GitHubConnectionService()
            with patch("lib.scm.connection_service.github_oauth.exchange_code", return_value=token):
                with patch(
                    "lib.scm.connection_service.github_oauth.get_user_info",
                    return_value=user,
                ):
                    with patch(
                        "lib.scm.connection_service.upsert_connection",
                        return_value=7,
                    ) as mock_upsert:
                        result = svc.complete_connection("code-123", "pending-token")

        self.assertEqual(result.app_identity, "octocat")
        self.assertEqual(result.provider_username, "octocat")
        self.assertEqual(result.connection_id, 7)
        keyed_user = mock_upsert.call_args.args[0]
        self.assertEqual(keyed_user, "octocat")

    def test_falls_back_to_app_user_when_username_blank(self):
        token = github_oauth.OAuthTokenResult(access_token="ghu_abc")
        user = github_oauth.OAuthUserInfo(provider_user_id="", username="")

        with patch.dict("os.environ", _CONFIG_ENV):
            svc = GitHubConnectionService()
            with patch("lib.scm.connection_service.github_oauth.exchange_code", return_value=token):
                with patch(
                    "lib.scm.connection_service.github_oauth.get_user_info",
                    return_value=user,
                ):
                    with patch(
                        "lib.scm.connection_service.upsert_connection",
                        return_value=1,
                    ) as mock_upsert:
                        result = svc.complete_connection("code-123", "pending-token")

        self.assertEqual(result.app_identity, "pending-token")
        self.assertEqual(mock_upsert.call_args.args[0], "pending-token")


if __name__ == "__main__":
    unittest.main()
