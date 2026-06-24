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
