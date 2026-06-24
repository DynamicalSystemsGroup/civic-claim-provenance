from cli.views import shape_bindings

def test_v1_shaping():
    bindings = [{"id": {"value": "cl:x"}, "type": {"value": "claim"},
                 "label": {"value": "L"}, "verdict": {"value": "passed"}}]
    out = shape_bindings("V1", bindings)
    assert out == [{"id": "cl:x", "type": "claim", "label": "L", "verdict": "passed"}]

def test_v5_shaping_is_id_list():
    bindings = [{"id": {"value": "jd:a"}}, {"id": {"value": "am:b"}}]
    assert shape_bindings("V5", bindings) == ["jd:a", "am:b"]
