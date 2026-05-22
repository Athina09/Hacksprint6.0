"""Encrypted JSON database files — all records stored as AES-256-GCM blobs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypeVar

from .encryption import Aes256GcmCipher, EncryptionError

T = TypeVar("T")


class SecureDatabase:
    """One encrypted file per collection; plaintext never written to disk."""

    def __init__(self, path: Path, cipher: Aes256GcmCipher, *, aad: str) -> None:
        self.path = path
        self.cipher = cipher
        self.aad = aad
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def exists(self) -> bool:
        return self.path.is_file() and self.path.stat().st_size > 0

    def read(self, default: T) -> T:
        if not self.exists():
            return default
        try:
            encoded = self.path.read_text(encoding="utf-8")
            return self.cipher.decrypt_json(encoded, aad_label=self.aad)
        except (EncryptionError, json.JSONDecodeError, ValueError) as exc:
            raise EncryptionError(f"Cannot read encrypted store {self.path.name}") from exc

    def write(self, data: Any) -> None:
        encoded = self.cipher.encrypt_json(data, aad_label=self.aad)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(encoded, encoding="utf-8")
        tmp.replace(self.path)

    def wipe(self) -> None:
        if self.path.exists():
            self.path.unlink()
