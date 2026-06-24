# CLAUDE.md — how we build this, together and in parallel

This repo is a hackathon sprint. Three people sit side by side, each driving their
own Claude Code, each with **authority over one layer**. This file is the contract
that lets us move fast without colliding. Read it fully before touching anything.

> **First thing:** tell your Claude which layer you own ("I'm Joshua, the View
> layer"). Then work **only inside your layer's directories** and treat the seam
> artifacts below as shared API you change with care.

---

## The product (one paragraph)

An assurance layer for civic AI: take one government claim (NYC residential-organics
composting), make its **chain of evidence inspectable**, and keep the **human's
judgment authoritative**. Evidence does not verify a claim — evidence supports a
human judgment that the claim holds. The demo is a graph explorer that renders that
chain: nodes colored by *type*, shaded by *verdict* (`passed` / `failed` /
`cantTell`), with an inspector and filters.

---

## MVC — who owns what

We are organized as **Model · View · Controller**. Each person has final authority
over their layer's internals; the **seams between layers are frozen contracts**.

| Layer | Owner | Authority over (your directories) | You consume | Do **not** edit |
|---|---|---|---|---|
| **M — Model** | **Zargham** | `flexo/`, `ontology/`, `views/schema.json`, `views/queries/`, `cli/` | Christine's analysis (to coerce into the ontology) | `ui/`, `server/`, `analysis/` |
| **V — View** | **Joshua** | `ui/`, `server/` | `views/cache/*.json` + `views/schema.json` (the contract) | `cli/`, `ontology/`, `flexo/`, `views/queries/` |
| **C — Controller** | **Christine** | `analysis/`, `fixtures/capture-template.md` | pinned NYC Open Data; Z's schema (to conform to) | `ui/`, `server/`, `cli/`, `flexo/` |

- **M (Zargham)** owns *how knowledge is represented and stored*: the Flexo MMS
  deployment (the quadstore) and the abstract ontology + the frozen view shapes the
  dashboard binds to. M projects the store into the JSON cache.
- **V (Joshua)** owns *how it's seen*: the dashboard and its backend. V binds to the
  view **shapes**, never to the store or the ontology behind them.
- **C (Christine)** owns *the actual content*: a real analysis of her choosing over
  the pinned datasets. Her findings + judgments get **coerced into M's ontology** and
  thereby **visualized by V's work**. C asserts the analysis; M gives it form; V
  renders it. No layer silently launders another's.

---

## The pipeline (data flows C → M → V)

```
Christine's analysis (C)             ← real data science, her call
  → capture-template.md rows         ← every judgment explainable at logging time
  → Z coerces into ontology (.trig)  ← fixtures/*.trig, conformant to schema
  → Flexo quadstore (M)              ← ccp load
  → SPARQL views (M)                 ← views/queries/V1..V5.rq
  → JSON cache (M→V CONTRACT)        ← ccp refresh  → views/cache/*.json
  → dashboard backend (V)            ← server/app.py serves the cache
  → graph explorer (V)              ← ui/  Cytoscape: color by type, shade by verdict
```

**The demo reads the cache.** Flexo is upstream of the cache only — if Flexo is
down, the cache (and therefore the demo) still works. There are two ways to fill the
cache, both producing identical shapes:
- `uv run ccp seed-offline fixtures/graph-explorer-stub.trig` — no Flexo, instant
  (day-one + fallback).
- `uv run ccp refresh` — from Flexo via SPARQL (the real-MMS path; needs `.env`).

---

## Seam artifacts — shared API, change with care

These cross layer boundaries. Treat them like a published API.

1. **`views/schema.json`** — THE frozen contract (interface-contract A4). V1–V5 column
   names and value domains. **Only Zargham (M) changes it. Any change ripples to V and
   C — announce it at the table first.** Fields may be *added* (additive); never
   renamed or retyped.
2. **`views/cache/*.json`** — the generated M→V artifact. **Never hand-edit.** It is
   produced by `ccp seed-offline` / `ccp refresh`. On a merge conflict here, do **not**
   resolve by hand — regenerate (`uv run ccp seed-offline`) and commit the result.
3. **`fixtures/*.trig`** — Christine's analysis, coerced into M's ontology. Co-produced
   by C (content) + Z (form). The `.trig` is the hand-off.
4. **`fixtures/capture-template.md`** — the C→M capture discipline. Every judgment must
   carry: decision · chosen · verdict · grounding · attributer · rationale.

The frozen V1–V5 shapes (so everyone can recite them):
- **V1 nodes** `{id, type, label, verdict}` — `type ∈ {claim,evidence,assumption,judgment,attestation}`, `verdict ∈ {passed,failed,cantTell,—}`
- **V2 edges** `{src_id, dst_id, rel}` — `rel ∈ {supports,judges,dependsOn,assumes,attestsOver}`
- **V3 node_detail** — map `id → per-type record`
- **V4 rests_on** — map `id → [id…]` (transitive closure; stretch)
- **V5 judgments_only** — `[id…]` where type is assumption/judgment

`id` is an opaque string (e.g. `"cl:demo-variation"`). **Type comes from the `type`
field, never inferred from the id prefix.**

---

## Run it

```bash
# Model/pipeline (Python)
uv sync
uv run ccp seed-offline                     # fill the cache from the stub (no Flexo)
uv run ccp serve                            # dashboard backend on :8000
uv run pytest -q                            # smoke tests

# View (dashboard)
cd ui && npm install && npm run dev         # UI on :5173 (set VITE_API if backend moves)
cd ui && npm run build                      # production build / typecheck gate

# Model → Flexo (Zargham only; needs flexo/.env from .env.example)
./flexo/init.sh                             # provision org/repo + load stub + refresh cache
```

---

## House rules for the parallel sprint

- **Stay in your layer.** If a task needs a change in someone else's directory, that's
  a **seam** — say so out loud and let the owner make the change (or pair on it). Do
  not reach across silently.
- **Bind to shapes, not internals.** V binds to `schema.json`, never to SPARQL or the
  ontology. C conforms to the schema, never to the dashboard.
- **The cache is generated.** Regenerate, don't hand-merge.
- **Small commits, frequent integration.** See `docs/BRANCHING.md` for exactly how we
  branch and merge — read it before your first push.
- **Accepted debt (don't "fix" these unasked):** smoke-tests only; minimal styling;
  node-layout clipping; no auth; no live-Flexo in the demo path; V6 counterfactual cut;
  org-as-node and signing are roadmap. Naming the debt is on-brand for the method.
- **When in doubt about a seam, ask the table, not the code.** We're sitting together
  precisely so contract questions resolve in seconds.

Design intent and rationale live in `docs/superpowers/specs/` and the starter memos in
`docs/`. The work breakdown is `docs/work-packages-memo.md`.
