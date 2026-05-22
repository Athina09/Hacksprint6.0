"""AES-256 encrypted autopsy store: data/encrypted/autopsies.enc"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd

from security.crypto import decrypt_json, encrypt_json, is_key_configured, require_key

logger = logging.getLogger("aegis.security")

BACKEND_ROOT = Path(__file__).resolve().parent.parent
ENCRYPTED_DIR = BACKEND_ROOT / "data" / "encrypted"
AUTOPSIES_FILE = ENCRYPTED_DIR / "autopsies.enc"
DATASET_CSV = BACKEND_ROOT.parent / "dataset" / "forensic_autopsy_3000.csv"


def encrypt_csv_to_file(csv_path: Path | None = None, out_path: Path | None = None) -> Path:
    """Read plaintext CSV → write AES-256-GCM encrypted file."""
    require_key()
    target = out_path or AUTOPSIES_FILE
    source = csv_path or DATASET_CSV
    ENCRYPTED_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(source).fillna("")
    records = df.to_dict(orient="records")
    payload = {"dataset": source.name, "count": len(records), "records": records}

    target.write_text(encrypt_json(payload), encoding="utf-8")
    logger.info("AES-256-GCM wrote %s records → %s", len(records), target)
    return target


def decrypt_file_to_records(path: Path | None = None) -> list[dict[str, Any]]:
    """Decrypt autopsies.enc → list of autopsy dicts."""
    require_key()
    data = decrypt_json((path or AUTOPSIES_FILE).read_text(encoding="utf-8"))
    if isinstance(data, dict) and "records" in data:
        return data["records"]
    if isinstance(data, list):
        return data
    raise ValueError("Invalid encrypted autopsy file format.")


def seed_autopsies(*, force: bool = False) -> Path:
    if AUTOPSIES_FILE.exists() and not force:
        return AUTOPSIES_FILE
    return encrypt_csv_to_file()


def load_autopsies() -> list[dict[str, Any]]:
    return decrypt_file_to_records()


def ensure_autopsies_file() -> bool:
    if not is_key_configured():
        return False
    if not AUTOPSIES_FILE.exists():
        encrypt_csv_to_file()
    return AUTOPSIES_FILE.is_file()
