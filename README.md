# Civic Claim Provenance

**An assurance layer for civic AI.** Make a claim's chain of evidence inspectable, and
keep the human's judgment authoritative — so that independent, citizen-produced analysis
can earn institutional-grade legitimacy.

> **Evidence does not verify a claim — evidence supports a human's judgment that the
> claim holds.** Most AI civic tools quietly break this by emitting verdicts. This one
> holds the line: it traces the evidence; the human renders the judgment.

### Why — institutional legitimacy for citizen science

The traceability and assurance discipline that lets aerospace V&V and government
determinations be trusted — auditable evidence, judgments owned by named people, no
laundering of opinion into fact — is exactly what independent, **citizen science**
lacks. Make a citizen scientist's chain of evidence inspectable, keep every judgment
explicit and attributable, and the same rigor that legitimizes an institution can
legitimize a citizen's claim. The analysis here is itself citizen science: an
independent study of public NYC sanitation data, made institutionally legible.

### ▶ Live demo — https://dynamicalsystemsgroup.github.io/civic-claim-provenance/

A [Marimo](https://marimo.io) notebook, exported to static HTML and served from GitHub
Pages. It renders the chain of evidence two ways: a **graph** (nodes colored by type,
shaded by verdict, edges labeled by relation) and a **judgments** table (every human
call, explainable at a glance).

The discipline isn't new; the domain is. Traceable chains of evidence, provenance, and
assurance arguments are how aerospace makes high-stakes decisions auditable. We port that
battle-tested practice from aerospace — a public demonstration can be found in the [ADCS
lifecycle demo](https://github.com/DynamicalSystemsGroup/ADCS-lifecycle-demo) — to a civic
determination over real NYC Open Data.

## The case — NYC residential-organics composting

We trace one concrete claim: *per-district residential-organics composting **rate**
(diversion and capture) is describable from DSNY data* — all 59 community districts,
CY2021–present, with no structural data gaps. Each evidence reading is pinned to its
source and hashed; each interpretive link gets an honest verdict with a named rationale;
and **Christine Rodríguez** signs over the panel.

The honesty is the point — the verdicts include **can't-tell**, not just *supported*:

- The post-mandate **rate increase is visible** in the data → *supported*, but **strictly
  as a describing claim**.
- **Causal attribution** of that increase to the composting mandate → **can't-tell**:
  confounders are unresolved, and the data cannot settle a causal question.
- The **35.8% compostable fraction** (the capture-rate denominator) is a **named
  assumption** from the 2023 Waste Characterization Study, applied uniformly across
  districts because no per-district breakdown is published — a stated caveat, not a silent
  default.

A tool that can say *"the data can't settle this"* is what preserves the official's
authority.

### Public data sources

Two real sources, both public:

| Source | Reference | Role |
| --- | --- | --- |
| DSNY Monthly Tonnage | NYC Open Data [`ebb7-mvp5`](https://data.cityofnewyork.us/resource/ebb7-mvp5.json) | **The spine** — per-district residential organics; 708 district-months (59 × CY2021–present), zero structural nulls; diversion rate is a direct quotient |
| DSNY 2023 Waste Characterization Study | DSNY published report (PDF) | Citywide compostable fraction (35.8%) — the capture-rate denominator |

Absence is honestly unmeasured: the organics tonnage fields are null where unreported and
**never a literal `0`** — "no data" is not "zero tons."

## How it works

```
Christine's analysis (C)            real data science over the pinned datasets
  → capture rows                    every judgment explainable at logging time
  → coerced into the ontology (M)   fixtures/nyc-composting-real.trig
  → Flexo MMS quadstore (M)         ccp load   (one branch per named graph)
  → SPARQL projection (M)           ccp refresh → views/cache/*.json
  → Marimo notebook (V)             notebooks/dashboard.py reads the cache
  → GitHub Pages (V)                static export; no live server in the demo
```

**The demo reads a pre-computed JSON cache** (`views/cache/*.json`) — the single interface
between the Model and the View. Flexo is upstream of the cache only, so the demo runs with
no server and no Flexo. The cache fills two ways, producing identical shapes: offline from
a `.trig` (`ccp seed-offline`), or from Flexo via SPARQL (`ccp refresh`).

Reasoning is checked by **closure rules** (`ccp check`): no claim without supporting
evidence or an explicit can't-tell; every verdict carries a rationale; evidence and
judgment kept in separate named graphs; attestation attributed to a person.

## The authoritative source of truth

Behind the cache sits the thing that makes the chain trustworthy: a single
**authoritative source of truth (ASoT)** — the version-controlled Flexo model. Everything a
reader sees (the JSON cache, the graph, the judgments table) is a *projection* of that one
governed model, never an independent copy. Change the model and regenerate; nothing
downstream can drift from it or assert something the model doesn't contain. That is exactly
why the cache is the *only* interface between layers — it is generated, never authored.

Crucially it is an *authoritative* source of truth, not a naive *single* one: the model
does not claim to be where the facts originate — it **cites and pins its upstream sources**
(the DSNY datasets, hashed and dated) and records who judged what, on what grounds. It is
the accountable apex of a chain of custody, not an oracle. That distinction is what
institutional accountability needs: an auditor can start from any conclusion and walk back
through one governed structure to the pinned evidence and the named human who signed it.

This is not a civic invention. Complex, distributed, *institutionally accountable* systems
in aerospace and defense are engineered this way — the discipline behind model-based
systems engineering and doctrines like the **[Modular Open Systems Approach
(MOSA)](https://www.cto.mil/sea/mosa/)**, where
many vendors and institutions integrate against open standards and a shared authoritative
reference rather than divergent private copies, so the whole system stays auditable across
organizational seams. We bring the same ASoT discipline to a civic determination: one
governed, openly-standardized model that a citizen, an official, and an auditor can all
point to and trust.

## The assembled ontology — borrow, don't invent

Following the ADCS demo, we add **no novel epistemic vocabulary**. We assemble
established, off-the-shelf standards — each contributing one layer of the argument — and
add only thin local glue (a small `p:` property namespace and stable node ids). Borrowing
rather than inventing is what makes the epistemics both credible *and* legible.

| Layer | Standard | Contributes |
| --- | --- | --- |
| Provenance | [PROV-O](https://www.w3.org/TR/prov-o/) | what was derived from what, attributed to whom, when |
| Process | [P-Plan](http://purl.org/net/p-plan) | the analytic steps, their inputs/outputs, and ordering |
| Argument | [ontoGSN](https://fortiss.github.io/OntoGSN/) | goal ← strategy ← solution, with assumptions/justifications as first-class context |
| Verdict | [EARL](https://www.w3.org/TR/EARL10-Schema/) | `passed` / `failed` / `cantTell`, each carrying a rationale |
| Legibility | [SKOS](https://www.w3.org/TR/skos-reference/) | an audience reskin so the graph reads to a non-technical stakeholder |

Doctrinal precedent: **ICD 203** (the US intelligence community's analytic-tradecraft
standard that keeps evidence and judgment separate) and
[**nanopublications**](https://nanopub.net/) (assertion + provenance + publication-info as
three named graphs). The five canonical node types — claim, evidence, assumption,
judgment, attestation — and five relations are the thin civic projection over this stack.

## Built on

This is mostly existing, permissively-licensed work; we build only the thin civic layer
over it.

- **[OpenMBEE Flexo MMS — Layer-1 service](https://github.com/Open-MBEE/flexo-mms-layer1-service)**
  — the graph-native (RDF), version-controlled quadstore with named graphs that backs the
  Model. Runs locally via the
  [flexo-mms-deployment](https://github.com/openmbee/flexo-mms-deployment) Docker stack.
  Part of [OpenMBEE](https://www.openmbee.org/) (NumFOCUS-sponsored; JPL flight + large-
  telescope pedigree). On *"why not just git?"*, see the semantic diff/merge
  [Flexo-vs-git experiments](https://github.com/Open-MBEE/flexo-conflict-resolution-policy-research/tree/main/experiments).
- **[ADCS lifecycle demo](https://github.com/DynamicalSystemsGroup/ADCS-lifecycle-demo)**
  ([live](https://dynamicalsystemsgroup.github.io/ADCS-lifecycle-demo/)) — the assurance
  core we port from aerospace requirements-traceability: ontology, evidence binding +
  hashing + PROV, the SHACL closure suite, forward/backward audit, and the `explain` chain.
- **[NYC Open Data](https://opendata.cityofnewyork.us)** and the **NYC Department of
  Sanitation (DSNY)** — the real civic evidence (the two sources above).
- **Assembled epistemic standards** — PROV-O, P-Plan, ontoGSN, EARL, SKOS (+ ICD 203,
  nanopublications). See [The assembled ontology](#the-assembled-ontology--borrow-dont-invent).
- **Civic interop** — [civic-ai-tools](https://github.com/npstorey/civic-ai-tools)
  ([site](https://civicaitools.org)) for Socrata access and the Civic Claim Vocabulary;
  [Typed Standards](https://typedstandards.org/) for signed, independently-verifiable
  packages (the next layer — designed toward, not built here; it proves integrity and
  identity, not correctness, which is exactly what the human judgment supplies).

## Run it

```bash
uv sync

# Build the cache + preview the demo (no Flexo needed)
uv run ccp seed-offline --trig fixtures/nyc-composting-real.trig   # → views/cache/*.json
uv run ccp check fixtures/nyc-composting-real.trig                 # closure rules
uv run marimo run notebooks/dashboard.py                          # the demo, locally

# Static export (what GitHub Pages serves)
uv run marimo export html notebooks/dashboard.py -o _site/index.html --include-code
```

The real-MMS path (Model owner; local Flexo in Docker — no token needed, see
[`flexo/README.md`](flexo/README.md)):

```bash
./flexo/init.sh                                  # provision + load + refresh
uv run ccp load fixtures/nyc-composting-real.trig
uv run ccp refresh                               # Flexo → views/cache/*.json
```

Deployment is automatic: pushing to `main` runs
[`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) — seed the cache from the
real fixture, export the notebook, publish to Pages.

## How we built it — the process is the product

Built by a **three-person team in a ~2-hour hackathon**, working fully in parallel under a
**Model · View · Controller** split, each person driving their own Claude Code:

- **M — Model — Zargham:** the Flexo MMS deployment, the assembled ontology, and the view
  contract (`flexo/`, `ontology/`, `views/`, `cli/`).
- **V — View — Joshua:** the Marimo notebook + GitHub Pages deploy (`notebooks/`).
- **C — Controller — Christine:** the real composting analysis, coerced into the ontology
  (`analysis/`, `fixtures/`).

We could put three people in parallel from minute one because we **froze the seam first**:
the JSON cache (`views/cache/*.json`) is the *only* interface between layers, so V built
against its shape while M built the pipeline behind it and C produced the content — nobody
blocked on anyone. That discipline — freeze the interface, own your layer, make every
judgment attributable — is the **same accountability the tool itself is about**. The
contract and the rules of engagement are in [`CLAUDE.md`](CLAUDE.md) and
[`docs/BRANCHING.md`](docs/BRANCHING.md). (`ui/` and `server/` are a superseded
React/FastAPI prototype, retained until removed.)

## Status & roadmap

Shipped: a real composting-rate analysis, closure-validated, projected through Flexo to a
static Marimo notebook on GitHub Pages. **Named as next steps, not built:** cryptographic
signing (Typed Standards), organizations/authorities as first-class nodes, and topological
/ fragility analysis over the graph.

---

*Dynamical Systems Group. Ports DSG's aerospace requirements-traceability discipline
(ADCS · OpenMBEE · Flexo) to a civic analysis grounded in real NYC Open Data.*
