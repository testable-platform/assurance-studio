"""SQLite-backed SCM OAuth state and encrypted connection storage."""

from __future__ import print_function

import base64
import os
import secrets
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from lib.scm.token_encryption import decrypt_token, encrypt_token

ROOT = Path(__file__).resolve().parents[2]
_STATE_TTL_SEC = 600
_PROVIDER = "github"
_TOKEN_REFRESH_BUFFER_SEC = 120


def _db_path():
    custom = os.getenv("SCM_DB_PATH", "").strip()
    if custom:
        return Path(custom)
    return ROOT / "scm_connections.db"


@contextmanager
def _connect():
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _migrate_db(conn):
    cols = {row[1] for row in conn.execute("PRAGMA table_info(scm_connections)")}
    if "token_expires_at" not in cols:
        conn.execute("ALTER TABLE scm_connections ADD COLUMN token_expires_at TEXT")
    if "refresh_token_expires_at" not in cols:
        conn.execute("ALTER TABLE scm_connections ADD COLUMN refresh_token_expires_at TEXT")


def _init_db(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS scm_oauth_state (
            state TEXT PRIMARY KEY,
            app_user TEXT NOT NULL,
            repo_slug TEXT NOT NULL,
            login_hint TEXT,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS scm_connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_user TEXT NOT NULL,
            provider TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            provider_user_id TEXT,
            provider_username TEXT,
            repo_slug TEXT NOT NULL,
            access_token_enc TEXT NOT NULL,
            refresh_token_enc TEXT,
            scopes TEXT,
            token_expires_at TEXT,
            refresh_token_expires_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(app_user, provider)
        );
        """
    )
    _migrate_db(conn)


def ensure_db():
    with _connect() as conn:
        _init_db(conn)


@dataclass(frozen=True)
class OAuthStateSession:
    app_user: str
    repo_slug: str
    login_hint: str | None = None


@dataclass(frozen=True)
class ScmConnectionRow:
    id: int
    app_user: str
    provider: str
    status: str
    provider_username: str | None
    provider_user_id: str | None
    repo_slug: str
    scopes: str | None
    access_token: str
    refresh_token: str | None
    token_expires_at: str | None
    refresh_token_expires_at: str | None
    updated_at: str


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _expiry_from_now(seconds):
    if seconds is None:
        return None
    try:
        sec = int(seconds)
    except (TypeError, ValueError):
        return None
    if sec <= 0:
        return None
    return (datetime.now(timezone.utc) + timedelta(seconds=sec)).isoformat()


def _parse_iso(value):
    if not value:
        return None
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _new_state_token():
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")


def create_oauth_state(app_user, login_hint=None, repo_slug=""):
    """Create single-use OAuth state (TTL enforced on consume)."""
    ensure_db()
    state = _new_state_token()
    with _connect() as conn:
        _init_db(conn)
        conn.execute(
            """
            INSERT INTO scm_oauth_state (state, app_user, repo_slug, login_hint, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                state,
                app_user.strip(),
                (repo_slug or "").strip(),
                (login_hint or "").strip() or None,
                _now_iso(),
            ),
        )
    return state


def consume_oauth_state(state):
    """Retrieve and delete OAuth state (single-use). Raises ValueError if invalid/expired."""
    if not (state or "").strip():
        raise ValueError("Missing OAuth state")
    ensure_db()
    with _connect() as conn:
        _init_db(conn)
        row = conn.execute(
            "SELECT state, app_user, repo_slug, login_hint, created_at FROM scm_oauth_state WHERE state = ?",
            (state.strip(),),
        ).fetchone()
        if not row:
            raise ValueError("Invalid or expired OAuth state. Start connect again.")
        conn.execute("DELETE FROM scm_oauth_state WHERE state = ?", (state.strip(),))
        created = datetime.fromisoformat(row["created_at"])
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - created > timedelta(seconds=_STATE_TTL_SEC):
            raise ValueError("OAuth state expired. Start connect again.")
        return OAuthStateSession(
            app_user=row["app_user"],
            repo_slug=row["repo_slug"],
            login_hint=row["login_hint"],
        )


def upsert_connection(
    app_user,
    *,
    provider,
    repo_slug,
    provider_user_id,
    provider_username,
    access_token,
    refresh_token=None,
    scopes="",
    expires_in=None,
    refresh_token_expires_in=None,
):
    """Insert or update encrypted SCM connection for app_user+provider."""
    ensure_db()
    access_enc = encrypt_token(access_token)
    refresh_enc = encrypt_token(refresh_token) if refresh_token else None
    token_expires_at = _expiry_from_now(expires_in)
    refresh_token_expires_at = _expiry_from_now(refresh_token_expires_in)
    now = _now_iso()
    with _connect() as conn:
        _init_db(conn)
        conn.execute(
            """
            INSERT INTO scm_connections (
                app_user, provider, status, provider_user_id, provider_username,
                repo_slug, access_token_enc, refresh_token_enc, scopes,
                token_expires_at, refresh_token_expires_at, created_at, updated_at
            ) VALUES (?, ?, 'active', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(app_user, provider) DO UPDATE SET
                status = 'active',
                provider_user_id = excluded.provider_user_id,
                provider_username = excluded.provider_username,
                repo_slug = excluded.repo_slug,
                access_token_enc = excluded.access_token_enc,
                refresh_token_enc = excluded.refresh_token_enc,
                scopes = excluded.scopes,
                token_expires_at = excluded.token_expires_at,
                refresh_token_expires_at = excluded.refresh_token_expires_at,
                updated_at = excluded.updated_at
            """,
            (
                app_user.strip(),
                provider,
                provider_user_id,
                provider_username,
                repo_slug.strip(),
                access_enc,
                refresh_enc,
                scopes or "",
                token_expires_at,
                refresh_token_expires_at,
                now,
                now,
            ),
        )
        row = conn.execute(
            "SELECT id FROM scm_connections WHERE app_user = ? AND provider = ?",
            (app_user.strip(), provider),
        ).fetchone()
        return int(row["id"])


def update_connection_tokens(
    app_user,
    *,
    provider=_PROVIDER,
    access_token,
    refresh_token=None,
    scopes="",
    expires_in=None,
    refresh_token_expires_in=None,
):
    """Update tokens after refresh without changing repo/user metadata."""
    ensure_db()
    access_enc = encrypt_token(access_token)
    refresh_enc = encrypt_token(refresh_token) if refresh_token else None
    token_expires_at = _expiry_from_now(expires_in)
    refresh_token_expires_at = _expiry_from_now(refresh_token_expires_in)
    now = _now_iso()
    with _connect() as conn:
        _init_db(conn)
        cur = conn.execute(
            """
            UPDATE scm_connections
            SET access_token_enc = ?,
                refresh_token_enc = COALESCE(?, refresh_token_enc),
                scopes = COALESCE(NULLIF(?, ''), scopes),
                token_expires_at = ?,
                refresh_token_expires_at = COALESCE(?, refresh_token_expires_at),
                updated_at = ?
            WHERE app_user = ? AND provider = ? AND status = 'active'
            """,
            (
                access_enc,
                refresh_enc,
                scopes or "",
                token_expires_at,
                refresh_token_expires_at,
                now,
                app_user.strip(),
                provider,
            ),
        )
        if cur.rowcount == 0:
            raise ValueError("No active SCM connection to refresh for %s" % app_user)


def _row_to_connection(row):
    try:
        token = decrypt_token(row["access_token_enc"])
    except Exception:
        return None
    refresh_token = None
    if row["refresh_token_enc"]:
        try:
            refresh_token = decrypt_token(row["refresh_token_enc"])
        except Exception:
            refresh_token = None
    return ScmConnectionRow(
        id=int(row["id"]),
        app_user=row["app_user"],
        provider=row["provider"],
        status=row["status"],
        provider_username=row["provider_username"],
        provider_user_id=row["provider_user_id"],
        repo_slug=row["repo_slug"],
        scopes=row["scopes"],
        access_token=token,
        refresh_token=refresh_token,
        token_expires_at=row["token_expires_at"],
        refresh_token_expires_at=row["refresh_token_expires_at"],
        updated_at=row["updated_at"] or "",
    )


def get_connection(app_user, provider=_PROVIDER):
    """Return active connection with decrypted tokens, or None."""
    if not (app_user or "").strip():
        return None
    ensure_db()
    with _connect() as conn:
        _init_db(conn)
        row = conn.execute(
            """
            SELECT id, app_user, provider, status, provider_username, provider_user_id,
                   repo_slug, scopes, access_token_enc, refresh_token_enc,
                   token_expires_at, refresh_token_expires_at, updated_at
            FROM scm_connections
            WHERE app_user = ? AND provider = ? AND status = 'active'
            """,
            (app_user.strip(), provider),
        ).fetchone()
        if not row:
            return None
        return _row_to_connection(row)


def connection_needs_refresh(conn, buffer_sec=_TOKEN_REFRESH_BUFFER_SEC):
    """Return True when access token is expired or near expiry."""
    if not conn or not conn.token_expires_at:
        return False
    expires = _parse_iso(conn.token_expires_at)
    if not expires:
        return False
    return datetime.now(timezone.utc) >= expires - timedelta(seconds=buffer_sec)


def refresh_token_expired(conn):
    if not conn or not conn.refresh_token_expires_at:
        return False
    expires = _parse_iso(conn.refresh_token_expires_at)
    if not expires:
        return False
    return datetime.now(timezone.utc) >= expires


def update_connection_repo(app_user, repo_slug, default_branch="main", provider=_PROVIDER):
    """Set the active target repository after OAuth repo discovery."""
    slug = (repo_slug or "").strip()
    if not slug or "/" not in slug:
        raise ValueError("Repository must be owner/repo")
    ensure_db()
    now = _now_iso()
    with _connect() as conn:
        _init_db(conn)
        cur = conn.execute(
            """
            UPDATE scm_connections
            SET repo_slug = ?, updated_at = ?
            WHERE app_user = ? AND provider = ? AND status = 'active'
            """,
            (slug, now, app_user.strip(), provider),
        )
        if cur.rowcount == 0:
            raise ValueError("No active SCM connection to update for %s" % app_user)
    return slug, (default_branch or "main").strip() or "main"


def revoke_connection(app_user, provider=_PROVIDER):
    """Revoke connection and wipe stored tokens."""
    if not (app_user or "").strip():
        return False
    ensure_db()
    with _connect() as conn:
        _init_db(conn)
        cur = conn.execute(
            """
            UPDATE scm_connections
            SET status = 'revoked',
                access_token_enc = '',
                refresh_token_enc = NULL,
                token_expires_at = NULL,
                refresh_token_expires_at = NULL,
                updated_at = ?
            WHERE app_user = ? AND provider = ? AND status = 'active'
            """,
            (_now_iso(), app_user.strip(), provider),
        )
        return cur.rowcount > 0
