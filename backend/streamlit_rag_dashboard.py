"""
AEGIS RAG pipeline overview (Streamlit demo)

  cd backend && source .venv/bin/activate
  streamlit run streamlit_rag_dashboard.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

import pandas as pd
import streamlit as st

from rag_metrics import PIPELINES, get_all_metrics, get_pipeline, search_rag_meta
from seed_data import EVIDENCE_INDEX

DOMAINS = list(PIPELINES.keys())
DOMAIN_LABELS = {
    "autopsy": "Autopsy",
    "tod": "TOD",
    "pmi": "PMI",
    "timeline": "Timeline",
    "evidence": "Evidence",
    "hypothesis": "Hypothesis",
    "movement": "Movement",
}

st.set_page_config(page_title="AEGIS pipelines", layout="wide")

st.title("RAG pipeline overview")
st.caption("Demo metrics for the hackathon stack. Not live model scores.")

case_id = st.sidebar.selectbox("Case", ["C-2041", "C-2042", "C-2043"], index=0)
metrics = get_all_metrics(case_id)
st.sidebar.markdown(f"**{metrics['indexed_chunks']:,}** chunks indexed")
st.sidebar.caption(f"{metrics['embedding_model']} · {metrics['reranker']}")

c1, c2 = st.columns(2)
c1.metric("Mean accuracy (domains)", f"{metrics['aggregate_accuracy'] * 100:.0f}%")
c2.metric("Pipelines", len(DOMAINS))

chart_df = pd.DataFrame(
    {
        "domain": [DOMAIN_LABELS.get(d["domain"], d["domain"]) for d in metrics["domains"]],
        "accuracy %": [d["overall_accuracy"] * 100 for d in metrics["domains"]],
    }
).set_index("domain")
st.bar_chart(chart_df)

st.subheader("Pipelines")
tab_labels = [DOMAIN_LABELS.get(d, d) for d in DOMAINS]
tabs = st.tabs(tab_labels)

for tab, domain in zip(tabs, DOMAINS):
    with tab:
        p = get_pipeline(domain, case_id)
        st.write(f"**{p['label']}** — `{p['model']}`")
        a, b = st.columns(2)
        a.metric("Accuracy", f"{p['overall_accuracy'] * 100:.0f}%")
        b.metric("Confidence", f"{p['model_confidence'] * 100:.0f}%")

        stages_df = pd.DataFrame(
            [
                {
                    "stage": s["label"],
                    "score": f"{s['score'] * 100:.0f}%",
                    "ms": s["latency_ms"],
                }
                for s in p["stages"]
            ]
        )
        st.dataframe(stages_df, use_container_width=True, hide_index=True)

        if p.get("outputs"):
            out_df = pd.DataFrame(
                [
                    {
                        "field": o["label"],
                        "value": o.get("value", ""),
                        "conf": f"{o['confidence'] * 100:.0f}%",
                    }
                    for o in p["outputs"]
                ]
            )
            st.dataframe(out_df, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Evidence search (demo)")
query = st.text_input("Query", value="DNA suspect", label_visibility="collapsed")
if st.button("Search", type="primary") or query:
    tokens = set(re.findall(r"\w+", query.lower()))
    hits = 0
    case_filter = st.sidebar.checkbox("Only this case", value=True)
    for item in EVIDENCE_INDEX:
        meta = item.get("metadata", {})
        if case_filter and meta.get("case_id") != case_id:
            continue
        text = (item.get("document", "") + str(meta)).lower()
        if any(t in text for t in tokens):
            hits += 1
    rag = search_rag_meta(query, 5, min(hits, 5))
    st.write(f"**{hits}** matching docs · **{rag['chunks_used']}** used in context")
    with st.expander("Retrieval details"):
        st.json(rag)
