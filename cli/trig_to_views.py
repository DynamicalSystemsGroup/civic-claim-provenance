"""Offline .trig → V1–V5 views via rdflib. No Flexo. Output shapes are identical
to the Flexo-materialized cache (views/schema.json)."""
from __future__ import annotations
from rdflib import Dataset, RDFS, URIRef
from cli.views import rests_on

P = "urn:nyccompost:prop:"
PREFIXES = {
    "urn:nyccompost:claim:": "cl:", "urn:nyccompost:evidence:": "ev:",
    "urn:nyccompost:assumption:": "am:", "urn:nyccompost:judgment:": "jd:",
    "urn:nyccompost:attestation:": "at:",
}
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

def _curie(uri):
    s = str(uri)
    for full, short in PREFIXES.items():
        if s.startswith(full):
            return short + s[len(full):]
    return s

def _prop(ds, node, name):
    v = ds.value(node, URIRef(P + name))
    return str(v) if v is not None else None

def trig_to_views(trig_path):
    ds = Dataset()
    ds.parse(trig_path, format="trig")
    nodes, edges, details = [], [], {}
    # collect typed nodes
    typed = {s: str(o) for s, _, o, _ in ds.quads((None, URIRef(P + "nodeType"), None, None))}
    # verdict on judgment nodes (earl:outcome localname)
    EARL = URIRef("http://www.w3.org/ns/earl#outcome")
    own_verdict = {}
    for s, _, o, _ in ds.quads((None, EARL, None, None)):
        own_verdict[s] = str(o).rsplit("#", 1)[-1].rsplit("/", 1)[-1]
    # governing judgment verdict for claims/assumptions it judges
    gov_verdict = {}
    for s, _, o, _ in ds.quads((None, URIRef(P + "judges"), None, None)):
        if s in own_verdict:
            gov_verdict[o] = own_verdict[s]
    for node, ntype in typed.items():
        verdict = own_verdict.get(node) or gov_verdict.get(node) or "—"
        nid = _curie(node)
        label = ds.value(node, RDFS.label)
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
