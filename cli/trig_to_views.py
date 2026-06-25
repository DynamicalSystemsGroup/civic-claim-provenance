"""Offline .trig → V1–V5 views via rdflib. No Flexo. Output shapes are identical
to the Flexo-materialized cache (views/schema.json)."""
from __future__ import annotations
from rdflib import Dataset, RDFS, URIRef
from cli.curie import _curie

P = "urn:nyccompost:prop:"
EDGE_RELS = ["supports", "judges", "dependsOn", "assumes", "attestsOver"]
DETAIL_PROPS = {
    "claim": [("statement", "statement"), ("status", "_status")],
    "evidence": [("sourceId", "source_id"), ("sourceVersion", "source_version"),
                 ("queryUrl", "query_url"), ("finding", "finding"), ("payloadSha256", "payload_sha256")],
    "assumption": [("statement", "statement")],
    "judgment": [("judges", "judges"), ("decision", "decision"), ("chosen", "chosen"),
                 ("rationale", "grounding"), ("attributer", "attributer"), ("rationale", "rationale"),
                 ("pinnedAsOf", "pinned_as_of")],
    "attestation": [("attester", "attester"), ("orgAuspice", "org_auspice"),
                    ("signedAt", "signed_at"), ("attestsOver", "attests_over")],
}


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


def _prop(ds, node, name):
    # ds.value() only reads the default graph; the data lives in named graphs,
    # so query across all graphs via quads().
    q = list(ds.quads((node, URIRef(P + name), None, None)))
    return str(q[0][2]) if q else None


def trig_to_views_from_dataset(ds):
    """Project an rdflib Dataset into the V1–V5 view dict.

    Shared by the offline path (Dataset parsed from a .trig file) and the live
    path (Dataset reconstructed from Flexo quads). One code path = guaranteed
    shape parity between `ccp seed-offline` and `ccp refresh`.
    """
    nodes, edges, details = [], [], {}
    typed = {s: str(o) for s, _, o, _ in ds.quads((None, URIRef(P + "nodeType"), None, None))}
    EARL = URIRef("http://www.w3.org/ns/earl#outcome")
    own_verdict = {}
    for s, _, o, _ in ds.quads((None, EARL, None, None)):
        own_verdict[s] = str(o).rsplit("#", 1)[-1].rsplit("/", 1)[-1]
    gov_verdict = {}
    for s, _, o, _ in ds.quads((None, URIRef(P + "judges"), None, None)):
        if s in own_verdict:
            gov_verdict[o] = own_verdict[s]
    for node, ntype in typed.items():
        verdict = own_verdict.get(node) or gov_verdict.get(node) or "—"
        nid = _curie(node)
        lq = list(ds.quads((node, RDFS.label, None, None)))
        label = lq[0][2] if lq else None
        nodes.append({"id": nid, "type": ntype, "label": str(label) if label else nid, "verdict": verdict})
        det = {"type": ntype}
        for src, dst in DETAIL_PROPS.get(ntype, []):
            val = _prop(ds, node, src)
            if val is not None:
                det[dst] = _curie(URIRef(val)) if src in ("judges", "attestsOver") else val
        if ntype == "claim":
            det["statement"] = _prop(ds, node, "statement")
            det["status"] = verdict
        if ntype == "judgment":
            det["earl_outcome"] = verdict
        details[nid] = det
    for rel in EDGE_RELS:
        for s, _, o, _ in ds.quads((None, URIRef(P + rel), None, None)):
            edges.append({"src_id": _curie(s), "dst_id": _curie(o), "rel": rel})
    judgments_only = [n["id"] for n in nodes if n["type"] in ("assumption", "judgment")]
    return {"V1": nodes, "V2": edges, "V3": details, "V4": rests_on(edges), "V5": judgments_only}


def trig_to_views(trig_path):
    ds = Dataset()
    ds.parse(trig_path, format="trig")
    return trig_to_views_from_dataset(ds)
