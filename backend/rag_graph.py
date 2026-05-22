"""Plotly figures for RAG pipeline visualization."""

from __future__ import annotations

import math
from typing import Any

import plotly.graph_objects as go

from rag_pipeline import DOMAIN_USES, RAG_FLOW

_STATUS = {
    "live": {"fill": "#22c55e", "line": "#15803d", "name": "Live"},
    "planned": {"fill": "#475569", "line": "#94a3b8", "name": "Planned"},
    "demo": {"fill": "#38bdf8", "line": "#0284c7", "name": "Demo"},
}

_SHORT = {
    "ingest": "Ingest",
    "chunk": "Chunk",
    "embed": "Embed",
    "retrieve": "Retrieve",
    "rerank": "Rerank",
    "generate": "Generate",
    "validate": "Validate",
}


def _dark_layout(fig: go.Figure, height: int, x_max: float = 6.5) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font=dict(color="#e2e8f0", size=12),
        margin=dict(l=24, r=24, t=48, b=24),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    fig.update_xaxes(visible=False, range=[-0.8, x_max])
    fig.update_yaxes(visible=False, range=[-0.35, 0.55])
    return fig


def pipeline_flow_figure(steps: list[dict[str, Any]] | None = None) -> go.Figure:
    """Horizontal pipeline graph: nodes + directed edges."""
    steps = steps or RAG_FLOW
    n = len(steps)
    xs = list(range(n))
    ys = [0.0] * n

    fig = go.Figure()

    for i in range(n - 1):
        fig.add_trace(
            go.Scatter(
                x=[xs[i], xs[i + 1]],
                y=[0, 0],
                mode="lines",
                line=dict(color="#64748b", width=4),
                hoverinfo="skip",
                showlegend=False,
            )
        )
        fig.add_annotation(
            x=(xs[i] + xs[i + 1]) / 2,
            y=0.02,
            text="▶",
            showarrow=False,
            font=dict(color="#94a3b8", size=14),
        )

    for status, style in _STATUS.items():
        idx = [i for i, s in enumerate(steps) if s["status"] == status]
        if not idx:
            continue
        hover = [
            f"<b>{_SHORT.get(steps[i]['id'], steps[i]['id'])}</b><br>"
            f"Status: {steps[i]['status']}<br>{steps[i]['detail']}"
            for i in idx
        ]
        fig.add_trace(
            go.Scatter(
                x=[xs[i] for i in idx],
                y=[ys[i] for i in idx],
                mode="markers+text",
                name=style["name"],
                marker=dict(
                    size=56,
                    color=style["fill"],
                    line=dict(width=3, color=style["line"]),
                ),
                text=[_SHORT.get(steps[i]["id"], steps[i]["id"]) for i in idx],
                textposition="middle center",
                textfont=dict(size=11, color="#0f172a", family="Arial Black"),
                hovertext=hover,
                hoverinfo="text",
            )
        )

    stores = (
        "autopsies.enc · evidence.enc<br>timelines.enc · movement.enc"
    )
    fig.add_annotation(
        x=-0.55,
        y=0.38,
        text=f"<b>Encrypted stores</b><br>{stores}",
        showarrow=False,
        align="left",
        font=dict(size=10, color="#94a3b8"),
        bgcolor="rgba(15,23,42,0.9)",
        bordercolor="#334155",
        borderwidth=1,
    )
    fig.add_annotation(
        x=n - 0.45,
        y=0.38,
        text="<b>Consumers</b><br>React Copilot · Case UI",
        showarrow=False,
        align="right",
        font=dict(size=10, color="#94a3b8"),
        bgcolor="rgba(15,23,42,0.9)",
        bordercolor="#334155",
        borderwidth=1,
    )

    return _dark_layout(fig, height=320, x_max=n - 0.3)


def domains_hub_figure(domains: list[dict[str, str]] | None = None) -> go.Figure:
    """Domains feed into retrieve (live) and generate (planned)."""
    domains = domains or DOMAIN_USES
    fig = go.Figure()

    hub = {"retrieve": (0, 0), "generate": (2.2, 0), "validate": (4.2, 0)}
    for key, (x, y) in hub.items():
        step = next((s for s in RAG_FLOW if s["id"] == key), None)
        status = step["status"] if step else "planned"
        st = _STATUS[status]
        fig.add_trace(
            go.Scatter(
                x=[x],
                y=[y],
                mode="markers+text",
                name=st["name"] if key == "retrieve" else None,
                showlegend=key == "retrieve",
                marker=dict(size=48, color=st["fill"], line=dict(width=2, color=st["line"])),
                text=[key.capitalize()],
                textposition="middle center",
                textfont=dict(size=10, color="#0f172a"),
                hovertext=step["detail"] if step else key,
                hoverinfo="text",
            )
        )

    fig.add_trace(
        go.Scatter(
            x=[hub["retrieve"][0], hub["generate"][0], hub["validate"][0]],
            y=[0, 0, 0],
            mode="lines",
            line=dict(color="#64748b", width=3),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    n = len(domains)
    for i, d in enumerate(domains):
        angle = (i / max(n - 1, 1)) * 3.14159 - 1.5708
        x = 0 + 1.35 * math.cos(angle)
        y = 0.85 + 0.55 * math.sin(angle)
        live = d["domain"] == "evidence"
        color = "#22c55e" if live else "#334155"
        fig.add_trace(
            go.Scatter(
                x=[x, hub["retrieve"][0]],
                y=[y, hub["retrieve"][1]],
                mode="lines",
                line=dict(color=color, width=2, dash="solid" if live else "dot"),
                hoverinfo="skip",
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[x],
                y=[y],
                mode="markers+text",
                marker=dict(size=28, color=color, line=dict(width=1, color="#94a3b8")),
                text=[d["domain"]],
                textposition="top center",
                textfont=dict(size=9, color="#e2e8f0"),
                hovertext=d["use"],
                hoverinfo="text",
                showlegend=False,
            )
        )

    fig.add_annotation(
        x=0,
        y=-0.42,
        text="Evidence domain → live /api/search · others → planned LLM path",
        showarrow=False,
        font=dict(size=10, color="#94a3b8"),
    )

    fig.update_layout(
        height=380,
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font=dict(color="#e2e8f0"),
        margin=dict(l=20, r=20, t=40, b=40),
        showlegend=False,
    )
    fig.update_xaxes(visible=False, range=[-2, 5])
    fig.update_yaxes(visible=False, range=[-0.55, 1.35])
    return fig


def retrieval_sankey_figure(
    chunks_scanned: int,
    chunks_matched: int,
    chunks_returned: int,
    query: str,
) -> go.Figure:
    """Sankey for one search: query → index → matches → context."""
    labels = [
        f"Query",
        f"Index ({chunks_scanned} chunks)",
        f"Matched ({chunks_matched})",
        f"Context ({chunks_returned})",
    ]
    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                node=dict(
                    pad=20,
                    thickness=22,
                    label=labels,
                    color=["#38bdf8", "#475569", "#eab308", "#22c55e"],
                ),
                link=dict(
                    source=[0, 1, 2],
                    target=[1, 2, 3],
                    value=[
                        max(chunks_scanned, 1),
                        max(chunks_matched, 1),
                        max(chunks_returned, 1),
                    ],
                    color=["rgba(56,189,248,0.4)", "rgba(234,179,8,0.4)", "rgba(34,197,94,0.5)"],
                ),
            )
        ]
    )
    fig.update_layout(
        title=dict(text=f"Retrieval flow · “{query[:40]}”", font=dict(size=14, color="#e2e8f0")),
        height=280,
        paper_bgcolor="#0f172a",
        font=dict(color="#e2e8f0"),
        margin=dict(l=16, r=16, t=48, b=16),
    )
    return fig
