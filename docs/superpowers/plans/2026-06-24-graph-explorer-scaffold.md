# Graph Explorer Scaffold Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up a graph-explorer dashboard rendering the NYC composting claim's provenance graph (V1–V5 views), fed by a JSON cache that is materialized from Flexo via SPARQL but read directly by the demo.

**Architecture:** A frozen `views/schema.json` + a committed seed `views/cache/*.json` are the contract everyone binds to. Track A (Z) builds the Python CLI + Flexo client + SPARQL views + dashboard backend. Track B (Joshua) builds the Vite/React/Cytoscape UI against the cache. Track C (Christine) gets a capture template + load path. All three run concurrently after Task 0.

**Tech Stack:** Python 3.12 + uv (typer, httpx, rdflib, fastapi, uvicorn, pyshacl); Vite + React + TypeScript + Cytoscape.js; Flexo MMS Layer-1 (remote `try-layer1.starforge.app` default).

## Global Constraints

- **Demo reads the cache, never live Flexo.** Flexo is upstream of the cache only.
- **V1–V5 column names + value domains are FROZEN** per interface-contract A4 (see `views/schema.json`). New fields additive only — never rename/retype.
- **Node `id` is an opaque string** (e.g. `"cl:demo-variation"`); type comes from the `type` field, never inferred from prefix.
- **Verdict domain:** `passed | failed | cantTell | —` (em-dash literal for evidence/assumption).
- **Node types:** `claim | evidence | assumption | judgment | attestation`. **Edge rels:** `supports | judges | dependsOn | assumes | attestsOver`.
- **Testing is downscoped to smoke-tests** (per spec §2) — one happy-path test per Python module; UI verified via preview, not unit tests.
- **Python deps via uv only.** Commit frequently. Reuse existing DSG code (cite source in commit msg) over writing new.

---

## File Structure

```
civic-claim-provenance/
  pyproject.toml                  # uv project: cli + server + ontology
  views/
    schema.json                   # FROZEN V1–V5 shapes (Task 0)
    cache/{V1..V5}.json           # seed cache, hand-derived then regen'd (Task 0 / A3)
    queries/{V1..V5}.rq           # SPARQL (Task A2)
  cli/
    __init__.py
    flexo_client.py               # login/put/update/query (Task A1)
    trig_to_views.py              # .trig → cache via rdflib (Task A3)
    views.py                      # SPARQL rows → schema-shaped dicts (Task A2)
    ccp.py                        # typer app: load/refresh/seed-offline/serve (Task A3)
  server/
    __init__.py
    app.py                        # FastAPI: GET /views/{n}.json, POST /refresh (Task A4)
  flexo/{init.sh, .env.example, README.md}   # (Task A5)
  ontology/{shacl_runner.py, rdf_utils.py, closure_shapes.ttl}   # (Task A6)
  fixtures/graph-explorer-stub.trig          # (Task 0, copied)
  fixtures/capture-template.md               # (Task C1)
  ui/                             # Vite/React/TS (Task B1+)
    src/data/views.ts             # fetch layer (Task B1)
    src/graph/Graph.tsx           # Cytoscape (Task B2)
    src/inspector/Inspector.tsx   # V3 (Task B3)
    src/filters/Filters.tsx       # V5/V4 (Task B4)
    src/App.tsx                   # layout (Task B5)
  docs/                           # 5 memos + spec (Task 0, copied)
  tests/                          # pytest smoke tests
```

---

### Task 0: Contract freeze + repo skeleton (CRITICAL PATH — blocks all tracks)

**Files:**
- Create: `pyproject.toml`, `views/schema.json`, `views/cache/V1.json`…`V5.json`, `README.md`
- Copy: starter memos → `docs/`, `graph-explorer-stub.trig` → `fixtures/`

**Interfaces:**
- Produces: `views/schema.json` (the binding contract) and `views/cache/*.json` (seed data of the exact shapes Tracks A & B consume).

- [ ] **Step 1: Copy starter assets into the repo**

```bash
cd /Users/z/Documents/GitHub/civic-claim-provenance
KIT=/Users/z/Downloads/hackathon-prep
mkdir -p docs fixtures views/cache views/queries cli server tests ontology flexo
cp "$KIT"/{README.md,hackathon-project-memo.md,policy-analysis-and-data-assessment.md,ontology-and-doctrine.md,interface-contracts.md,work-packages-memo.md,cowork-data-verification-task.md} docs/
cp "$KIT"/graph-explorer-stub.trig fixtures/
```

- [ ] **Step 2: Write `views/schema.json` (the frozen contract)**

```json
{
  "version": "0.1",
  "frozen": "interface-contracts.md A4",
  "node_types": ["claim", "evidence", "assumption", "judgment", "attestation"],
  "edge_rels": ["supports", "judges", "dependsOn", "assumes", "attestsOver"],
  "verdicts": ["passed", "failed", "cantTell", "—"],
  "views": {
    "V1": {"file": "cache/V1.json", "shape": "array", "columns": ["id", "type", "label", "verdict"]},
    "V2": {"file": "cache/V2.json", "shape": "array", "columns": ["src_id", "dst_id", "rel"]},
    "V3": {"file": "cache/V3.json", "shape": "map_by_id", "by_type": {
      "claim": ["statement", "status"],
      "evidence": ["source_id", "source_version", "query_url", "finding", "retrieved_at", "payload_sha256"],
      "assumption": ["statement"],
      "judgment": ["judges", "decision", "chosen", "grounding", "attributer", "rationale", "earl_outcome", "pinned_as_of"],
      "attestation": ["attester", "org_auspice", "signed_at", "attests_over"]
    }},
    "V4": {"file": "cache/V4.json", "shape": "map_by_id", "value": "array_of_id", "stretch": true},
    "V5": {"file": "cache/V5.json", "shape": "array_of_id"}
  }
}
```

- [ ] **Step 3: Write the seed cache (hand-derived from `graph-explorer-stub.trig`)**

`views/cache/V1.json`:
```json
[
  {"id": "cl:demo-variation", "type": "claim", "label": "Residential-organics tonnage per capita varies across districts", "verdict": "passed"},
  {"id": "am:demo-denominator", "type": "assumption", "label": "Per-capita denominator choice", "verdict": "—"},
  {"id": "jd:demo-supported", "type": "judgment", "label": "Variation is describable from the data", "verdict": "passed"},
  {"id": "jd:demo-denominator", "type": "judgment", "label": "Denominator is a deferred human judgment", "verdict": "cantTell"},
  {"id": "ev:demo-tonnage", "type": "evidence", "label": "Per-district residential-organics tonnage, CY2025", "verdict": "—"},
  {"id": "at:demo-signoff", "type": "attestation", "label": "Sign-off over the variation finding", "verdict": "—"}
]
```

`views/cache/V2.json`:
```json
[
  {"src_id": "ev:demo-tonnage", "dst_id": "cl:demo-variation", "rel": "supports"},
  {"src_id": "jd:demo-supported", "dst_id": "cl:demo-variation", "rel": "judges"},
  {"src_id": "jd:demo-supported", "dst_id": "ev:demo-tonnage", "rel": "dependsOn"},
  {"src_id": "jd:demo-denominator", "dst_id": "am:demo-denominator", "rel": "judges"},
  {"src_id": "jd:demo-denominator", "dst_id": "am:demo-denominator", "rel": "dependsOn"},
  {"src_id": "cl:demo-variation", "dst_id": "am:demo-denominator", "rel": "assumes"},
  {"src_id": "at:demo-signoff", "dst_id": "cl:demo-variation", "rel": "attestsOver"}
]
```

`views/cache/V3.json`:
```json
{
  "cl:demo-variation": {"type": "claim", "statement": "Per-district CY2025 residential-organics tonnage per capita is not uniform.", "status": "passed"},
  "am:demo-denominator": {"type": "assumption", "statement": "Denominator = 2010 CD-native population (placeholder; stale)."},
  "jd:demo-supported": {"type": "judgment", "judges": "cl:demo-variation", "decision": "Is per-district CY2025 tonnage describable?", "chosen": "supported", "grounding": "Complete series, 708 = 59x12, zero missing.", "attributer": "A. Analyst", "rationale": "Complete series, 708 = 59x12, zero missing (synthetic mirror).", "earl_outcome": "passed", "pinned_as_of": "2026-06-01"},
  "jd:demo-denominator": {"type": "judgment", "judges": "am:demo-denominator", "decision": "Which population denominator?", "chosen": "deferred - needs human judgment", "grounding": "Normative choice; data cannot pick.", "attributer": "A. Analyst", "rationale": "Currency vs CD-native cleanliness; normative, data cannot pick.", "earl_outcome": "cantTell", "pinned_as_of": ""},
  "ev:demo-tonnage": {"type": "evidence", "source_id": "ebb7-mvp5", "source_version": "2026-06-01", "query_url": "https://example.invalid/synthetic-query", "finding": "Synthetic per-district tonnage series.", "retrieved_at": "2026-06-24T19:10:00Z", "payload_sha256": "0000000000000000000000000000000000000000000000000000000000000000"},
  "at:demo-signoff": {"type": "attestation", "attester": "Jane Official", "org_auspice": "NYC DSNY (synthetic)", "signed_at": "2026-06-24T20:00:00Z", "attests_over": "cl:demo-variation"}
}
```

`views/cache/V5.json`:
```json
["am:demo-denominator", "jd:demo-supported", "jd:demo-denominator"]
```

`views/cache/V4.json`:
```json
{"at:demo-signoff": ["cl:demo-variation", "ev:demo-tonnage", "am:demo-denominator", "jd:demo-supported", "jd:demo-denominator"]}
```

- [ ] **Step 4: Write `pyproject.toml`**

```toml
[project]
name = "civic-claim-provenance"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "typer>=0.12,<1.0",
  "httpx>=0.28",
  "rdflib>=7.0",
  "fastapi>=0.110",
  "uvicorn>=0.29",
  "pyshacl>=0.31",
]

[project.scripts]
ccp = "cli.ccp:app"

[dependency-groups]
dev = ["pytest>=8.0"]
```

- [ ] **Step 5: Write `README.md` skeleton** (who-owns-what + quickstart)

```markdown
# Civic Claim Provenance — Graph Explorer

Assurance layer for civic AI: make one government claim's chain of evidence
inspectable, keep the human judgment authoritative. Demo = the graph explorer.

## Pipeline
`.trig → ccp load → Flexo → SPARQL → ccp refresh → views/cache/*.json → ccp serve → ui/`
The demo reads the cache. Flexo is upstream of the cache only.

## Quickstart (no Flexo needed)
```bash
uv sync
uv run ccp seed-offline fixtures/graph-explorer-stub.trig   # regenerate cache
uv run ccp serve                                            # backend on :8000
cd ui && npm install && npm run dev                         # dashboard on :5173
```

## Ownership
- `cli/`, `server/`, `views/queries/`, `ontology/`, `flexo/` — Z (backend, schema, closure)
- `ui/` — Joshua (dashboard)
- `fixtures/`, capture template — Christine (content)
```

- [ ] **Step 6: Verify the seed cache is valid JSON and commit**

Run: `python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('views/**/*.json', recursive=True)]; print('all cache JSON valid')"`
Expected: `all cache JSON valid`

```bash
git add -A
git commit -m "Task 0: freeze schema.json + seed cache from stub; repo skeleton"
```

---

## TRACK A — Backend & pipeline (Z). Tasks A1–A6 run after Task 0.

### Task A1: Flexo Layer-1 client

**Files:**
- Create: `cli/__init__.py` (empty), `cli/flexo_client.py`, `tests/test_flexo_client.py`

**Interfaces:**
- Produces: `class FlexoClient` with `__init__(self, base_url, org, repo, token=None, auth_url=None, user=None, password=None)`; methods `login() -> str`, `put_turtle(path, body) -> int`, `update(branch, sparql) -> int`, `query(branch, sparql) -> dict` (returns SPARQL JSON `{"results":{"bindings":[...]}}`). Consumed by `cli/views.py` (A2) and `cli/ccp.py` (A3).

- [ ] **Step 1: Write the smoke test** (pure construction + header building, no network)

```python
# tests/test_flexo_client.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_flexo_client.py -v`
Expected: FAIL (ModuleNotFoundError / no FlexoClient)

- [ ] **Step 3: Implement `cli/flexo_client.py`** (adapted from `ADCS-lifecycle-demo/pipeline/backends/flexo.py` + `experiment-1/run.sh`)

```python
"""Flexo MMS Layer-1 client. Adapted from ADCS-lifecycle-demo backends/flexo.py
and flexo-conflict-resolution-policy-research experiment-1/run.sh."""
from __future__ import annotations
import httpx

class FlexoClient:
    def __init__(self, base_url, org, repo, token=None, auth_url=None,
                 user="user01", password="password1", timeout=180):
        self.base = base_url.rstrip("/")
        self.org, self.repo = org, repo
        self.token = token
        self.auth_url = (auth_url or "").rstrip("/")
        self.user, self.password = user, password
        self.timeout = timeout

    def _branch_url(self, branch, verb):
        return f"{self.base}/orgs/{self.org}/repos/{self.repo}/branches/{branch}/{verb}"

    def _headers(self, content_type=None, accept=None):
        h = {"Authorization": f"Bearer {self.token}"}
        if content_type:
            h["Content-Type"] = content_type
        if accept:
            h["Accept"] = accept
        return h

    def login(self) -> str:
        # Remote uses a pre-issued token; local stack issues one via auth /login.
        if self.token:
            return self.token
        r = httpx.get(f"{self.auth_url}/login", auth=(self.user, self.password), timeout=30)
        r.raise_for_status()
        self.token = r.json()["token"]
        return self.token

    def put_turtle(self, url, body) -> int:
        r = httpx.put(url, headers=self._headers("text/turtle"), content=body, timeout=self.timeout)
        return r.status_code  # caller treats 2xx or 409 (exists) as OK

    def update(self, branch, sparql) -> int:
        r = httpx.post(self._branch_url(branch, "update"),
                       headers=self._headers("application/sparql-update"),
                       content=sparql, timeout=self.timeout)
        r.raise_for_status()
        return r.status_code

    def query(self, branch, sparql) -> dict:
        r = httpx.post(self._branch_url(branch, "query"),
                       headers=self._headers("application/sparql-query", "application/json"),
                       content=sparql, timeout=self.timeout)
        r.raise_for_status()
        return r.json()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_flexo_client.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add cli/__init__.py cli/flexo_client.py tests/test_flexo_client.py
git commit -m "Task A1: Flexo Layer-1 client (reused from ADCS + experiment-1)"
```

---

### Task A2: SPARQL views + row-shaping

**Files:**
- Create: `views/queries/V1.rq`…`V5.rq`, `cli/views.py`, `tests/test_views.py`

**Interfaces:**
- Consumes: `FlexoClient.query` (A1).
- Produces: `VIEW_NAMES = ["V1","V2","V3","V4","V5"]`; `shape_bindings(name, bindings) -> object` mapping SPARQL JSON bindings to the schema shape; `materialize(client, branch) -> dict[str, object]` returning `{name: shaped}`. Consumed by `cli/ccp.py` (A3) and `server/app.py` (A4).

- [ ] **Step 1: Write the smoke test** (shaping logic, no network)

```python
# tests/test_views.py
from cli.views import shape_bindings

def test_v1_shaping():
    bindings = [{"id": {"value": "cl:x"}, "type": {"value": "claim"},
                 "label": {"value": "L"}, "verdict": {"value": "passed"}}]
    out = shape_bindings("V1", bindings)
    assert out == [{"id": "cl:x", "type": "claim", "label": "L", "verdict": "passed"}]

def test_v5_shaping_is_id_list():
    bindings = [{"id": {"value": "jd:a"}}, {"id": {"value": "am:b"}}]
    assert shape_bindings("V5", bindings) == ["jd:a", "am:b"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_views.py -v`
Expected: FAIL (no module cli.views)

- [ ] **Step 3: Write the five SPARQL queries**

`views/queries/V1.rq`:
```sparql
PREFIX p: <urn:nyccompost:prop:>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX earl: <http://www.w3.org/ns/earl#>
SELECT ?id ?type ?label ?verdict WHERE {
  ?node p:nodeType ?type ; rdfs:label ?label .
  BIND(STR(?node) AS ?id)
  OPTIONAL { ?gov p:judges ?node ; earl:outcome ?o .
             BIND(REPLACE(STR(?o), "^.*[#/]", "") AS ?govVerdict) }
  OPTIONAL { ?node earl:outcome ?own . BIND(REPLACE(STR(?own), "^.*[#/]", "") AS ?ownVerdict) }
  BIND(COALESCE(?ownVerdict, ?govVerdict, "—") AS ?verdict)
}
```
*(V2–V5 follow the same prefix block. V2 selects the five edge predicates; V3 is built client-side from the node's properties; V4 is computed in Python from V2 closure; V5 filters `p:nodeType IN ("assumption","judgment")`. See `cli/views.py` for the non-SPARQL views.)*

`views/queries/V2.rq`:
```sparql
PREFIX p: <urn:nyccompost:prop:>
SELECT ?src_id ?dst_id ?rel WHERE {
  VALUES ?rel { "supports" "judges" "dependsOn" "assumes" "attestsOver" }
  ?s ?pred ?o .
  BIND(STR(?s) AS ?src_id) BIND(STR(?o) AS ?dst_id)
  FILTER(?pred = IRI(CONCAT("urn:nyccompost:prop:", ?rel)))
}
```

`views/queries/V5.rq`:
```sparql
PREFIX p: <urn:nyccompost:prop:>
SELECT ?id WHERE { ?n p:nodeType ?t . FILTER(?t IN ("assumption","judgment")) BIND(STR(?n) AS ?id) }
```

`views/queries/V3.rq` and `views/queries/V4.rq`: single-line comment files —
```sparql
# V3 node_detail and V4 rests_on are assembled in cli/views.py
# (V3 from per-node properties; V4 from transitive closure of V2). Not direct SELECTs.
```

- [ ] **Step 4: Write `cli/views.py`**

```python
"""Map SPARQL JSON bindings to the frozen view shapes (views/schema.json)."""
from __future__ import annotations
from pathlib import Path

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

def materialize(client, branch):
    """Run SPARQL views against Flexo, assemble V1–V5 dict. V3 from node props is
    layered in by cli.trig_to_views for offline; for Flexo we query node props per id."""
    result = {}
    for name in ("V1", "V2", "V5"):
        sparql = (QUERY_DIR / f"{name}.rq").read_text()
        result[name] = shape_bindings(name, client.query(branch, sparql)["results"]["bindings"])
    result["V4"] = rests_on(result["V2"])
    result["V3"] = {}  # populated by a node-detail pass (out of smoke-test scope tonight)
    return result
```

- [ ] **Step 5: Run test to verify it passes**

Run: `uv run pytest tests/test_views.py -v`
Expected: PASS (2 passed)

- [ ] **Step 6: Commit**

```bash
git add views/queries cli/views.py tests/test_views.py
git commit -m "Task A2: SPARQL V1/V2/V5 + Python V3/V4 shaping"
```

---

### Task A3: CLI (`ccp`) with seed-offline / load / refresh / serve

**Files:**
- Create: `cli/trig_to_views.py`, `cli/ccp.py`, `tests/test_trig_to_views.py`

**Interfaces:**
- Consumes: `FlexoClient` (A1), `cli.views.materialize`/`rests_on` (A2).
- Produces: `trig_to_views(trig_path) -> dict[str, object]` (the offline `.trig`→views builder, writes identical shapes to Task 0's seed); typer `app` with commands `seed_offline`, `load`, `refresh`, `serve`.

- [ ] **Step 1: Write the smoke test** (offline build of the stub reproduces the seed shapes)

```python
# tests/test_trig_to_views.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_trig_to_views.py -v`
Expected: FAIL (no module cli.trig_to_views)

- [ ] **Step 3: Implement `cli/trig_to_views.py`** (rdflib; CURIE-ifies ids using the stub's prefixes)

```python
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
    typed = {s: str(o) for s, _, o in ds.quads((None, URIRef(P + "nodeType"), None, None))}
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_trig_to_views.py -v`
Expected: PASS (1 passed)

- [ ] **Step 5: Implement `cli/ccp.py`** (typer commands)

```python
"""ccp — the pipeline CLI. seed-offline | load | refresh | serve."""
from __future__ import annotations
import json, os
from pathlib import Path
import typer
from cli.trig_to_views import trig_to_views

app = typer.Typer(help="Civic Claim Provenance pipeline")
ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "views" / "cache"

def _write_cache(views: dict):
    CACHE.mkdir(parents=True, exist_ok=True)
    for name, data in views.items():
        (CACHE / f"{name}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))

def _client():
    from cli.flexo_client import FlexoClient
    return FlexoClient(os.environ.get("FLEXO_URL", "https://try-layer1.starforge.app"),
                       os.environ.get("FLEXO_ORG", "civic"),
                       os.environ.get("FLEXO_REPO", "composting"),
                       token=os.environ.get("FLEXO_TOKEN"),
                       auth_url=os.environ.get("FLEXO_AUTH_URL"))

@app.command("seed-offline")
def seed_offline(trig: str = "fixtures/graph-explorer-stub.trig"):
    """Build the cache directly from a .trig (no Flexo)."""
    _write_cache(trig_to_views(trig))
    typer.echo(f"cache written from {trig}")

@app.command()
def load(trig: str, branch: str = os.environ.get("FLEXO_BRANCH", "main")):
    """Load a .trig into Flexo (named graphs preserved on one branch)."""
    from rdflib import Dataset
    c = _client(); c.login()
    ds = Dataset(); ds.parse(trig, format="trig")
    for ctx in ds.contexts():
        nt = ctx.serialize(format="nt").strip()
        if not nt:
            continue
        gname = str(ctx.identifier)
        body = f"INSERT DATA {{ GRAPH <{gname}> {{\n{nt}\n}} }}"
        c.update(branch, body)
    typer.echo(f"loaded {trig} into {branch}")

@app.command()
def refresh(branch: str = os.environ.get("FLEXO_BRANCH", "main")):
    """Materialize the cache from Flexo via SPARQL."""
    from cli.views import materialize
    c = _client(); c.login()
    _write_cache(materialize(c, branch))
    typer.echo("cache refreshed from Flexo")

@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000):
    """Run the dashboard backend (serves the cache + /refresh)."""
    import uvicorn
    uvicorn.run("server.app:api", host=host, port=port)

if __name__ == "__main__":
    app()
```

- [ ] **Step 6: Verify `seed-offline` reproduces a valid cache and commit**

Run: `uv run ccp seed-offline && python3 -c "import json; print(len(json.load(open('views/cache/V1.json'))), 'nodes')"`
Expected: `6 nodes`

```bash
git add cli/trig_to_views.py cli/ccp.py tests/test_trig_to_views.py views/cache
git commit -m "Task A3: ccp CLI (seed-offline/load/refresh/serve) + rdflib offline builder"
```

---

### Task A4: Dashboard backend (FastAPI)

**Files:**
- Create: `server/__init__.py` (empty), `server/app.py`, `tests/test_server.py`

**Interfaces:**
- Consumes: `views/cache/*.json`; `cli.trig_to_views` / `cli.views` for `/refresh`.
- Produces: FastAPI app `api` with `GET /views/{name}` (name ∈ V1…V5) returning the cached JSON, and `POST /refresh` (offline rebuild from the stub by default). Consumed by `ui/src/data/views.ts` (B1).

- [ ] **Step 1: Write the smoke test**

```python
# tests/test_server.py
from fastapi.testclient import TestClient
from server.app import api

def test_get_v1_returns_nodes():
    client = TestClient(api)
    r = client.get("/views/V1")
    assert r.status_code == 200
    assert any(n["type"] == "claim" for n in r.json())

def test_unknown_view_404():
    assert TestClient(api).get("/views/V9").status_code == 404
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_server.py -v`
Expected: FAIL (no server.app)

- [ ] **Step 3: Implement `server/app.py`**

```python
"""Dashboard backend: serve the JSON cache + a refresh hook. CORS open for Vite dev."""
from __future__ import annotations
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "views" / "cache"
VIEWS = {"V1", "V2", "V3", "V4", "V5"}

api = FastAPI(title="Civic Claim Provenance backend")
api.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@api.get("/views/{name}")
def get_view(name: str):
    if name not in VIEWS:
        raise HTTPException(404, f"unknown view {name}")
    f = CACHE / f"{name}.json"
    if not f.exists():
        raise HTTPException(404, f"{name} not materialized — run `ccp seed-offline`")
    return json.loads(f.read_text())

@api.post("/refresh")
def refresh(trig: str = "fixtures/graph-explorer-stub.trig"):
    from cli.trig_to_views import trig_to_views
    views = trig_to_views(str(ROOT / trig))
    CACHE.mkdir(parents=True, exist_ok=True)
    for n, data in views.items():
        (CACHE / f"{n}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return {"refreshed": sorted(views.keys())}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_server.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add server/__init__.py server/app.py tests/test_server.py
git commit -m "Task A4: FastAPI dashboard backend (serve cache + /refresh)"
```

---

### Task A5: Flexo provisioning + env docs

**Files:**
- Create: `flexo/init.sh`, `flexo/.env.example`, `flexo/README.md`

**Interfaces:**
- Produces: an executable `init.sh` that provisions org/repo/main branch and loads the stub via `ccp load`; documented env contract.

- [ ] **Step 1: Write `flexo/.env.example`**

```bash
# Remote (default) — token Z holds:
FLEXO_URL=https://try-layer1.starforge.app
FLEXO_TOKEN=
FLEXO_ORG=civic
FLEXO_REPO=composting
FLEXO_BRANCH=main
# Local stack (openmbee/flexo-mms-deployment) alternative:
# FLEXO_URL=http://localhost:8080
# FLEXO_AUTH_URL=http://localhost:8082
# FLEXO_USER=user01
# FLEXO_PASS=password1
```

- [ ] **Step 2: Write `flexo/init.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail
# Provision org/repo and load the stub fixture into Flexo, then refresh the cache.
# Requires a .env with FLEXO_* (see .env.example). Reuses the ccp CLI.
cd "$(dirname "$0")/.."
[ -f .env ] && set -a && . ./.env && set +a
python3 - <<'PY'
import os, httpx
base=os.environ["FLEXO_URL"].rstrip("/"); org=os.environ.get("FLEXO_ORG","civic"); repo=os.environ.get("FLEXO_REPO","composting")
tok=os.environ.get("FLEXO_TOKEN")
if not tok and os.environ.get("FLEXO_AUTH_URL"):
    tok=httpx.get(os.environ["FLEXO_AUTH_URL"].rstrip("/")+"/login",
                  auth=(os.environ.get("FLEXO_USER","user01"),os.environ.get("FLEXO_PASS","password1")),timeout=30).json()["token"]
h={"Authorization":f"Bearer {tok}","Content-Type":"text/turtle"}
for url in (f"{base}/orgs/{org}", f"{base}/orgs/{org}/repos/{repo}"):
    code=httpx.put(url,headers=h,content=f'<> <http://purl.org/dc/terms/title> "x"@en .',timeout=180).status_code
    print(url, code, "(409=exists OK)" if code==409 else "")
PY
uv run ccp load fixtures/graph-explorer-stub.trig
uv run ccp refresh
echo "Flexo provisioned + cache refreshed."
```

- [ ] **Step 3: Write `flexo/README.md`** (local-stack instructions)

```markdown
# Flexo backing

Default: hosted remote `try-layer1.starforge.app` (Z holds the token) — no Docker.
Set `FLEXO_TOKEN` in `.env` (copy from `.env.example`), then `./flexo/init.sh`.

## Local stack (offline fallback)
The full Layer-1 stack is the external openmbee deployment, not vendored here:
```bash
git clone https://github.com/openmbee/flexo-mms-deployment.git
cd flexo-mms-deployment/docker-compose && docker compose up -d
# wait for: layer1-service ... Responding at http://0.0.0.0:8080
```
Then point `.env` at the local URLs (commented block in `.env.example`) and run `./flexo/init.sh`.
Named graph = preserved inside one `main` branch; V1–V5 query the union.
```

- [ ] **Step 4: Make executable and commit**

Run: `chmod +x flexo/init.sh && bash -n flexo/init.sh && echo "syntax ok"`
Expected: `syntax ok`

```bash
git add flexo/
git commit -m "Task A5: Flexo provisioning (init.sh) + env + local-stack docs"
```

---

### Task A6: Vendor closure-rule tooling (Z/WP-1b, off UI critical path)

**Files:**
- Create: `ontology/shacl_runner.py`, `ontology/rdf_utils.py`, `ontology/closure_shapes.ttl`, `ontology/__init__.py`, `tests/test_closure.py`

**Interfaces:**
- Produces: `run_shacl(data_graph, shapes_graph, ...) -> ShaclResult` (vendored verbatim); a minimal `closure_shapes.ttl` asserting "every judgment carries a rationale".

- [ ] **Step 1: Vendor the two libs verbatim**

```bash
cp /Users/z/Documents/GitHub/flexo-conflict-resolution-policy-research/experiments/lib/shacl_runner.py ontology/shacl_runner.py
cp /Users/z/Documents/GitHub/flexo-conflict-resolution-policy-research/experiments/lib/rdf_utils.py ontology/rdf_utils.py
touch ontology/__init__.py
```

- [ ] **Step 2: Write `ontology/closure_shapes.ttl`** (one real invariant)

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix p:  <urn:nyccompost:prop:> .
[] a sh:NodeShape ;
   sh:targetSubjectsOf p:chosen ;     # every node that made a choice (a judgment)
   sh:property [ sh:path p:rationale ; sh:minCount 1 ;
                 sh:message "judgment lacks a rationale (WP-1b closure)" ] .
```

- [ ] **Step 3: Write the smoke test** (stub passes the rationale invariant)

```python
# tests/test_closure.py
from rdflib import Graph, Dataset
from ontology.shacl_runner import run_shacl

def test_stub_judgments_have_rationale():
    ds = Dataset(); ds.parse("fixtures/graph-explorer-stub.trig", format="trig")
    data = Graph()
    for q in ds.quads((None, None, None, None)):
        data.add(q[:3])
    shapes = Graph(); shapes.parse("ontology/closure_shapes.ttl", format="turtle")
    assert run_shacl(data, shapes).conforms
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_closure.py -v`
Expected: PASS (1 passed)

- [ ] **Step 5: Commit**

```bash
git add ontology/ tests/test_closure.py
git commit -m "Task A6: vendor SHACL closure tooling + rationale invariant (WP-1b)"
```

---

## TRACK B — Dashboard UI (Joshua). Tasks B1–B5 run after Task 0, parallel to Track A.

### Task B1: Vite/React/TS scaffold + data layer

**Files:**
- Create: `ui/` (via Vite), `ui/src/data/views.ts`, `ui/.env`
- Modify: `ui/src/App.tsx` (smoke render)

**Interfaces:**
- Produces: types `NodeRow {id,type,label,verdict}`, `EdgeRow {src_id,dst_id,rel}`; `fetchView<T>(name): Promise<T>` reading `${VITE_API}/views/{name}` (default `http://127.0.0.1:8000`). Consumed by B2–B5.

- [ ] **Step 1: Scaffold Vite + add Cytoscape**

```bash
cd /Users/z/Documents/GitHub/civic-claim-provenance
npm create vite@latest ui -- --template react-ts
cd ui && npm install && npm install cytoscape
printf 'VITE_API=http://127.0.0.1:8000\n' > .env
```

- [ ] **Step 2: Write `ui/src/data/views.ts`**

```typescript
export type NodeType = "claim" | "evidence" | "assumption" | "judgment" | "attestation";
export type Verdict = "passed" | "failed" | "cantTell" | "—";
export type EdgeRel = "supports" | "judges" | "dependsOn" | "assumes" | "attestsOver";
export interface NodeRow { id: string; type: NodeType; label: string; verdict: Verdict; }
export interface EdgeRow { src_id: string; dst_id: string; rel: EdgeRel; }

const API = (import.meta.env.VITE_API as string) ?? "http://127.0.0.1:8000";

export async function fetchView<T>(name: "V1" | "V2" | "V3" | "V4" | "V5"): Promise<T> {
  const r = await fetch(`${API}/views/${name}`);
  if (!r.ok) throw new Error(`view ${name}: ${r.status}`);
  return r.json() as Promise<T>;
}
```

- [ ] **Step 3: Smoke render in `ui/src/App.tsx`**

```tsx
import { useEffect, useState } from "react";
import { fetchView, NodeRow } from "./data/views";
export default function App() {
  const [nodes, setNodes] = useState<NodeRow[]>([]);
  useEffect(() => { fetchView<NodeRow[]>("V1").then(setNodes).catch(console.error); }, []);
  return <pre>{nodes.length} nodes loaded</pre>;
}
```

- [ ] **Step 4: Verify (backend must be running)**

Run (in repo root, separate shell): `uv run ccp serve`
Then verify via preview tooling that the page shows `6 nodes loaded`.
Expected: `6 nodes loaded`

- [ ] **Step 5: Commit**

```bash
git add ui/
git commit -m "Task B1: Vite/React/TS scaffold + typed view fetch layer"
```

---

### Task B2: Cytoscape graph (V1 nodes + V2 edges)

**Files:**
- Create: `ui/src/graph/Graph.tsx`, `ui/src/graph/style.ts`
- Modify: `ui/src/App.tsx`

**Interfaces:**
- Consumes: `fetchView`, `NodeRow`, `EdgeRow` (B1).
- Produces: `<Graph onSelect={(id:string)=>void} hidden?:Set<string> />` rendering color-by-type, shade-by-verdict.

- [ ] **Step 1: Write `ui/src/graph/style.ts`** (the visual contract)

```typescript
export const TYPE_COLOR: Record<string, string> = {
  claim: "#2563eb", evidence: "#16a34a", assumption: "#9333ea",
  judgment: "#ea580c", attestation: "#0d9488",
};
export const VERDICT_OPACITY: Record<string, number> = {
  passed: 1.0, cantTell: 0.55, failed: 0.3, "—": 0.85,
};
```

- [ ] **Step 2: Write `ui/src/graph/Graph.tsx`**

```tsx
import { useEffect, useRef } from "react";
import cytoscape from "cytoscape";
import { fetchView, NodeRow, EdgeRow } from "../data/views";
import { TYPE_COLOR, VERDICT_OPACITY } from "./style";

export function Graph({ onSelect, hidden }: { onSelect: (id: string) => void; hidden?: Set<string> }) {
  const box = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  useEffect(() => {
    let cy: cytoscape.Core;
    Promise.all([fetchView<NodeRow[]>("V1"), fetchView<EdgeRow[]>("V2")]).then(([nodes, edges]) => {
      cy = cytoscape({
        container: box.current!,
        elements: [
          ...nodes.map((n) => ({ data: { id: n.id, label: n.label, type: n.type, verdict: n.verdict } })),
          ...edges.map((e) => ({ data: { id: `${e.src_id}-${e.rel}-${e.dst_id}`, source: e.src_id, target: e.dst_id, rel: e.rel } })),
        ],
        style: [
          { selector: "node", style: {
            "background-color": (el: any) => TYPE_COLOR[el.data("type")] ?? "#666",
            "background-opacity": (el: any) => VERDICT_OPACITY[el.data("verdict")] ?? 1,
            label: "data(label)", "font-size": 8, "text-wrap": "wrap", "text-max-width": "120px",
            width: 28, height: 28, "text-valign": "bottom" } },
          { selector: "edge", style: {
            label: "data(rel)", "font-size": 6, "curve-style": "bezier",
            "target-arrow-shape": "triangle", width: 1.5, "line-color": "#bbb", "target-arrow-color": "#bbb" } },
          { selector: ".hidden", style: { display: "none" } },
        ],
        layout: { name: "breadthfirst", directed: true, padding: 20 },
      });
      cy.on("tap", "node", (ev) => onSelect(ev.target.id()));
      cyRef.current = cy;
    });
    return () => cy?.destroy();
  }, [onSelect]);
  useEffect(() => {
    const cy = cyRef.current; if (!cy) return;
    cy.nodes().forEach((n) => n.toggleClass("hidden", !!hidden && !hidden.has(n.id())));
  }, [hidden]);
  return <div ref={box} style={{ width: "100%", height: "100%" }} />;
}
```

- [ ] **Step 3: Render `<Graph>` full-bleed in `App.tsx`** (temporary, finalized in B5)

```tsx
import { Graph } from "./graph/Graph";
export default function App() {
  return <div style={{ height: "100vh" }}><Graph onSelect={(id) => console.log(id)} /></div>;
}
```

- [ ] **Step 4: Verify via preview** — graph shows 6 colored nodes, 7 labeled edges; the `cantTell` judgment is visibly faded.

- [ ] **Step 5: Commit**

```bash
git add ui/src/graph ui/src/App.tsx
git commit -m "Task B2: Cytoscape graph — color by type, shade by verdict"
```

---

### Task B3: Inspector panel (V3)

**Files:**
- Create: `ui/src/inspector/Inspector.tsx`

**Interfaces:**
- Consumes: `fetchView<Record<string, any>>("V3")`.
- Produces: `<Inspector selectedId={string|null} />` rendering the node-detail record as labeled rows.

- [ ] **Step 1: Write `ui/src/inspector/Inspector.tsx`**

```tsx
import { useEffect, useState } from "react";
import { fetchView } from "../data/views";

export function Inspector({ selectedId }: { selectedId: string | null }) {
  const [detail, setDetail] = useState<Record<string, any>>({});
  useEffect(() => { fetchView<Record<string, any>>("V3").then(setDetail).catch(console.error); }, []);
  if (!selectedId) return <aside style={pane}><em>Select a node</em></aside>;
  const rec = detail[selectedId] ?? {};
  return (
    <aside style={pane}>
      <h3 style={{ marginTop: 0 }}>{selectedId}</h3>
      <table><tbody>
        {Object.entries(rec).map(([k, v]) => (
          <tr key={k}><td style={{ fontWeight: 600, paddingRight: 8, verticalAlign: "top" }}>{k}</td><td>{String(v)}</td></tr>
        ))}
      </tbody></table>
    </aside>
  );
}
const pane: React.CSSProperties = { width: 320, padding: 16, borderLeft: "1px solid #ddd", overflow: "auto", fontSize: 13 };
```

- [ ] **Step 2: Verify in B5** (wired with selection there). Commit now.

```bash
git add ui/src/inspector
git commit -m "Task B3: V3 inspector panel"
```

---

### Task B4: Filters (V5 keep; V4 stretch)

**Files:**
- Create: `ui/src/filters/Filters.tsx`

**Interfaces:**
- Produces: `<Filters onJudgmentsOnly={(on:boolean)=>void} onRestsOn={(on:boolean)=>void} />` — two toggle buttons. Parent computes the `hidden` set from V5/V4.

- [ ] **Step 1: Write `ui/src/filters/Filters.tsx`**

```tsx
import { useState } from "react";
export function Filters({ onJudgmentsOnly, onRestsOn }:
  { onJudgmentsOnly: (on: boolean) => void; onRestsOn: (on: boolean) => void }) {
  const [j, setJ] = useState(false); const [r, setR] = useState(false);
  return (
    <div style={{ display: "flex", gap: 8, padding: 8 }}>
      <button onClick={() => { const v = !j; setJ(v); onJudgmentsOnly(v); }}
              style={btn(j)}>Show only the judgment calls</button>
      <button onClick={() => { const v = !r; setR(v); onRestsOn(v); }}
              style={btn(r)}>What this rests on (stretch)</button>
    </div>
  );
}
const btn = (on: boolean): React.CSSProperties => ({
  padding: "6px 10px", border: "1px solid #888", borderRadius: 6,
  background: on ? "#1f2937" : "#fff", color: on ? "#fff" : "#111", cursor: "pointer" });
```

- [ ] **Step 2: Commit** (wired in B5)

```bash
git add ui/src/filters
git commit -m "Task B4: V5 judgments-only + V4 rests-on filter buttons"
```

---

### Task B5: App layout + wire selection & filters

**Files:**
- Modify: `ui/src/App.tsx`

**Interfaces:**
- Consumes: `Graph`, `Inspector`, `Filters`, `fetchView` (B1–B4).

- [ ] **Step 1: Write the final `ui/src/App.tsx`**

```tsx
import { useEffect, useState } from "react";
import { Graph } from "./graph/Graph";
import { Inspector } from "./inspector/Inspector";
import { Filters } from "./filters/Filters";
import { fetchView, NodeRow } from "./data/views";

export default function App() {
  const [selected, setSelected] = useState<string | null>(null);
  const [allIds, setAllIds] = useState<string[]>([]);
  const [hidden, setHidden] = useState<Set<string> | undefined>(undefined);

  useEffect(() => { fetchView<NodeRow[]>("V1").then((ns) => setAllIds(ns.map((n) => n.id))); }, []);

  const judgmentsOnly = async (on: boolean) => {
    if (!on) return setHidden(undefined);
    const keep = new Set(await fetchView<string[]>("V5"));
    setHidden(keep);
  };
  const restsOn = async (on: boolean) => {
    if (!on || !selected) return setHidden(undefined);
    const v4 = await fetchView<Record<string, string[]>>("V4");
    const keep = new Set([selected, ...(v4[selected] ?? [])]);
    setHidden(keep);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <header style={{ padding: "8px 16px", borderBottom: "1px solid #ddd" }}>
        <strong>Civic Claim Provenance</strong> — NYC composting claim
        <Filters onJudgmentsOnly={judgmentsOnly} onRestsOn={restsOn} />
      </header>
      <div style={{ display: "flex", flex: 1, minHeight: 0 }}>
        <div style={{ flex: 1, minWidth: 0 }}><Graph onSelect={setSelected} hidden={hidden} /></div>
        <Inspector selectedId={selected} />
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Full demo verification via preview** — with `uv run ccp serve` running: graph renders; clicking the governing judgment fills the inspector with `decision/chosen/grounding/attributer/rationale`; "show only the judgment calls" hides everything except the assumption + two judgments; the `cantTell` node is faded.

- [ ] **Step 3: Commit**

```bash
git add ui/src/App.tsx
git commit -m "Task B5: app layout + wired selection, V5/V4 filters — demo complete"
```

---

## TRACK C — Content path (Christine). Runs after Task 0, parallel.

### Task C1: Capture template + load path

**Files:**
- Create: `fixtures/capture-template.md`

**Interfaces:**
- Produces: the B2-capture-discipline template (one row per judgment) and the documented path `notes → .trig → ccp load → ccp refresh`.

- [ ] **Step 1: Write `fixtures/capture-template.md`** (interface-contract B2)

```markdown
# Judgment capture template (Contract B2)

One row per link / judgment. Every judgment must be explainable AT LOGGING TIME:
"I chose X because Y, on grounds Z." No silent judgments in code.

| link/claim | backing evidence (ev:* id or query_url+ts) | decision | chosen | verdict (passed/failed/cantTell) | grounding (precedent/theory/principle) | attributer (your name) | rationale (the why) | depends-on |
|---|---|---|---|---|---|---|---|---|
| e.g. variation describable | ev:demo-tonnage | Is CY2025 tonnage describable? | supported | passed | complete series 708=59x12 | C. Analyst | zero missing across 25,060 rows | ev:demo-tonnage |

When complete, Z lifts these rows into conformant `jd:*`/`ev:*` nodes in a `.trig`,
then: `uv run ccp load <file>.trig && uv run ccp refresh` — the dashboard updates with zero UI change.
```

- [ ] **Step 2: Commit**

```bash
git add fixtures/capture-template.md
git commit -m "Task C1: judgment capture template + load path (Contract B2)"
```

---

## INTEGRATION

### Task D1: End-to-end demo smoke + README finalize

**Files:**
- Modify: `README.md` (fill any gaps), add `tests/test_e2e.py`

- [ ] **Step 1: Write `tests/test_e2e.py`** (offline path produces a renderable cache)

```python
# tests/test_e2e.py
import json, subprocess, sys
from pathlib import Path

def test_seed_offline_then_serve_shapes():
    subprocess.run([sys.executable, "-m", "cli.ccp", "seed-offline"], check=True)
    v1 = json.loads(Path("views/cache/V1.json").read_text())
    v2 = json.loads(Path("views/cache/V2.json").read_text())
    assert len(v1) == 6 and len(v2) == 7
    assert {n["type"] for n in v1} == {"claim","evidence","assumption","judgment","attestation"}
    assert {e["rel"] for e in v2} == {"supports","judges","dependsOn","assumes","attestsOver"}
```

- [ ] **Step 2: Run the full suite**

Run: `uv run pytest -v`
Expected: all PASS

- [ ] **Step 3: Manual demo dry-run** (the 3-minute path)

```bash
uv run ccp seed-offline && uv run ccp serve &   # backend :8000
cd ui && npm run dev                            # dashboard :5173
```
Verify via preview: graph renders → click judgment → inspector → "judgment calls" filter.

- [ ] **Step 4: Commit**

```bash
git add tests/test_e2e.py README.md
git commit -m "Task D1: end-to-end demo smoke test + README finalize"
```

---

## Self-Review

**Spec coverage:**
- Pipeline (spec §3) → Tasks A1–A4 + B1 (each stage). ✓
- Reuse (§4) → A1 (Flexo client), A2 (.rq convention), A6 (shacl_runner/rdf_utils). ✓
- Single-branch load (§4) → A3 `load` (GRAPH-per-context into one branch). ✓
- V1–V5 frozen shapes (§5) → Task 0 schema.json + cache; produced by A2/A3, consumed by B2–B5. ✓
- Repo layout (§6) → Task 0 + per-track files. ✓
- 3-min demo (§7) → B5 Step 2 + D1 Step 3. ✓
- Parallelization (§8) → Task 0 unblocks; Tracks A/B/C independent. ✓
- Acceptance (§9) → D1. ✓
- Open items (§10): real `.trig` wired via same `load` path (A3); remote default (A5); per-capita = cantTell node (already in seed cache). ✓

**Type consistency:** `NodeRow/EdgeRow/Verdict/NodeType/EdgeRel` consistent across B1–B5; `fetchView` signature stable; Python view keys `V1…V5` consistent across A2/A3/A4; cache file names `V{n}.json` consistent. ✓

**Placeholder scan:** no TBD/TODO; every code step has full code. V3-from-Flexo is explicitly marked out-of-scope tonight in A2 (offline V3 via A3 covers the demo). ✓
