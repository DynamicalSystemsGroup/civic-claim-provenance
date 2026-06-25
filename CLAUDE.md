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
human judgment that the claim holds. The demo is a **Marimo notebook deployed
statically to GitHub Pages** that renders the chain; it reads a pre-computed JSON
cache written by M. The cache is the only interface between M and V — no live server
is needed in the demo path.

---

## MVC — who owns what

We are organized as **Model · View · Controller**. Each person has final authority
over their layer's internals; the **seams between layers are frozen contracts**.

| Layer | Owner | Authority over (your directories) | You consume | Do **not** edit |
| --- | --- | --- | --- | --- |
| **M — Model** | **Zargham** | `flexo/`, `ontology/`, `views/schema.json`, `views/queries/`, `cli/` | Christine's analysis (to coerce into the ontology) | `notebook/`, `analysis/` |
| **V — View** | **Joshua** | `notebook/` (Marimo + GitHub Pages) | `views/cache/*.json` — shape per the M→V contract below | `cli/`, `ontology/`, `flexo/`, `views/queries/` |
| **C — Controller** | **Christine** | `analysis/`, `fixtures/capture-template.md` | pinned NYC Open Data; Z's schema (to conform to) | `notebook/`, `cli/`, `flexo/` |

> **V layer is now a Marimo notebook on GitHub Pages** (replacing `ui/` + `server/`).
> Joshua will define the `notebook/` directory. The FastAPI server (`server/`) is no
> longer needed for the demo path — the Marimo notebook reads the JSON cache directly
> as a static file. `ui/` and `server/` remain in the repo until Joshua cleans them up.

- **M (Zargham)** owns *how knowledge is represented and stored*: the Flexo MMS
  deployment (the quadstore) and the abstract ontology + the frozen view shapes the
  notebook binds to. M projects the store into the JSON cache.
- **V (Joshua)** owns *how it's seen*: the Marimo notebook, its GitHub Pages
  deployment, and the JSON schema M must write to. V binds to the cache shape,
  never to the store or the ontology behind it.
- **C (Christine)** owns *the actual content*: a real analysis of her choosing over
  the pinned datasets. Her findings + judgments get **coerced into M's ontology** and
  thereby **visualized by V's work**. C asserts the analysis; M gives it form; V
  renders it. No layer silently launders another's.

---

## The pipeline (data flows C → M → V)

```text
Christine's analysis (C)             ← real data science, her call
  → capture-template.md rows         ← every judgment explainable at logging time
  → Z coerces into ontology (.trig)  ← fixtures/*.trig, conformant to schema
  → Flexo quadstore (M)              ← ccp load (one branch per named graph)
  → SPARQL projection (M)            ← trig_to_views_from_dataset()
  → JSON cache (M→V CONTRACT)        ← ccp refresh  → views/cache/*.json
  → Marimo notebook (V)              ← notebook/  reads cache as static file
  → GitHub Pages (V)                 ← static deploy; no live server needed
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

1. **`views/cache/*.json`** — the M→V artifact and **the only runtime interface
   between layers**. **Never hand-edit.** Produced by `ccp seed-offline` / `ccp
   refresh`. On a merge conflict here, do **not** resolve by hand — regenerate
   (`uv run ccp seed-offline`) and commit the result.
2. **`views/schema.json`** — M's current output schema (V1–V5, see below). This is
   under active renegotiation with Joshua: **the V1–V5 shape is M's current
   projection; Joshua will specify the shape his Marimo notebook needs and M will
   adapt `ccp refresh` to write to it. Until Joshua's schema is final, V1–V5 is the
   working contract.** Only Zargham (M) edits this file; changes are additive only.
3. **`fixtures/*.trig`** — Christine's analysis, coerced into M's ontology. Co-produced
   by C (content) + Z (form). The `.trig` is the hand-off.
4. **`fixtures/capture-template.md`** — the C→M capture discipline. Every judgment must
   carry: decision · chosen · verdict · grounding · attributer · rationale.

Current M output shapes in `views/cache/` (V1–V5, working contract until Joshua finalises):

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
uv run pytest -q                            # smoke tests

# View (Marimo notebook — Joshua's layer, TBD)
# notebook/ directory to be defined by Joshua; reads views/cache/*.json as static data

# Model → Flexo (Zargham only; needs .env from flexo/.env.example)
./flexo/init.sh                             # provision org/repo + load stub + refresh cache
uv run ccp load fixtures/graph-explorer-stub.trig   # load .trig (one branch per named graph)
uv run ccp refresh                          # project Flexo → views/cache/*.json
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
