"""RAG metrics — computed from rag_eval (measured), not hardcoded."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from rag_eval import (
    CASE_META,
    DOMAIN_LABELS,
    compute_all_cases,
    compute_case_metrics,
    load_stores,
)

DATA_DIR = Path(__file__).resolve().parent / "data" / "encrypted"


@lru_cache(maxsize=1)
def _computed() -> dict[str, Any]:
    evidence, autopsies, timelines, movement = load_stores(DATA_DIR)
    return compute_all_cases(evidence, autopsies, timelines, movement, DATA_DIR)


def refresh_metrics_cache() -> None:
    _computed.cache_clear()


def domain_metrics_rows(case_id: str = "MG-101") -> list[dict[str, Any]]:
    return list(_computed()["cases"][case_id]["domains"])


def stage_metrics_rows(domain: str, case_id: str = "MG-101") -> list[dict[str, Any]]:
    stages = _computed()["cases"][case_id]["stages"]
    if domain != "evidence":
        return [
            {
                "stage": s["label"],
                "accuracy": s["score"] if s["score"] is not None else 0.0,
                "latency_ms": s["latency_ms"] or 0,
                "source": s["source"],
            }
            for s in stages
        ]
    return [
        {
            "stage": s["label"],
            "accuracy": s["score"] if s["score"] is not None else 0.0,
            "latency_ms": s["latency_ms"] or 0,
            "source": s["source"],
        }
        for s in stages
    ]


def get_eval_detail(case_id: str, domain: str) -> dict[str, Any]:
    return _computed()["cases"][case_id]["domain_eval"].get(domain, {})


def get_all_metrics(case_id: str = "MG-101") -> dict[str, Any]:
    m = _computed()["cases"][case_id]
    domains = m["domains"]
    avg_acc = sum(d["accuracy"] for d in domains) / max(len(domains), 1)
    avg_conf = sum(d["confidence"] for d in domains) / max(len(domains), 1)
    return {
        "case_id": case_id,
        "aggregate_accuracy": round(avg_acc, 3),
        "aggregate_confidence": round(avg_conf, 3),
        "domains": domains,
        "indexed_chunks": m["indexed_chunks"],
        "evidence_chunks": m["evidence_chunks"],
        "measured": True,
    }


def all_cases_comparison() -> list[dict[str, Any]]:
    return _computed()["all_domain_rows"]


# Legacy names for imports
PIPELINES = {k: {"domain": k, "label": DOMAIN_LABELS[k]} for k in DOMAIN_LABELS}
