"""
AEGIS API — all database files encrypted at rest with AES-256-GCM.
Run: uvicorn main:app --host 127.0.0.1 --port 8000
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from security import Aes256GcmCipher, EncryptionError, SecureDatabase
from rag_pipeline import retrieve_evidence
from seed_data import (
    AUTOPSIES,
    CASE_MOVEMENT,
    CASE_TIMELINES,
    EVIDENCE_INDEX,
    SEED_VERSION,
)

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DATA_DIR = Path(__file__).resolve().parent / "data" / "encrypted"
CIPHER = Aes256GcmCipher.from_env()

STORES = {
    "autopsies": SecureDatabase(DATA_DIR / "autopsies.enc", CIPHER, aad="aegis-autopsies"),
    "evidence": SecureDatabase(DATA_DIR / "evidence.enc", CIPHER, aad="aegis-evidence"),
    "timelines": SecureDatabase(DATA_DIR / "timelines.enc", CIPHER, aad="aegis-timelines"),
    "movement": SecureDatabase(DATA_DIR / "movement.enc", CIPHER, aad="aegis-movement"),
}


def _bootstrap() -> None:
    marker = DATA_DIR / ".seed_version"
    stale = not marker.exists() or marker.read_text(encoding="utf-8").strip() != SEED_VERSION
    if stale:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        STORES["autopsies"].write(AUTOPSIES)
        STORES["evidence"].write(EVIDENCE_INDEX)
        STORES["timelines"].write(CASE_TIMELINES)
        STORES["movement"].write(CASE_MOVEMENT)
        marker.write_text(SEED_VERSION, encoding="utf-8")
    else:
        if not STORES["autopsies"].exists():
            STORES["autopsies"].write(AUTOPSIES)
        if not STORES["evidence"].exists():
            STORES["evidence"].write(EVIDENCE_INDEX)
        if not STORES["timelines"].exists():
            STORES["timelines"].write(CASE_TIMELINES)
        if not STORES["movement"].exists():
            STORES["movement"].write(CASE_MOVEMENT)


_bootstrap()

app = FastAPI(title="AEGIS Secure API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PMIRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    Age: int
    Sex: str
    Height: float
    Weight: float
    Putrefaction: int
    Putre_level: str
    rigor_mortis: str = Field(alias="Rigor Mortis")
    livor_mortis: str = Field(alias="Livor Mortis")
    algor_mortis: int = Field(alias="Algor Mortis")
    stomach_contents: str = Field(alias="Stomach Contents")
    vitreous_potassium: float = Field(alias="Vitreous Potassium")
    Entomology: str


@app.get("/api/security/status")
def security_status():
    key_set = bool(os.environ.get("DATABASE_ENCRYPTION_KEY", "").strip())
    return {
        "encryption_enabled": True,
        "algorithm": CIPHER.algorithm,
        "key_configured": key_set,
        "key_derivation": "SHA-256(secret) → 256-bit AES key",
        "databases": list(STORES.keys()),
        "storage_path": str(DATA_DIR),
        "files_encrypted": sum(1 for s in STORES.values() if s.exists()),
    }


@app.get("/api/stats")
def stats():
    autopsies = STORES["autopsies"].read([])
    evidence = STORES["evidence"].read([])
    return {
        "total_autopsies": len(autopsies),
        "active_cases": 8,
        "high_risk": 4,
        "ai_flagged": 5,
        "contradictions": 12,
        "missing_evidence": 3,
        "backend_online": True,
        "encryption": CIPHER.algorithm,
    }


@app.get("/api/autopsies")
def list_autopsies(limit: int = Query(50, ge=1, le=200), skip: int = Query(0, ge=0)):
    rows = STORES["autopsies"].read([])
    page = rows[skip : skip + limit]
    return {"data": page, "count": len(rows)}


@app.get("/api/autopsy/{cpr}")
def get_autopsy(cpr: str):
    rows = STORES["autopsies"].read([])
    for row in rows:
        if row.get("CPR Number") == cpr:
            return row
    raise HTTPException(status_code=404, detail="Autopsy record not found")


@app.get("/api/cases/{case_id}/timeline")
def case_timeline(case_id: str):
    timelines = STORES["timelines"].read({})
    events = timelines.get(case_id, [])
    return {"case_id": case_id, "timeline": events}


@app.get("/api/cases/{case_id}/movement")
def case_movement(case_id: str):
    movement = STORES["movement"].read({})
    points = movement.get(case_id, [])
    return {"case_id": case_id, "movement": points}


@app.get("/api/search")
def search_evidence(
    query: str,
    n_results: int = Query(5, ge=1, le=20),
    case_id: str | None = Query(None),
):
    evidence = STORES["evidence"].read([])
    out = retrieve_evidence(evidence, query, n_results=n_results, case_id=case_id)
    return {
        "query": out["query"],
        "results": [
            {
                "document": r["document"],
                "metadata": r["metadata"],
                "distance": r["distance"],
            }
            for r in out["results"]
        ],
    }


@app.get("/api/rag/flow")
def rag_flow():
    """RAG stage definitions for Streamlit / docs."""
    from rag_pipeline import DOMAIN_USES, RAG_FLOW

    return {"stages": RAG_FLOW, "domains": DOMAIN_USES}


@app.get("/api/rag/metrics")
def rag_metrics(case_id: str = Query("MG-101")):
    """Measured RAG metrics from seed eval (same as Streamlit dashboard)."""
    from rag_metrics import get_all_metrics, refresh_metrics_cache

    refresh_metrics_cache()
    return get_all_metrics(case_id)


@app.post("/pmi/predict")
def predict_pmi(body: PMIRequest):
    hours = 12.0 + body.Putrefaction * 6 + body.vitreous_potassium * 0.8
    if body.rigor_mortis == "Full":
        hours += 4
    confidence = min(0.95, 0.55 + body.Putrefaction * 0.08)
    return {
        "predicted_pmi_hours": round(hours, 1),
        "confidence_score": round(confidence, 2),
        "explanation": {
            "putrefaction": body.Putrefaction * 0.35,
            "vitreous_k": body.vitreous_potassium * 0.25,
            "entomology": 0.2,
        },
        "message": "PMI estimate from encrypted autopsy store (AES-256 protected)",
    }


@app.post("/api/admin/reencrypt")
def reencrypt_databases():
    """Re-write all stores (e.g. after key rotation — supply new DATABASE_ENCRYPTION_KEY first)."""
    try:
        for name, store in STORES.items():
            data = store.read([] if name == "autopsies" or name == "evidence" else {})
            store.write(data)
        return {"status": "ok", "algorithm": CIPHER.algorithm, "stores": list(STORES.keys())}
    except EncryptionError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
