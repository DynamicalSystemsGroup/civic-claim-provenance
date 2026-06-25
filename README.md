# Civic Claim Provenance — Graph Explorer

Assurance layer for civic AI: make one government claim's chain of evidence
inspectable, keep the human judgment authoritative. Demo = the graph explorer.

## Pipeline
`.trig → ccp load → Flexo → SPARQL → ccp refresh → views/cache/*.json → ccp serve → ui/`
The demo reads the cache. Flexo is upstream of the cache only.

## Quickstart (no Flexo needed)
```bash
uv sync
# uv run ccp seed-offline fixtures/graph-explorer-stub.trig   # regenerate cache
uv run ccp seed-offline
uv run ccp serve                                            # backend on :8000
cd ui && npm install && npm run dev                         # dashboard on :5173
```

## Team — MVC

We sprint in parallel, each owning one layer. **Read [`CLAUDE.md`](CLAUDE.md) and
[`docs/BRANCHING.md`](docs/BRANCHING.md) before your first commit.**

- **M — Model — Zargham:** `flexo/`, `ontology/`, `views/schema.json`, `views/queries/`, `cli/` (Flexo deployment + ontology + the frozen view contract)
- **V — View — Joshua:** `ui/`, `server/` (the graph-explorer dashboard + its backend)
- **C — Controller — Christine:** `analysis/`, `fixtures/capture-template.md` (the real analysis, coerced into M's ontology, rendered by V)

The seam between layers is the frozen V1–V5 contract in `views/schema.json` and the
generated `views/cache/*.json`. Bind to shapes, not internals.
