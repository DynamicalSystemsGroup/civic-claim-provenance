from cli.trig_to_views import trig_to_views, trig_to_views_from_dataset

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


def test_dataset_projection_matches_file_projection():
    """trig_to_views_from_dataset on a pre-loaded Dataset must produce the same
    output as trig_to_views(path). Proves the shared core used by the live Flexo
    path is identical to the offline path — no separate projection logic to drift."""
    from rdflib import Dataset as RDFDataset
    path = "fixtures/graph-explorer-stub.trig"
    ds = RDFDataset()
    ds.parse(path, format="trig")

    from_file = trig_to_views(path)
    from_ds = trig_to_views_from_dataset(ds)

    key_v1 = lambda n: n["id"]
    key_v2 = lambda e: (e["src_id"], e["dst_id"], e["rel"])
    assert sorted(from_file["V1"], key=key_v1) == sorted(from_ds["V1"], key=key_v1)
    assert sorted(from_file["V2"], key=key_v2) == sorted(from_ds["V2"], key=key_v2)
    assert sorted(from_file["V5"]) == sorted(from_ds["V5"])
    assert from_file["V3"] == from_ds["V3"]
    assert from_file["V4"] == from_ds["V4"]
