"""Security envelope on API payloads."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

from security.crypto import AES256_ALGORITHM


class SecurityField(BaseModel):
    algorithm: Literal["AES-256-GCM"] = AES256_ALGORITHM
    integrity_hash: Optional[str] = None
    ciphertext: Optional[str] = None
