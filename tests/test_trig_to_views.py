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


def test_labels_are_human_readable_not_curies():
    # regression: data lives in named graphs; detail/label lookups must span them
    views = trig_to_views("fixtures/graph-explorer-stub.trig")
    claim = next(n for n in views["V1"] if n["type"] == "claim")
    assert "varies across districts" in claim["label"]
    assert claim["label"] != claim["id"]


def test_v3_judgment_detail_is_populated():
    # regression: the inspector (demo step 3) needs full judgment provenance
    views = trig_to_views("fixtures/graph-explorer-stub.trig")
    jd = views["V3"]["jd:demo-supported"]
    assert jd["decision"] and jd["chosen"] and jd["attributer"] and jd["rationale"]
    assert jd["earl_outcome"] == "passed"
