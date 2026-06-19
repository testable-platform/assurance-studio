"""Tests for QA credential resolution in the UI."""

import unittest
from unittest.mock import patch


class QaEffectiveCredsTests(unittest.TestCase):
    def test_session_only_no_env_fallback(self):
        import streamlit as st

        st.session_state.clear()
        st.session_state["qa_login_ok"] = False

        with patch("ui.app._qa_session_creds", return_value=(None, None)):
            with patch("ui.app._qa_env_creds", return_value=("env@test.com", "secret")) as env_mock:
                from ui.app import _qa_effective_creds

                email, password, source = _qa_effective_creds()
        env_mock.assert_not_called()
        self.assertIsNone(email)
        self.assertIsNone(password)
        self.assertIsNone(source)

    def test_returns_signed_in_session(self):
        import streamlit as st

        st.session_state.clear()
        st.session_state["qa_login_ok"] = True
        st.session_state["qa_email_saved"] = "user@test.com"
        st.session_state["qa_password_saved"] = "pw"

        from ui.app import _qa_effective_creds

        email, password, source = _qa_effective_creds()
        self.assertEqual(email, "user@test.com")
        self.assertEqual(password, "pw")
        self.assertEqual(source, "session")


class AppUserEmailTests(unittest.TestCase):
    def test_identity_without_password_after_oauth(self):
        import streamlit as st

        st.session_state.clear()
        st.session_state["_bound_app_user"] = "oauth@test.com"
        st.session_state["qa_email_saved"] = "oauth@test.com"

        from ui.app import _app_user_email, _qa_effective_creds

        self.assertEqual(_app_user_email(), "oauth@test.com")
        email, password, source = _qa_effective_creds()
        self.assertIsNone(email)
        self.assertIsNone(password)

    def test_github_login_is_app_identity(self):
        import streamlit as st

        st.session_state.clear()
        st.session_state["github_user_login"] = "octocat"
        st.session_state["qa_login_ok"] = True
        st.session_state["qa_email_saved"] = "signed@test.com"
        st.session_state["qa_password_saved"] = "pw"
        st.session_state["_bound_app_user"] = "other@test.com"

        from ui.app import _app_user_email

        self.assertEqual(_app_user_email(), "octocat")

    def test_bound_user_used_when_no_github(self):
        import streamlit as st

        st.session_state.clear()
        st.session_state["_bound_app_user"] = "other@test.com"
        st.session_state["qa_login_ok"] = True
        st.session_state["qa_email_saved"] = "signed@test.com"
        st.session_state["qa_password_saved"] = "pw"

        from ui.app import _app_user_email

        self.assertEqual(_app_user_email(), "other@test.com")


if __name__ == "__main__":
    unittest.main()
