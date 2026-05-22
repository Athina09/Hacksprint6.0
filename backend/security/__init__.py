"""AES-256-GCM security for AEGIS backend."""

from security.crypto import (
    AES256_ALGORITHM,
    decrypt_bytes,
    decrypt_json,
    encrypt_bytes,
    encrypt_json,
    is_key_configured,
    require_key,
    sha256_hex,
    sha256_json,
    verify_integrity,
)
from security.data import (
    AUTOPSIES_FILE,
    ENCRYPTED_DIR,
    decrypt_file_to_records,
    encrypt_csv_to_file,
    ensure_autopsies_file,
    load_autopsies,
    seed_autopsies,
)
from security.models import SecurityField

__all__ = [
    "AES256_ALGORITHM",
    "AUTOPSIES_FILE",
    "ENCRYPTED_DIR",
    "SecurityField",
    "decrypt_bytes",
    "decrypt_json",
    "decrypt_file_to_records",
    "encrypt_bytes",
    "encrypt_csv_to_file",
    "encrypt_json",
    "ensure_autopsies_file",
    "is_key_configured",
    "load_autopsies",
    "require_key",
    "seed_autopsies",
    "sha256_hex",
    "sha256_json",
    "verify_integrity",
]
