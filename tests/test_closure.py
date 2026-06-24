from rdflib import Graph, Dataset
from ontology.shacl_runner import run_shacl

def test_stub_judgments_have_rationale():
    ds = Dataset(); ds.parse("fixtures/graph-explorer-stub.trig", format="trig")
    data = Graph()
    for q in ds.quads((None, None, None, None)):
        data.add(q[:3])
    shapes = Graph(); shapes.parse("ontology/closure_shapes.ttl", format="turtle")
    assert run_shacl(data, shapes).conforms
