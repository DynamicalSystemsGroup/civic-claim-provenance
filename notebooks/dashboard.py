# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo",
#   "networkx==3.6.1",
#   "matplotlib==3.11.0",
#   "pandas==3.0.3",
# ]
# ///
"""Civic Claim Provenance — graph explorer (Marimo, UI inspiration).

Reads the M->V cache (views/cache/V1..V5.json — the frozen interface contract)
and renders the chain of evidence two ways:

  * Graph tab — a NetworkX view of the argument: nodes COLORED BY TYPE
    (claim/evidence/assumption/judgment/attestation), SHADED BY VERDICT
    (passed/failed/cantTell/—), edges labeled by relation.
  * Judgments tab — the human judgments laid out in the `capture-template.md`
    shape (link/claim · evidence · decision · chosen · verdict · grounding ·
    attributer · rationale · depends-on). Every judgment explainable at a glance.

This binds to the cache SHAPES, never to Flexo or the ontology. Regenerate the
cache with `uv run ccp seed-offline` (or `ccp refresh`) — this notebook updates
with zero changes.

Run:  marimo run notebooks/dashboard.py   (from the repo root)
"""

import marimo

__generated_with = "0.23.10"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import json
    from pathlib import Path

    import marimo as mo
    import networkx as nx
    import pandas as pd
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt

    return Path, json, mo, mpatches, nx, pd, plt


@app.cell(hide_code=True)
def _(Path, json):
    # The cache is the M->V contract. This notebook lives in <root>/notebooks,
    # so the cache (<root>/views/cache) is one level up.
    CACHE_DIR = Path(__file__).resolve().parents[1] / "views" / "cache"

    def _load(name: str, default):
        path = CACHE_DIR / f"{name}.json"
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text())
        except (ValueError, OSError):
            return default

    v1_nodes = _load("V1", [])            # [{id, type, label, verdict}]
    v2_edges = _load("V2", [])            # [{src_id, dst_id, rel}]
    v3_detail = _load("V3", {})           # {id: per-type record}
    v4_rests_on = _load("V4", {})         # {id: [id, ...]}
    v5_judgments = _load("V5", [])        # [id, ...]
    cache_found = bool(v1_nodes)
    return CACHE_DIR, cache_found, v1_nodes, v2_edges, v3_detail, v5_judgments


@app.cell(hide_code=True)
def _(CACHE_DIR, cache_found, mo):
    if cache_found:
        header = mo.md(
            "# Civic Claim Provenance — graph explorer\n"
            "Assurance layer for a civic AI claim: the chain of evidence is "
            "inspectable, the human judgment stays authoritative."
        )
    else:
        header = mo.callout(
            mo.md(
                f"**No cache found at `{CACHE_DIR}`.** Generate it from the repo "
                "root with:\n\n"
                "```bash\nuv run ccp seed-offline --trig fixtures/graph-explorer-stub.trig\n```"
            ),
            kind="warn",
        )
    header
    return


@app.cell
def _(mo, v1_nodes):
    # Type / verdict palettes — the two visual encodings (color by type, shade
    # by verdict) that the production dashboard mirrors.
    TYPE_COLORS = {
        "claim": "#2563eb",        # blue
        "evidence": "#16a34a",     # green
        "assumption": "#f59e0b",   # amber
        "judgment": "#9333ea",     # purple
        "attestation": "#dc2626",  # red
    }
    VERDICT_ALPHA = {
        "passed": 1.0,
        "failed": 0.85,
        "cantTell": 0.55,
        "—": 0.30,
    }
    VERDICT_BORDER = {
        "passed": "#15803d",
        "failed": "#b91c1c",
        "cantTell": "#b45309",
        "—": "#9ca3af",
    }

    _types = sorted({n["type"] for n in v1_nodes}) or list(TYPE_COLORS)
    _verdicts = sorted({n["verdict"] for n in v1_nodes}) or list(VERDICT_ALPHA)
    type_filter = mo.ui.multiselect(
        options=_types, value=_types, label="Node types"
    )
    verdict_filter = mo.ui.multiselect(
        options=_verdicts, value=_verdicts, label="Verdicts"
    )
    return (
        TYPE_COLORS,
        VERDICT_ALPHA,
        VERDICT_BORDER,
        type_filter,
        verdict_filter,
    )


@app.cell
def _(
    TYPE_COLORS,
    VERDICT_ALPHA,
    VERDICT_BORDER,
    mpatches,
    nx,
    plt,
    type_filter,
    v1_nodes,
    v2_edges,
    verdict_filter,
):
    def build_graph_figure():
        keep_types = set(type_filter.value)
        keep_verdicts = set(verdict_filter.value)
        nodes = [
            n for n in v1_nodes
            if n["type"] in keep_types and n["verdict"] in keep_verdicts
        ]
        keep_ids = {n["id"] for n in nodes}

        graph = nx.DiGraph()
        for n in nodes:
            graph.add_node(n["id"], **n)
        for e in v2_edges:
            if e["src_id"] in keep_ids and e["dst_id"] in keep_ids:
                graph.add_edge(e["src_id"], e["dst_id"], rel=e["rel"])

        fig, ax = plt.subplots(figsize=(11, 7.5))
        if graph.number_of_nodes() == 0:
            ax.text(0.5, 0.5, "No nodes match the current filters",
                    ha="center", va="center", fontsize=13, color="#6b7280")
            ax.axis("off")
            return fig

        pos = nx.spring_layout(graph, seed=7, k=1.6)

        node_colors, edge_colors, line_widths = [], [], []
        for nid in graph.nodes():
            data = graph.nodes[nid]
            node_colors.append(TYPE_COLORS.get(data["type"], "#6b7280"))
            edge_colors.append(VERDICT_BORDER.get(data["verdict"], "#9ca3af"))
            line_widths.append(3.0 if data["verdict"] in ("passed", "failed") else 1.5)
        alphas = [VERDICT_ALPHA.get(graph.nodes[n]["verdict"], 0.5) for n in graph.nodes()]

        nx.draw_networkx_nodes(
            graph, pos, ax=ax, node_size=2400,
            node_color=node_colors, edgecolors=edge_colors,
            linewidths=line_widths, alpha=alphas,
        )
        nx.draw_networkx_edges(
            graph, pos, ax=ax, arrows=True, arrowsize=18,
            edge_color="#6b7280", width=1.4, node_size=2400,
            connectionstyle="arc3,rad=0.07",
        )
        nx.draw_networkx_labels(
            graph, pos, ax=ax,
            labels={n: n for n in graph.nodes()},
            font_size=7.5, font_color="white", font_weight="bold",
        )
        nx.draw_networkx_edge_labels(
            graph, pos, ax=ax,
            edge_labels=nx.get_edge_attributes(graph, "rel"),
            font_size=7, font_color="#374151",
            bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.8},
        )

        type_handles = [
            mpatches.Patch(color=c, label=t)
            for t, c in TYPE_COLORS.items() if t in keep_types
        ]
        leg1 = ax.legend(handles=type_handles, title="Type (fill)",
                         loc="upper left", fontsize=8, title_fontsize=8)
        ax.add_artist(leg1)
        verdict_handles = [
            mpatches.Patch(facecolor="#d1d5db", edgecolor=b, linewidth=2, label=v)
            for v, b in VERDICT_BORDER.items()
        ]
        ax.legend(handles=verdict_handles, title="Verdict (border)",
                  loc="upper right", fontsize=8, title_fontsize=8)
        ax.set_title("Chain of evidence", fontsize=12)
        ax.axis("off")
        fig.tight_layout()
        return fig

    graph_figure = build_graph_figure()
    return (graph_figure,)


@app.cell
def _(pd, v1_nodes, v2_edges, v3_detail, v5_judgments):
    # Reshape judgments into the `capture-template.md` columns. One row per
    # judgment: "I chose X because Y, on grounds Z."
    def _label(node_id: str) -> str:
        for n in v1_nodes:
            if n["id"] == node_id:
                return n["label"]
        return node_id

    def _depends_on(node_id: str) -> list[str]:
        return [e["dst_id"] for e in v2_edges
                if e["src_id"] == node_id and e["rel"] == "dependsOn"]

    rows = []
    for jid in v5_judgments:
        rec = v3_detail.get(jid, {})
        if rec.get("type") != "judgment":
            continue
        deps = _depends_on(jid)
        evidence = [d for d in deps if d.startswith("ev:")] or deps
        judged = rec.get("judges", "")
        rows.append({
            "link / claim": f"{judged} — {_label(judged)}" if judged else jid,
            "backing evidence": ", ".join(evidence) or "—",
            "decision": rec.get("decision", ""),
            "chosen": rec.get("chosen", ""),
            "verdict": rec.get("earl_outcome", ""),
            "grounding": rec.get("grounding", ""),
            "attributer": rec.get("attributer", ""),
            "rationale": rec.get("rationale", ""),
            "depends-on": ", ".join(deps) or "—",
        })

    judgments_df = pd.DataFrame(rows)
    return (judgments_df,)


@app.cell(hide_code=True)
def _(judgments_df, mo):
    if judgments_df.empty:
        judgments_view = mo.md("_No judgments in the cache (V5 is empty)._")
    else:
        judgments_view = mo.vstack([
            mo.md(
                "### Human judgments (`capture-template.md` shape)\n"
                "Every row is a logged decision — explainable at capture time."
            ),
            mo.ui.table(judgments_df, selection=None, pagination=True),
        ])
    # Built here but NOT displayed standalone — it is shown only inside the
    # "Judgments" tab below (avoids rendering the table twice).
    return (judgments_view,)


@app.cell
def _(graph_figure, judgments_view, mo, type_filter, verdict_filter):
    graph_tab = mo.vstack([
        mo.hstack([type_filter, verdict_filter], justify="start", gap=2),
        mo.as_html(graph_figure),
    ])
    tabs = mo.ui.tabs({
        "Graph": graph_tab,
        "Judgments": judgments_view,
    })
    tabs
    return


if __name__ == "__main__":
    app.run()
