from cli.flexo_client import FlexoClient

def test_endpoint_addressing():
    c = FlexoClient("http://localhost:8080", "civic", "composting", token="t")
    assert c._branch_url("main", "query") == \
        "http://localhost:8080/orgs/civic/repos/composting/branches/main/query"

def test_headers_carry_bearer():
    c = FlexoClient("http://x", "o", "r", token="abc")
    h = c._headers("application/sparql-query")
    assert h["Authorization"] == "Bearer abc"
    assert h["Content-Type"] == "application/sparql-query"
