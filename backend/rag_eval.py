"""Compute RAG metrics from real seed data + live retrieval (no hardcoded accuracy)."""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any

from rag_pipeline import retrieve_evidence
from seed_data import (
    CASE_MOVEMENT,
    CASE_TIMELINES,
    EVAL_CASES,
    EVIDENCE_EVAL_QUERIES,
    TIMELINE_EVAL_QUERIES,
)

DOMAIN_LABELS = {
    "autopsy": "Autopsy",
    "tod": "TOD",
    "pmi": "PMI",
    "timeline": "Timeline",
    "evidence": "Evidence",
    "hypothesis": "Hypothesis",
    "movement": "Movement",
}

CASE_META = EVAL_CASES


def _doc_matches(text: str, must_match: list[str]) -> bool:
    if not must_match:
        return False
    low = text.lower()
    return all(m.lower() in low for m in must_match)


def _search_records(
    records: list[dict[str, Any]],
    query: str,
    *,
    text_fn,
    n_results: int = 5,
) -> list[dict]:
    tokens = set(re.findall(r"\w+", query.lower()))
    scored: list[tuple[int, dict]] = []
    for item in records:
        text = text_fn(item).lower()
        hits = sum(1 for t in tokens if t in text)
        if hits:
            scored.append((hits, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [x[1] for x in scored[:n_results]]


def _run_query_eval(
    run_fn,
    queries: list[dict[str, Any]],
    *,
    k: int = 5,
) -> dict[str, Any]:
    precisions: list[float] = []
    recalls: list[float] = []
    mrrs: list[float] = []
    hits = 0
    rows: list[dict[str, Any]] = []
    latencies: list[float] = []

    for q in queries:
        t0 = time.perf_counter()
        results = run_fn(q)
        latency_ms = round((time.perf_counter() - t0) * 1000, 1)
        latencies.append(latency_ms)

        expect_empty = q.get("expect_empty", False)
        must = q.get("must_match", [])

        if expect_empty:
            ok = len(results) == 0
            prec = rec = 1.0 if ok else 0.0
            rr = 0.0
        else:
            rel_in_top = sum(1 for text in results[:k] if _doc_matches(text, must))
            prec = rel_in_top / k
            rank = next(
                (i + 1 for i, text in enumerate(results) if _doc_matches(text, must)),
                None,
            )
            rec = 1.0 if rank else 0.0
            rr = (1.0 / rank) if rank else 0.0

        if rec >= 1.0:
            hits += 1
        precisions.append(prec)
        recalls.append(rec)
        mrrs.append(rr)
        rows.append(
            {
                "query_id": q.get("id", ""),
                "query": q["query"],
                "case_id": q.get("case_id", ""),
                "pass": rec >= 1.0 if not expect_empty else prec >= 1.0,
                "precision_at_k": round(prec, 3),
                "recall_at_k": round(rec, 3),
                "mrr": round(rr, 3),
                "latency_ms": latency_ms,
                "top_hit": (results[0][:100] if results else "—"),
            }
        )

    n = max(len(queries), 1)
    p = sum(precisions) / n
    r = sum(recalls) / n
    return {
        "queries": len(queries),
        "hit_rate": round(hits / n, 3),
        "precision_at_k": round(p, 3),
        "recall_at_k": round(r, 3),
        "mrr": round(sum(mrrs) / n, 3),
        "f1": _f1(p, r),
        "avg_latency_ms": round(sum(latencies) / max(len(latencies), 1), 1),
        "rows": rows,
    }


def _f1(p: float, r: float) -> float:
    if p + r == 0:
        return 0.0
    return round(2 * p * r / (p + r), 3)


def evaluate_evidence(evidence: list[dict], case_id: str) -> dict[str, Any]:
    queries = [q for q in EVIDENCE_EVAL_QUERIES if q["case_id"] == case_id]

    def run(q: dict) -> list[str]:
        raw = retrieve_evidence(evidence, q["query"], n_results=5, case_id=q["case_id"])
        return [r["document"] for r in raw["results"]]

    return _run_query_eval(run, queries)


def evaluate_timeline(timelines: dict, case_id: str) -> dict[str, Any]:
    events = timelines.get(case_id, [])
    queries = [q for q in TIMELINE_EVAL_QUERIES if q["case_id"] == case_id]
    if not events or not queries:
        return _empty_eval("No timeline seed or eval queries")

    def run(q: dict) -> list[str]:
        found = _search_records(
            events,
            q["query"],
            text_fn=lambda e: f"{e.get('title', '')} {e.get('description', '')}",
        )
        return [f"{r.get('title', '')}: {r.get('description', '')}" for r in found]

    return _run_query_eval(run, queries)


def evaluate_movement(movement: dict, case_id: str) -> dict[str, Any]:
    points = movement.get(case_id, [])
    if not points:
        return _empty_eval("No movement seed for case")

    queries = [
        {"id": "m1", "case_id": case_id, "query": "Central Station", "must_match": ["Central"]},
        {"id": "m2", "case_id": case_id, "query": "Egmore", "must_match": ["Egmore"]},
        {"id": "m3", "case_id": case_id, "query": "Gate suspect", "must_match": ["Gate"]},
    ]

    def run(q: dict) -> list[str]:
        found = _search_records(points, q["query"], text_fn=lambda p: f"{p.get('label', '')} {p.get('type', '')}")
        return [r.get("label", "") for r in found]

    return _run_query_eval(run, queries)


def _empty_eval(note: str) -> dict[str, Any]:
    return {
        "queries": 0,
        "hit_rate": 0.0,
        "precision_at_k": 0.0,
        "recall_at_k": 0.0,
        "mrr": 0.0,
        "f1": 0.0,
        "avg_latency_ms": 0.0,
        "rows": [],
        "note": note,
    }


def evaluate_autopsy(autopsies: list[dict], case_id: str) -> dict[str, Any]:
    row = next((a for a in autopsies if a.get("case_id") == case_id), None)
    if not row:
        return _empty_eval("No autopsy record for case")
    required = ["CPR Number", "Age", "Vitreous Potassium", "Rigor Mortis"]
    filled = sum(1 for k in required if row.get(k) not in (None, ""))
    coverage = filled / len(required)
    return {
        "queries": 1,
        "hit_rate": 1.0,
        "precision_at_k": round(coverage, 3),
        "recall_at_k": round(coverage, 3),
        "mrr": 1.0,
        "f1": round(coverage, 3),
        "confidence": round(coverage, 3),
        "avg_latency_ms": 0.0,
        "rows": [
            {
                "query_id": "autopsy_fields",
                "query": "required fields present",
                "case_id": case_id,
                "pass": coverage >= 1.0,
                "top_hit": row.get("CPR Number", ""),
                "precision_at_k": round(coverage, 3),
                "recall_at_k": round(coverage, 3),
                "mrr": 1.0,
                "latency_ms": 0,
            }
        ],
        "note": "Autopsy store field completeness",
    }


def evaluate_pmi(autopsies: list[dict], case_id: str) -> dict[str, Any]:
    row = next((a for a in autopsies if a.get("case_id") == case_id), None)
    if not row:
        return _empty_eval("No autopsy for PMI")
    putrefaction = int(row.get("Putrefaction", 0))
    vk = float(row.get("Vitreous Potassium", 0))
    hours = 12.0 + putrefaction * 6 + vk * 0.8
    if row.get("Rigor Mortis") == "Full":
        hours += 4
    confidence = min(0.95, 0.55 + putrefaction * 0.08)
    c = round(confidence, 3)
    return {
        "queries": 1,
        "hit_rate": 1.0,
        "precision_at_k": c,
        "recall_at_k": c,
        "mrr": c,
        "f1": c,
        "confidence": c,
        "predicted_hours": round(hours, 1),
        "avg_latency_ms": 0.0,
        "rows": [
            {
                "query_id": "pmi_formula",
                "query": "PMI from vitreous + putrefaction",
                "case_id": case_id,
                "pass": True,
                "top_hit": f"{hours}h @ {confidence:.0%}",
                "precision_at_k": c,
                "recall_at_k": c,
                "mrr": c,
                "latency_ms": 0,
            }
        ],
        "note": "PMI /pmi/predict formula on autopsy row",
    }


def evaluate_tod(timelines: dict, case_id: str) -> dict[str, Any]:
    events = timelines.get(case_id, [])
    if not events:
        return _empty_eval("No timeline for TOD")
    confs = [e.get("confidence", 0) / 100.0 for e in events]
    avg = round(sum(confs) / len(confs), 3)
    return {
        "queries": len(events),
        "hit_rate": 1.0,
        "precision_at_k": avg,
        "recall_at_k": avg,
        "mrr": avg,
        "f1": avg,
        "confidence": avg,
        "avg_latency_ms": 0.0,
        "rows": [],
        "note": "Mean timeline event confidence (TOD signals)",
    }


def evaluate_hypothesis(evidence_ev: dict, timeline_ev: dict) -> dict[str, Any]:
    f1 = round((evidence_ev.get("f1", 0) + timeline_ev.get("f1", 0)) / 2, 3)
    return {
        "queries": 0,
        "hit_rate": f1,
        "precision_at_k": f1,
        "recall_at_k": f1,
        "mrr": f1,
        "f1": f1,
        "confidence": f1,
        "avg_latency_ms": 0.0,
        "rows": [],
        "note": "Average of evidence + timeline measured F1",
    }


def evaluate_stages(
    evidence: list[dict],
    evidence_ev: dict,
    data_dir: Path,
) -> list[dict[str, Any]]:
    enc = data_dir / "evidence.enc"
    chunks = len(evidence)
    return [
        {
            "id": "ingest",
            "label": "Document ingest",
            "score": 1.0 if enc.exists() else 0.0,
            "latency_ms": 0,
            "source": "evidence.enc on disk",
        },
        {
            "id": "chunk",
            "label": "Semantic chunking",
            "score": round(min(1.0, chunks / max(len(EVIDENCE_EVAL_QUERIES), 1)), 3),
            "latency_ms": 0,
            "source": f"{chunks} chunks indexed",
        },
        {
            "id": "embed",
            "label": "Embedding (bge-m3)",
            "score": None,
            "latency_ms": None,
            "source": "not implemented",
        },
        {
            "id": "retrieve",
            "label": "Retrieval (keyword)",
            "score": evidence_ev.get("recall_at_k", 0.0),
            "latency_ms": evidence_ev.get("avg_latency_ms", 0),
            "source": "EVIDENCE_EVAL_QUERIES recall@5",
        },
        {
            "id": "rerank",
            "label": "Cross-encoder rerank",
            "score": None,
            "latency_ms": None,
            "source": "not implemented",
        },
        {
            "id": "generate",
            "label": "LLM synthesis",
            "score": None,
            "latency_ms": None,
            "source": "not implemented",
        },
        {
            "id": "validate",
            "label": "Forensic validator",
            "score": None,
            "latency_ms": None,
            "source": "not implemented",
        },
    ]


def compute_case_metrics(
    case_id: str,
    evidence: list[dict],
    autopsies: list[dict],
    timelines: dict,
    movement: dict,
    data_dir: Path,
) -> dict[str, Any]:
    ev_ev = evaluate_evidence(evidence, case_id)
    tl_ev = evaluate_timeline(timelines, case_id)
    mv_ev = evaluate_movement(movement, case_id)
    au_ev = evaluate_autopsy(autopsies, case_id)
    pmi_ev = evaluate_pmi(autopsies, case_id)
    tod_ev = evaluate_tod(timelines, case_id)
    hyp_ev = evaluate_hypothesis(ev_ev, tl_ev)

    domain_eval = {
        "evidence": ev_ev,
        "timeline": tl_ev,
        "movement": mv_ev,
        "autopsy": au_ev,
        "pmi": pmi_ev,
        "tod": tod_ev,
        "hypothesis": hyp_ev,
    }

    rows = []
    for key, ev in domain_eval.items():
        rows.append(
            {
                "domain": key,
                "label": DOMAIN_LABELS[key],
                "dataset": case_id,
                "case_name": CASE_META[case_id]["label"],
                "accuracy": ev.get("f1", 0),
                "confidence": ev.get("confidence", ev.get("mrr", ev.get("f1", 0))),
                "f1": ev.get("f1", 0),
                "recall_at_k": ev.get("recall_at_k", 0),
                "precision_at_k": ev.get("precision_at_k", 0),
                "hit_rate": ev.get("hit_rate", 0),
                "eval_queries": ev.get("queries", 0),
                "source": ev.get("note", "retrieval eval on seed data"),
            }
        )

    case_chunks = len([e for e in evidence if (e.get("metadata") or {}).get("case_id") == case_id])

    return {
        "case_id": case_id,
        "domains": rows,
        "domain_eval": domain_eval,
        "stages": evaluate_stages(evidence, ev_ev, data_dir),
        "evidence_chunks": case_chunks,
        "indexed_chunks": len(evidence),
    }


def compute_all_cases(
    evidence: list[dict],
    autopsies: list[dict],
    timelines: dict,
    movement: dict,
    data_dir: Path,
) -> dict[str, Any]:
    by_case = {
        cid: compute_case_metrics(cid, evidence, autopsies, timelines, movement, data_dir)
        for cid in CASE_META
    }
    all_rows: list[dict] = []
    for m in by_case.values():
        all_rows.extend(m["domains"])
    return {"cases": by_case, "all_domain_rows": all_rows}


def load_stores(data_dir: Path) -> tuple[list, list, dict, dict]:
    """Load from encrypted files when possible, else seed."""
    from seed_data import AUTOPSIES, EVIDENCE_INDEX

    evidence = EVIDENCE_INDEX
    autopsies = AUTOPSIES
    timelines = CASE_TIMELINES
    movement = CASE_MOVEMENT
    try:
        from dotenv import load_dotenv
        from security import Aes256GcmCipher, SecureDatabase

        load_dotenv(data_dir.parent.parent.parent / ".env")
        c = Aes256GcmCipher.from_env()
        ev_path = data_dir / "evidence.enc"
        if ev_path.exists():
            evidence = SecureDatabase(ev_path, c, aad="aegis-evidence").read([])
        au_path = data_dir / "autopsies.enc"
        if au_path.exists():
            autopsies = SecureDatabase(au_path, c, aad="aegis-autopsies").read([])
        tl_path = data_dir / "timelines.enc"
        if tl_path.exists():
            timelines = SecureDatabase(tl_path, c, aad="aegis-timelines").read({})
        mv_path = data_dir / "movement.enc"
        if mv_path.exists():
            movement = SecureDatabase(mv_path, c, aad="aegis-movement").read({})
    except Exception:
        pass
    return evidence, autopsies, timelines, movement
