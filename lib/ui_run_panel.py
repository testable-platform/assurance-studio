"""Streamlit run panel with live progress and stdout streaming."""

from __future__ import print_function

import contextlib
import io

import streamlit as st


class _LiveLog(io.StringIO):
    def __init__(self, box, max_lines=200):
        super().__init__()
        self._box = box
        self._lines = []
        self._max = max_lines

    def write(self, s):
        if not s:
            return 0
        super().write(s)
        for line in s.splitlines():
            if line.strip():
                self._lines.append(line.rstrip())
        if len(self._lines) > self._max:
            self._lines = self._lines[-self._max :]
        self._box.code("\n".join(self._lines[-40:]), language=None)
        return len(s)


class RunPanel(object):
    """Context manager: st.status + progress + live log."""

    def __init__(self, title):
        self.title = title
        self._status = None
        self.bar = None
        self.status_line = None
        self.log_box = None
        self._log_stream = None

    def __enter__(self):
        self._status = st.status(self.title, expanded=True)
        self._status.__enter__()
        self.bar = st.progress(0.0)
        self.status_line = st.empty()
        self.log_box = st.empty()
        self._log_stream = _LiveLog(self.log_box)
        return self

    def progress(self, phase, current, total, branch="", message=""):
        total = max(int(total or 0), 1)
        current = min(max(int(current or 0), 0), total)
        self.bar.progress(min(current / total, 1.0))
        self.status_line.markdown(
            "**%s** — `%s` — **%d / %d** — %s"
            % (self.title, phase, current, total, branch or "—")
        )
        if message:
            st.caption(message)

    def stdout_redirect(self):
        return contextlib.redirect_stdout(self._log_stream)

    def __exit__(self, exc_type, exc, tb):
        if exc_type:
            self._status.update(label="%s — failed" % self.title, state="error")
        else:
            self._status.update(label="%s — complete" % self.title, state="complete")
        return self._status.__exit__(exc_type, exc, tb)
