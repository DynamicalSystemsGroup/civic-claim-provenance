# Design — Civic Claim Provenance: Graph Explorer Scaffold

**Date:** 2026-06-24
**Author:** Zargham (DSG), with Claude
**Status:** Draft for review
**Scope:** Tonight's hackathon scaffold. Maximally parallelizable across three people; deliberate technical debt accepted; a working 3-minute demo is the only hard success criterion.

---

## 1. Goal

Ship a **graph-explorer dashboard** that renders the NYC composting claim's chain of evidence — the WP-3b surface over the interface-contract **V1–V5 frozen views**. A non-technical stakeholder can see the provenance graph, tell evidence from human judgment at a glance, spot where the data honestly *can't tell*, and inspect any node's grounds.

The demo's product is the **accountable process**, not any particular result.

## 2. Non-goals (deliberate debt, named not hidden)

- **No live-Flexo dependency during the demo.** The demo reads a JSON cache. (Flexo is upstream of the cache, not in the demo's hot path.)
- **No V6 counterfactual** ("what would change") — stretch only.
- **No closure-rule enforcement in the UI** — that's Z's server-side concern (WP-1b); shapes vendored but off the UI critical path.
- **No auth, no org-as-node, no cryptographic signing** — roadmap, per the memos.
- **Hand-written SPARQL against a thin schema; smoke-test only; minimal-but-legible styling.**

## 3. The pipeline (the load-bearing decision)

```
.trig  (Christine's analysis, logged per Z's ontology)
  └─ cli load        → FLEXO quadstore  (single working branch, named graphs preserved)
                          └─ SPARQL  (views/queries/V1–V5.rq)
                              └─ cli refresh   → JSON CACHE  (views/cache/*.json)   ← demo source of truth
                                                   └─ dashboard backend  (serve cache + POST /refresh)
                                                        └─ dashboard views  (Cytoscape)
```

**The JSON cache is the seam.** It de-risks the 3-minute demo (deterministic, fast, cannot fail live) while preserving the real-MMS provenance story (the cache is materialized *from Flexo via SPARQL*, not hand-authored).

**Two routes write the identical cache** so no one is blocked:
- `cli refresh` — Flexo → SPARQL → cache. **The demo path.**
- `cli seed-offline` — `.trig` → cache directly via rdflib, **no Flexo**. Joshua's day-one unblock and the ultimate fallback.

## 4. Reuse (this is ~all existing, battle-tested DSG code)

| Need | Reused from | How |
|---|---|---|
| Flexo Layer-1 client | `ADCS-lifecycle-demo/pipeline/backends/flexo.py` + `flexo-conflict.../experiments/experiment-1/run.sh` | `login` (`GET $AUTH/login` → token), `put` (provision org/repo/branch), `update` (`INSERT DATA` via `application/sparql-update`), `query` (`POST .rq` → SPARQL JSON). Bearer auth; re-fetch token per phase (JWT expires fast). |
| SPARQL-as-files | experiments' `oracle/*.rq` convention | `views/queries/V1…V5.rq` |
| Closure rules (Z, WP-1b) | `flexo-conflict.../experiments/lib/shacl_runner.py` + `rdf_utils.py` | vendored into `ontology/`; `pyshacl`-based; off UI critical path |
| Local Flexo stack | external `openmbee/flexo-mms-deployment` compose | documented in `flexo/README.md`, **not vendored**. Remote `try-layer1.starforge.app` (token Z holds) is functionally equivalent (Exp 9–11) and the default. |

**Confirmed endpoint facts:** Layer-1 :8080, auth :8082, `user01/password1` local; addressing `{FLEXO_URL}/orgs/{ORG}/repos/{REPO}/branches/{BRANCH}/{query|update}`.

**Single-branch decision:** the explorer must render the whole graph at once, so all four named graphs (`g:evidence` / `g:provenance` / `g:judgments` / `g:attestation`) load into **one** working branch (preserved via `INSERT DATA { GRAPH g:… { … } }`); V1–V5 query the default-union. Branch-per-layer stays a Z/WP-1c flourish, not a UI dependency.

## 5. The five views (frozen shapes — interface-contract A4, source of truth)

`views/schema.json` is the single authority; UI and CLI both bind to it.

- **V1 `nodes`** → `{id, type∈{claim,evidence,assumption,judgment,attestation}, label, verdict∈{passed,failed,cantTell,—}}` — node render: **color by `type`, shade by `verdict`**.
- **V2 `edges`** → `{src_id, dst_id, rel∈{supports,judges,dependsOn,assumes,attestsOver}}` — layout.
- **V3 `node_detail(id)`** → per-type record (claim/evidence/assumption/judgment/attestation fields per A4) — inspector panel.
- **V4 `rests_on(id)`** → transitive closure of `judges`/`dependsOn`/`supports` → `[id…]` — "what this rests on" (stretch).
- **V5 `judgments_only`** → `[id…]` where `type∈{assumption,judgment}` — "show only the judgment calls".

Stability guarantee carried from A4: columns and value domains frozen; rows grow; any new field is additive.

## 6. Repo layout (boundaries = parallel ownership)

```
civic-claim-provenance/
  ui/                       # Joshua — Vite + React + Cytoscape.js
    src/
      data/views.ts         # single data path: fetch V1..V5 JSON from backend
      graph/                # Cytoscape: type→color, verdict→shade
      inspector/            # V3 panel
      filters/              # V5 (and V4 stretch) toggles
  cli/                      # the pipeline driver (Python, uv, typer)
    ccp.py                  # commands: load · refresh · seed-offline · serve
    flexo_client.py         # httpx: login/put/update/query (reused)
  server/                   # dashboard backend (thin; part of cli `serve`)
    app.py                  # GET /views/{name}.json (from cache) · POST /refresh
  views/
    schema.json             # frozen V1..V5 shapes (single source of truth)
    queries/V1..V5.rq       # SPARQL
    cache/                  # the JSON cache (committed seed; regenerated by refresh)
  fixtures/
    graph-explorer-stub.trig   # have it now; evidence_supply_chain.trig wired when it lands
  ontology/                 # Z/WP-1b: shacl_runner.py, rdf_utils.py, closure_shapes.ttl
  flexo/
    init.sh                 # provision org/repo/branch
    .env.example            # FLEXO_URL/ORG/REPO/TOKEN/USER/PASS
    README.md               # local-stack (flexo-mms-deployment) + remote docs
  docs/                     # the 5 starter memos + this spec
  README.md                 # quickstart + who-owns-what
```

`cli` and `server` are one Python package, two entry points: `ccp serve` IS the dashboard backend (serves cache + exposes `/refresh`); `ccp refresh` runs the Flexo→cache materialization.

## 7. The 3-minute demo (the only hard success criterion)

1. **Open dashboard** → the provenance graph renders. Nodes colored by *type*, shaded by *verdict*. (V1+V2 from cache.)
2. **Read the graph aloud:** evidence vs judgment nodes are visually distinct; the `cantTell`/`failed` node is right there — *"the tool can honestly say the data can't settle this; that preserves the official's authority."*
3. **Click the governing judgment** → inspector (V3) shows `decision · chosen · grounding · attributer · rationale` — a human call, attributable, with stated grounds.
4. **Toggle "show only the judgment calls"** (V5) → graph collapses to assumptions + judgments — *"every human call, isolated."*
5. *(stretch)* **"what this rests on"** (V4) from the attestation → highlights the chain.
6. **One line on rigor:** *"that JSON came from Flexo via SPARQL — same code local or DSG-hosted; provenance is real, hashed, re-queryable."*

**Core = V1/V2/V3 + V5. V4 stretch. V6 cut.**

## 8. Parallelization (day one, no blocking handoffs)

- **Joshua** builds the entire UI against `views/cache/*.json` (seeded offline from the stub) — no Flexo running.
- **Z** fills `views/queries/*.rq`, stands up the `flexo_client` + `load`, vendors closure shapes.
- **Christine** authors analysis per the capture discipline; her output `.trig` → `load` → `refresh` updates the cache with **zero UI code change**.

## 9. Acceptance

A non-technical viewer can open the dashboard (reading the cache), traverse the composting chain, distinguish evidence from judgment at a glance, reach any node's grounds via the inspector, and isolate the judgment calls — and the cache is reproducibly regenerable from Flexo via `ccp refresh`.

## 10. Open items (carried, not blocking)

- Per-capita denominator → live deferred node (per the work-packages memo); represented as a `cantTell` judgment in the data, no special UI.
- Real `evidence_supply_chain.trig` not yet in the kit — wired when it lands; shape unchanged.
- Repo remote: create `DynamicalSystemsGroup/civic-claim-provenance` and push **after** spec approval (local-only until then).
