"""Map SPARQL JSON bindings to the frozen view shapes (views/schema.json)."""
from __future__ import annotations
from pathlib import Path

VIEW_NAMES = ["V1", "V2", "V3", "V4", "V5"]
QUERY_DIR = Path(__file__).resolve().parent.parent / "views" / "queries"

def _val(binding, key, default=None):
    return binding[key]["value"] if key in binding else default

def shape_bindings(name, bindings):
    if name == "V1":
        return [{"id": _val(b, "id"), "type": _val(b, "type"),
                 "label": _val(b, "label"), "verdict": _val(b, "verdict", "—")} for b in bindings]
    if name == "V2":
        return [{"src_id": _val(b, "src_id"), "dst_id": _val(b, "dst_id"), "rel": _val(b, "rel")} for b in bindings]
    if name == "V5":
        return [_val(b, "id") for b in bindings]
    raise ValueError(f"{name} is assembled in Python, not from raw bindings")

def rests_on(edges):
    """V4: transitive closure of judges/dependsOn/supports per source node."""
    adj = {}
    for e in edges:
        if e["rel"] in ("judges", "dependsOn", "supports", "attestsOver"):
            adj.setdefault(e["src_id"], []).append(e["dst_id"])
    out = {}
    for start in adj:
        seen, stack = [], list(adj.get(start, []))
        while stack:
            n = stack.pop()
            if n not in seen:
                seen.append(n)
                stack.extend(adj.get(n, []))
        out[start] = seen
    return out

def materialize(client, branch):
    """Run SPARQL views against Flexo, assemble V1–V5 dict. V3 from node props is
    layered in by cli.trig_to_views for offline; for Flexo we query node props per id."""
    result = {}
    for name in ("V1", "V2", "V5"):
        sparql = (QUERY_DIR / f"{name}.rq").read_text()
        result[name] = shape_bindings(name, client.query(branch, sparql)["results"]["bindings"])
    result["V4"] = rests_on(result["V2"])
    result["V3"] = {}  # populated by a node-detail pass (out of smoke-test scope tonight)
    return result
