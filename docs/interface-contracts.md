# Interface Contracts — Parallel Work Enablement

**To:** Joshua, Christine
**From:** Zargham, Dynamical Systems Group (DSG)
**Date:** June 24, 2026
**Re:** The interfaces each layer binds to, so all three of us start now without waiting on a finished ontology. Companion to the work-packages memo.

---

## Principle: freeze interfaces, not implementations

A contract fixes *the shape of what crosses a boundary*, not the internals behind it. That lets the implementation behind each boundary evolve while work on both sides proceeds in parallel. The two contracts are deliberately asymmetric in firmness:

- **Z → Joshua is HARD.** A dashboard binds to data *shape*. If the shape isn't frozen, Joshua can't build. So we freeze it now — names, ids, and the output columns of a small set of views — even though the ontology behind them is still thin.
- **Z → Christine is SOFT.** Analysis binds to *meaning*. Her content can be normalized onto the ontology after the fact, provided the *why* behind each judgment is captured durably. So she owes a capture discipline, not schema conformance.

Mapped to the work packages: Contract A is the Z→Joshua boundary (WP-1a/1c/1d → WP-3); Contract B is the Christine↔Z boundary (WP-2 → WP-1) — the *obligation* flows Z→Christine (what she must capture), the *artifact* flows Christine→Z (her notes).

---

## Contract A — Z → Joshua  (HARD: frozen now)

Everything Joshua's dashboard binds to. Z owns what's behind it; Joshua codes to the surface below and nothing deeper.

### A1 · Store & transport — the standard
- **Store: Flexo MMS Layer 1 service** (graph-native RDF, version-controlled, named graphs). This is the standard; no second store.
- **Access:** Joshua reads via the Layer-1 service's SPARQL query interface. Z provides the connection config and the exact addressing (org / repo / branch / ref); Joshua treats it as a connection string.
- **Local-first:** Joshua runs a local Flexo Layer-1 in Docker. The hosted remote is the *same contract at a different URL*. The dashboard must never assume remote availability.

### A2 · Named graphs — frozen names (contents may grow)
`g:evidence` · `g:provenance` · `g:judgments` · `g:attestation`. Names are fixed today; what's inside them fills in over time.

### A3 · Node identifiers — frozen scheme, opaque to Joshua
Stable local ids per the **canonical schema** (ontology doc): `cl:*` claim · `ev:*` evidence · `am:*` assumption · `jd:*` judgment · `at:*` attestation (· `st:*` step, optional). **Node type is an explicit property, not inferred from the id prefix.** Source authority is held as *attributes* on evidence tonight (`ds:*` source id + version + hash), not a node — a flagged hackathon simplification. **District keys are already canonicalized upstream (WP-1a) before any node reaches a view — Joshua never sees raw `('2','01')` vs `('Bronx','1')` vs `'201'` encodings.**

### A4 · View contracts — the heart (frozen output shapes)
These are the named result shapes Z guarantees to produce from the store **regardless of how the ontology evolves**. Joshua binds the dashboard to these columns; Z owns the queries that fill them.

| View | Input | Output shape (frozen columns) | Drives |
|---|---|---|---|
| `V1 nodes` | — | `{id, type∈{claim,evidence,assumption,judgment,attestation}, label, verdict∈{passed,failed,cantTell,—}}` | node rendering: color by `type`, shade by `verdict` |
| `V2 edges` | — | `{src_id, dst_id, rel∈{supports,judges,dependsOn,assumes,attestsOver}}` | graph layout |
| `V3 node_detail` | `id` | claim → `{statement, status}`; evidence → `{source_id, source_version, query_url, finding, retrieved_at, payload_sha256}`; assumption → `{statement}`; judgment → `{judges, decision, chosen, grounding, attributer, rationale, earl_outcome, pinned_as_of}`; attestation → `{attester, org_auspice, signed_at, attests_over}` | inspector panel |
| `V4 rests_on` | `id` | transitive closure of `judges`/`dependsOn`/`supports` → `[id…]` | "show everything this conclusion rests on" |
| `V5 judgments_only` | — | `[id…]` where `type∈{assumption,judgment}` | "show only the judgment calls" |
| `V6 what_would_change` *(stretch)* | `id` (a `cantTell`) | recorded missing-evidence pointer(s) | the counterfactual mode |

**Stability guarantee:** column names and value domains for V1–V5 are frozen now. Rows grow as content lands; **shapes do not change**. Any new field is *additive* (a new optional column), never a rename or a type change.

**Implementation freedom (either side may use):** Z may serve each view as a live SPARQL `SELECT` returning those columns, **or** materialize it as a JSON export of the identical shape. Joshua's dashboard reads the shape, not the mechanism — so a materialized-JSON fallback keeps the dashboard working if the live endpoint is unavailable.

**Two binding notes:** (1) **the verdict lives on the judgment node** — `V1.verdict` is populated for `judgment` nodes; a `claim` shows its governing judgment's verdict by inheritance; `evidence`/`assumption` show `—`. (2) The richer ontology (ontoGSN, P-Plan) enriches the graph *behind* these views; the V1–V5 projection is unchanged by its addition — Joshua never has to track it.

### A5 · Seed fixture — the parallelization unlock
Z delivers the **verified `evidence_supply_chain.trig`** loaded into Flexo as the seed dataset, available now. It already conforms to the canonical schema as a thin instance: its `ev:*` are Evidence (pinned to source + hash + time), its verdict-bearing `as:*` are **Judgment-typed** (prefix cosmetic; type is the property), **zero dangling `dependsOn` references**. Three of the four named graphs are populated; the declared `g:attestation` is empty, and explicit Claim/Assumption nodes are not yet present — so Joshua exercises those node/edge types against the synthetic **`graph-explorer-stub.trig`** (all five node types + every edge relation) until real content lands. Joshua builds and tests the dashboard against both fixtures on day one; richer content later changes the *data*, not the *shape*.

### A6 · Acceptance — the boundary is "done" when
Joshua can stand up local Flexo Layer-1, load the fixture, render `V1`/`V2`, drive the `V3` inspector, and apply the `V4`/`V5` filters — with **zero dependence** on the final ontology or on live data pulls.

---

## Contract B — Z → Christine  (SOFT: capture discipline, retrofit later)

Christine works in her own tools and need not touch the ontology now. The one thing she owes is that every judgment is **recoverable and explainable** at the moment we lift it onto the graph.

### B1 · What she's free to do
Use pandas / scipy / notebook however is natural. No RDF, no named graphs, no schema conformance up front. Structure the analysis as the analysis wants to be structured.

### B2 · What she must capture — the minimal durable record
A lightweight, durable note (a structured markdown or CSV table is perfect), with one row per link and per judgment:
- **Link / claim:** a short label and the plain-language statement.
- **Backing evidence:** which dataset + query — reference the verified `ev:*` ids where they apply, or her own `query_url` + timestamp where she runs something new.
- **Judgment:** the decision in one line · what she chose · the **verdict** (`passed` / `failed` / `cantTell`) · the **grounding** (precedent / governing theory / principle / doctrine — even one sentence) · **her name as attributer** · the **rationale** (the *why*, in her words) · what it depends on.

### B3 · The one hard rule inside the soft contract
**Every judgment must be explainable at logging time.** If she can say, for any judgment, *"I chose X because Y, on grounds Z,"* it normalizes onto the ontology cleanly later. The notes are the contract; the graph is the destination. The failure mode to avoid is a judgment made silently in code with no recoverable why.

### B4 · Acceptance — the boundary is "done" when
Z and Christine together can lift her notes into conformant `as:*` / `ev:*` nodes with **no missing attributer, grounding, or rationale** — i.e., her capture already satisfies the WP-1b closure rules when logged.

---

## Why this lets all three of us start at once

- **Joshua** builds against the fixture + frozen views — needs nothing from Christine and nothing from the final ontology.
- **Christine** analyzes and captures whys — needs only the pinned, already-verified datasets, not the schema.
- **Zargham** freezes A2–A4, ships the fixture (A5), then evolves the ontology *underneath the stable views* and later lifts Christine's notes (B) into the store.

The single day-one blocker we're removing: **nobody waits on the finished ontology.**

## Deliberately NOT specified yet

The full class/property ontology (Z evolves it behind the views); Christine's analytic method and link set (hers to design); the dashboard's visual design (Joshua's, within V1–V5). Fixing these now would be specifying implementations, not interfaces — exactly what this document refuses to do.

---

## Z's first moves (so the contracts go live)

1. Publish the Flexo Layer-1 connection config + addressing (A1).
2. Confirm the frozen graph names, id scheme, and the V1–V5 column shapes (A2–A4) — thin is fine, frozen is the point.
3. Load `evidence_supply_chain.trig` into Layer-1 and hand Joshua the fixture (A5).
4. Send Christine the B2 capture template.
