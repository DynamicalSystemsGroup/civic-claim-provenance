"""Map SPARQL JSON bindings to the frozen view shapes (views/schema.json).
Also provides the live-path materialize() that fetches quads from Flexo and
runs the same projection as the offline path."""
from __future__ import annotations
from pathlib import Path
from rdflib import Dataset, URIRef, Literal, BNode
from cli.trig_to_views import trig_to_views_from_dataset

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


def _term(bv):
    """Convert a SPARQL JSON binding value dict to an rdflib term."""
    t, v = bv["type"], bv["value"]
    if t == "uri":
        return URIRef(v)
    if t == "bnode":
        return BNode(v)
    dt = bv.get("datatype")
    lang = bv.get("xml:lang")
    if lang:
        return Literal(v, lang=lang)
    if dt:
        return Literal(v, datatype=URIRef(dt))
    return Literal(v)


def _fetch_dataset(client, branch):
    """Fetch all named-graph quads from Flexo and return an rdflib Dataset.

    Uses a single SELECT over all named graphs so the resulting Dataset is
    structurally equivalent to parsing the source .trig file — enabling the
    shared trig_to_views_from_dataset() projection to run unchanged.
    """
    sparql = "SELECT ?g ?s ?p ?o WHERE { GRAPH ?g { ?s ?p ?o } }"
    rows = client.query(branch, sparql)["results"]["bindings"]
    ds = Dataset()
    for row in rows:
        ds.add((_term(row["s"]), URIRef(row["p"]["value"]), _term(row["o"]),
                URIRef(row["g"]["value"])))
    return ds


def materialize(client, branch):
    """Fetch the quadstore from Flexo and project it into the V1–V5 view dict.

    Delegates to trig_to_views_from_dataset() — the same function used by the
    offline `ccp seed-offline` path — so offline and live caches are guaranteed
    to be byte-for-shape identical.
    """
    return trig_to_views_from_dataset(_fetch_dataset(client, branch))
