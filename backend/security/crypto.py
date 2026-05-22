"""
AES-256-GCM implementation (cryptography.hazmat).

Wire format (url-safe base64):
  [version:1][nonce:12][ciphertext+tag]  → 256-bit key, 96-bit nonce, 128-bit GCM tag
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
from functools import lru_cache
from typing import Any

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

AES256_ALGORITHM = "AES-256-GCM"
ENV_KEY = "AEGIS_AES256_KEY"
AES256_KEY_BITS = 256
AES256_KEY_BYTES = AES256_KEY_BITS // 8
GCM_NONCE_BYTES = 12
GCM_TAG_BYTES = 16
ENVELOPE_VERSION = 1
GCM_AAD = b"aegis-command/aes256-gcm/v1"


def is_key_configured() -> bool:
    return bool(os.environ.get(ENV_KEY, "").strip())


def require_key() -> bytes:
    """Return the 32-byte AES-256 key; raise if missing."""
    return _load_key()


@lru_cache(maxsize=1)
def _load_key() -> bytes:
    raw = os.environ.get(ENV_KEY, "").strip()
    if not raw:
        raise ValueError(
            f"{ENV_KEY} is not set. Generate: python3 -c \"import secrets; print(secrets.token_hex(32))\""
        )
    if len(raw) == 64 and all(c in "0123456789abcdefABCDEF" for c in raw):
        key = bytes.fromhex(raw)
    else:
        key = HKDF(
            algorithm=hashes.SHA256(),
            length=AES256_KEY_BYTES,
            salt=b"aegis-command-aes256-v1",
            info=b"aegis-aes256-key",
        ).derive(raw.encode("utf-8"))
    if len(key) != AES256_KEY_BYTES:
        raise ValueError("AES-256 key must be 32 bytes.")
    return key


@lru_cache(maxsize=1)
def _aesgcm() -> AESGCM:
    return AESGCM(_load_key())


def encrypt_bytes(plaintext: bytes) -> str:
    """AES-256-GCM encrypt raw bytes → url-safe base64 envelope."""
    nonce = secrets.token_bytes(GCM_NONCE_BYTES)
    ciphertext = _aesgcm().encrypt(nonce, plaintext, GCM_AAD)
    envelope = bytes([ENVELOPE_VERSION]) + nonce + ciphertext
    return base64.urlsafe_b64encode(envelope).decode("ascii")


def decrypt_bytes(token: str) -> bytes:
    """Decrypt envelope produced by encrypt_bytes."""
    padded = token.encode("ascii")
    raw = base64.urlsafe_b64decode(padded + b"=" * (-len(padded) % 4))
    if len(raw) < 1 + GCM_NONCE_BYTES + GCM_TAG_BYTES:
        raise ValueError("Ciphertext too short for AES-256-GCM.")
    if raw[0] != ENVELOPE_VERSION:
        raise ValueError(f"Unknown envelope version: {raw[0]}")
    nonce = raw[1 : 1 + GCM_NONCE_BYTES]
    ciphertext = raw[1 + GCM_NONCE_BYTES :]
    try:
        return _aesgcm().decrypt(nonce, ciphertext, GCM_AAD)
    except Exception as exc:
        raise ValueError("AES-256-GCM decrypt failed (bad key or tampered data).") from exc


def encrypt_json(data: Any) -> str:
    """Encrypt a JSON-serializable object with AES-256-GCM."""
    plain = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return encrypt_bytes(plain)


def decrypt_json(token: str) -> Any:
    """Decrypt AES-256-GCM JSON envelope."""
    return json.loads(decrypt_bytes(token).decode("utf-8"))


def sha256_json(data: Any) -> str:
    plain = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(plain).hexdigest()


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_integrity(data: Any, expected_hex: str) -> bool:
    if not expected_hex or len(expected_hex) != 64:
        return False
    return secrets.compare_digest(sha256_json(data), expected_hex.lower())
