from pathlib import Path
from rdflib import Graph, Dataset, URIRef, Literal
from ontology.shacl_runner import run_shacl, load_shapes

SHAPES = load_shapes(Path("ontology/closure_shapes.ttl"))
P = "urn:nyccompost:prop:"
EARL = "http://www.w3.org/ns/earl#"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"


def _flatten(trig_path: str) -> Graph:
    ds = Dataset()
    ds.parse(trig_path, format="trig")
    g = Graph()
    for q in ds.quads():
        g.add(q[:3])
    return g


def test_stub_passes_full_closure():
    result = run_shacl(_flatten("fixtures/graph-explorer-stub.trig"), SHAPES)
    assert result.conforms, f"stub failed closure: {[v.message for v in result.violations]}"


def test_malformed_judgment_fails():
    g = Graph()
    j = URIRef("urn:test:j1")
    g.add((j, URIRef(P + "chosen"), Literal("yes")))
    g.add((j, URIRef(P + "nodeType"), Literal("judgment")))
    g.add((j, URIRef(RDFS + "label"), Literal("test judgment")))
    g.add((j, URIRef(P + "decision"), Literal("something")))
    g.add((j, URIRef(P + "rationale"), Literal("because")))
    # deliberately omit: p:attributer, earl:outcome, p:judges
    result = run_shacl(g, SHAPES)
    assert not result.conforms
    messages = {v.message for v in result.violations}
    assert any("attributer" in m for m in messages)
    assert any("earl:outcome" in m or "outcome" in m for m in messages)
    assert any("judge" in m for m in messages)


def test_malformed_evidence_fails():
    g = Graph()
    e = URIRef("urn:test:e1")
    g.add((e, URIRef(P + "sourceId"), Literal("ebb7-mvp5")))
    g.add((e, URIRef(P + "nodeType"), Literal("evidence")))
    g.add((e, URIRef(RDFS + "label"), Literal("test evidence")))
    # deliberately omit: p:finding
    result = run_shacl(g, SHAPES)
    assert not result.conforms
    assert any("finding" in v.message for v in result.violations)
