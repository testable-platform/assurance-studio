"""SCM OAuth connection — GitHub OAuth App flow (ported from ai-testable-platform)."""

from lib.scm.connection_service import GitHubConnectionService
from lib.scm.store import get_connection, revoke_connection

__all__ = ["GitHubConnectionService", "get_connection", "revoke_connection"]
