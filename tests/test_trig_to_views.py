from cli.trig_to_views import trig_to_views

def test_offline_build_matches_node_count():
    views = trig_to_views("fixtures/graph-explorer-stub.trig")
    ids = {n["id"] for n in views["V1"]}
    assert "cl:demo-variation" in ids and "jd:demo-denominator" in ids
    assert len(views["V1"]) == 6
    # claim inherits its governing judgment's verdict
    claim = next(n for n in views["V1"] if n["type"] == "claim")
    assert claim["verdict"] == "passed"
    # the deferred denominator judgment is cantTell
    assert any(n["verdict"] == "cantTell" for n in views["V1"])
    assert set(views["V5"]) == {"am:demo-denominator", "jd:demo-supported", "jd:demo-denominator"}
