"""AES-256-GCM encryption for data at rest (NIST-approved AEAD)."""

from __future__ import annotations

import base64
import hashlib
import os
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

NONCE_SIZE = 12
KEY_SIZE = 32  # AES-256
ALGORITHM = "AES-256-GCM"


class EncryptionError(Exception):
    pass


class Aes256GcmCipher:
    """Encrypt/decrypt payloads with AES-256-GCM and a 256-bit key."""

    def __init__(self, key: bytes) -> None:
        if len(key) != KEY_SIZE:
            raise EncryptionError(
                f"{ALGORITHM} requires a {KEY_SIZE}-byte key (got {len(key)} bytes)"
            )
        self._aes = AESGCM(key)

    @classmethod
    def from_secret(cls, secret: str) -> Aes256GcmCipher:
        """Derive a stable 256-bit key from an environment secret (SHA-256)."""
        if not secret or not secret.strip():
            raise EncryptionError(
                "DATABASE_ENCRYPTION_KEY is missing. Set a 32+ character secret in .env"
            )
        key = hashlib.sha256(secret.encode("utf-8")).digest()
        return cls(key)

    @classmethod
    def from_env(cls) -> Aes256GcmCipher:
        return cls.from_secret(os.environ.get("DATABASE_ENCRYPTION_KEY", ""))

    def encrypt_bytes(self, plaintext: bytes, associated_data: bytes | None = None) -> bytes:
        nonce = os.urandom(NONCE_SIZE)
        ciphertext = self._aes.encrypt(nonce, plaintext, associated_data)
        return nonce + ciphertext

    def decrypt_bytes(self, payload: bytes, associated_data: bytes | None = None) -> bytes:
        if len(payload) < NONCE_SIZE + 16:
            raise EncryptionError("Ciphertext too short or corrupted")
        nonce, ciphertext = payload[:NONCE_SIZE], payload[NONCE_SIZE:]
        try:
            return self._aes.decrypt(nonce, ciphertext, associated_data)
        except Exception as exc:
            raise EncryptionError("Decryption failed — wrong key or tampered data") from exc

    def encrypt_json(self, data: Any, *, aad_label: str = "aegis-db") -> str:
        import json

        plaintext = json.dumps(data, separators=(",", ":")).encode("utf-8")
        aad = aad_label.encode("utf-8")
        blob = self.encrypt_bytes(plaintext, aad)
        return base64.b64encode(blob).decode("ascii")

    def decrypt_json(self, encoded: str, *, aad_label: str = "aegis-db") -> Any:
        import json

        blob = base64.b64decode(encoded.encode("ascii"))
        plaintext = self.decrypt_bytes(blob, aad_label.encode("utf-8"))
        return json.loads(plaintext.decode("utf-8"))

    @property
    def algorithm(self) -> str:
        return ALGORITHM
