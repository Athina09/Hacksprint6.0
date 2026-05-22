"""RAG flow definition + retrieval (shared by API and Streamlit)."""

from __future__ import annotations

import re
from typing import Any

# What each stage means in this hackathon build
RAG_FLOW: list[dict[str, Any]] = [
    {
        "id": "ingest",
        "label": "1. Ingest",
        "status": "live",
        "detail": "Case files land in AES-256 encrypted stores (autopsies, evidence, timelines, movement).",
    },
    {
        "id": "chunk",
        "label": "2. Chunk",
        "status": "live",
        "detail": "Each evidence row is one searchable chunk (document + metadata).",
    },
    {
        "id": "embed",
        "label": "3. Embed",
        "status": "planned",
        "detail": "bge-m3 embeddings — configured in metrics, not run on disk yet.",
    },
    {
        "id": "retrieve",
        "label": "4. Retrieve",
        "status": "live",
        "detail": "Keyword overlap search via GET /api/search (same logic as Copilot evidence lookup).",
    },
    {
        "id": "rerank",
        "label": "5. Rerank",
        "status": "planned",
        "detail": "Cross-encoder reranker — demo scores only in rag_metrics.py.",
    },
    {
        "id": "generate",
        "label": "6. Generate",
        "status": "planned",
        "detail": "LLM answer from retrieved chunks (Copilot UI; no local model server yet).",
    },
    {
        "id": "validate",
        "label": "7. Validate",
        "status": "planned",
        "detail": "Forensic validator gate before answers surface in the product.",
    },
]

DOMAIN_USES: list[dict[str, str]] = [
    {"domain": "evidence", "use": "Copilot Q&A and evidence search"},
    {"domain": "autopsy", "use": "Autopsy report synthesis"},
    {"domain": "tod", "use": "Time of death reasoning"},
    {"domain": "pmi", "use": "Postmortem interval (PMI API)"},
    {"domain": "timeline", "use": "Timeline reconstruction"},
    {"domain": "hypothesis", "use": "Hypothesis suggestions"},
    {"domain": "movement", "use": "Movement / location traces"},
]


def retrieve_evidence(
    evidence: list[dict[str, Any]],
    query: str,
    *,
    n_results: int = 5,
    case_id: str | None = None,
) -> dict[str, Any]:
    """Same retrieval as main.search_evidence — token match, ranked by hit count."""
    tokens = set(re.findall(r"\w+", query.lower()))
    scored: list[tuple[int, dict[str, Any]]] = []
    for item in evidence:
        meta = item.get("metadata") or {}
        if case_id and meta.get("case_id") != case_id:
            continue
        doc = item.get("document", "").lower()
        text = doc + " " + str(meta).lower()
        hits = sum(1 for t in tokens if t in text)
        if hits:
            scored.append((hits, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for hits, item in scored[:n_results]:
        meta = item.get("metadata", {})
        results.append(
            {
                "document": item.get("document", ""),
                "metadata": meta,
                "match_score": hits,
                "distance": round(1.0 / max(hits, 1), 3),
            }
        )
    return {
        "query": query,
        "case_id": case_id,
        "tokens": sorted(tokens),
        "chunks_scanned": len(evidence),
        "chunks_matched": len(scored),
        "results": results,
    }
