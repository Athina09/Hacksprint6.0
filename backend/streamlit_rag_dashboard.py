"""
Evidence search accuracy — one chart for the selected case.

  streamlit run streamlit_rag_dashboard.py
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

import pandas as pd
import streamlit as st

from rag_eval import load_stores
from rag_metrics import DATA_DIR, get_eval_detail, refresh_metrics_cache
from rag_pipeline import retrieve_evidence
from seed_data import EVAL_CASES, EVIDENCE_INDEX


def _chart_label(meta: dict) -> str:
    return meta.get("chart") or meta.get("label", "Case")


def accuracy_chart_for_case(case_id: str) -> pd.DataFrame:
    ev = get_eval_detail(case_id, "evidence")
    label = _chart_label(EVAL_CASES[case_id])
    acc = round(ev.get("f1", 0) * 100, 1)
    return pd.DataFrame({"Accuracy %": [acc]}, index=[label])


st.set_page_config(page_title="Search accuracy", layout="wide")

if st.sidebar.button("Refresh metrics"):
    refresh_metrics_cache()
    st.rerun()

case_id = st.sidebar.selectbox(
    "Case",
    list(EVAL_CASES.keys()),
    format_func=lambda c: _chart_label(EVAL_CASES[c]),
)

ev = get_eval_detail(case_id, "evidence")
name = _chart_label(EVAL_CASES[case_id])

st.title("Evidence search accuracy")
st.caption(f"{case_id} · {ev.get('queries', 0)} test searches")

st.bar_chart(accuracy_chart_for_case(case_id))

if ev.get("note"):
    st.info(ev["note"])

st.divider()
query = st.text_input("Try a search", placeholder="e.g. mooring hook CCTV")
if query:
    evidence, _, _, _ = load_stores(DATA_DIR)
    if not evidence:
        evidence = EVIDENCE_INDEX
    out = retrieve_evidence(evidence, query, n_results=5, case_id=case_id)
    if not out["results"]:
        st.caption("No matches.")
    for r in out["results"]:
        st.text(r["document"])
