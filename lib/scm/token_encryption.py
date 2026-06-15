"""Fernet-based token encryption for SCM OAuth access tokens at rest."""

from __future__ import print_function

import base64
import hashlib
import os

from cryptography.fernet import Fernet


def _derive_key(secret):
    raw = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(raw)


def _get_fernet():
    secret = os.getenv("SCM_TOKEN_SECRET", "").strip()
    if not secret:
        raise RuntimeError("SCM_TOKEN_SECRET must be set for SCM token encryption")
    return Fernet(_derive_key(secret))


def encrypt_token(plaintext):
    """Encrypt a token string, returning a base64-encoded ciphertext."""
    return _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt_token(ciphertext):
    """Decrypt a base64-encoded ciphertext back to the original token."""
    return _get_fernet().decrypt(ciphertext.encode()).decode()
