# Assembled Ontology & Doctrine — the Epistemic Layer

**To:** Joshua, Christine
**From:** Zargham, Dynamical Systems Group (DSG)
**Date:** June 24, 2026
**Re:** The vocabulary WP-1a *assembles* (does not invent) and the doctrinal precedents we cite. The interface contracts bind to the shape this defines.

---

## Stance: assemble, don't invent

As in the ADCS demo, we add **no novel epistemic vocabulary**. Every term is borrowed from an established standard. Our only local terms are thin glue — a small `p:` property namespace and stable local ids (`ev:*`, `as:*`, `ds:*`, `at:*`) — plus a SKOS reskin for the audience. The civic-claim layer swaps in where SysMLv2 sat; the epistemic core is unchanged from the aerospace work, which is the point: the rigor is borrowed and battle-tested.

## The core principle (the invariant)

Evidence does not verify a claim; evidence supports a **human judgment** that the claim holds. The graph makes each judgment explicit, local, attributed, and interrogatable. The machine assembles and traces; the human decides and signs.

## Authoritative source of truth (ASoT), not single source of truth

We do not claim to be the single source of truth — in a policy setting that is impossible and dishonest, because every input is stewarded by some other authority (DSNY, the Census, a statute, a doctrine). Our graph is an **authoritative source of truth**: it renders judgments that are authoritative *because a named human committed to them*, while openly recording the external authorities its inputs draw on. This is part of the value proposition, not a limitation. (It also applies one level up: the schema itself is ASoT — it cites PROV/GSN/EARL/P-Plan rather than inventing. "Assemble, don't invent" is ASoT for the ontology.)

Two kinds of authority live in the graph:
- **Deciding authority** — the human who renders a judgment or signs an attestation (`prov:wasAttributedTo` an Agent). Internal.
- **Source authority** — the external steward of an input, pinned at a version (`prov:wasDerivedFrom` an Entity@version). External.

So every claim is at once **authoritative** (a deciding authority committed to it) and **contingent** (that commitment was pinned to specific source versions at a specific time). Three things become first-class structure rather than caveats: **pinned dependency** (evidence binds to `source@version` + content hash + retrieval time — the fixture already does this), **contingent validity** (a judgment holds *as of* its pinned inputs), and **staleness → re-run** (when a source's authoritative version advances — `prov:wasRevisionOf` the pin — every downstream judgment is mechanically flagged stale).

**Hackathon simplification (flagged):** tonight source authority is a *bare attribute* on evidence (source id + version + hash + time), not a node. Organizations/authorities as first-class nodes are well-trodden in knowledge-graph engineering and are a **next step in the ontology layer**, not a focus tonight.

**The natural payoff (out of scope tonight):** once support is a graph, robustness is topology — a claim resting on a single load-bearing path is fragile (an articulation point from collapse), while a claim with independent complementary supports is robust. We do not aim to make every claim robust; we aim to make fragilities **topologically discoverable and semantically interpretable**. That sensitivity/fragility analysis is a **next step in the reporting layer**; tonight the reporting layer is ledger-like reports and graph visualizations.

## Traceability — three constructs, not "bidirectional"

What safety-critical RTM practice calls *bidirectional traceability* bundles three distinct things. Separating them shows the two directions are **not** co-equal in an analysis setting.

1. **Local closure invariants** — per node, SHACL-checkable, no traversal. Every judgment node (assumption-adequacy or evidence-sufficiency) has ≥1 supporting evidence; every assumption names an attributer and a grounding; evidence and judgment occupy separate graphs; every verdict carries a rationale; no orphan nodes; attestation attributed to a person.
2. **Forward traceability = grounding = the integrity claim** — whole graph, **MUST pass**. Rooted at the conclusion, traverse toward sources: every assertion terminates, on *every* branch, in raw evidence (with a sufficiency judgment) or an explicit `cantTell`. No assertion floats. This generalizes the local rule to the whole network and *is* the integrity claim about the larger analysis: "fully grounded or honestly uncertain, everywhere."
3. **Backward traceability = utilization / parsimony** — **attested subgraph only**. From each node toward the conclusion: does it reach? Over the whole exploration this is the *wrong* check — an analysis legitimately pulls data it discards, and honest dead ends are not defects. Over the subgraph the human attests and presents, it is an **anti-evidence-laundering** check: every source placed before a policymaker must be load-bearing, no impressive pile that doesn't connect. *(Open decision: blocking vs advisory — see end.)*

The asymmetry is the honest civic translation: **forward over the conclusion-rooted graph (mandatory); backward over the attested subgraph only (no dead weight).**

## Composition — forward-chaining is PROV entity identity

A step's output assertion becoming a later step's evidence input is native PROV: one `prov:Entity` that is `prov:wasGeneratedBy` step N and `prov:used` by step N+1. At the argument layer that same entity is the `gsn:Goal` discharged by step N and the artifact cited by step N+1's `gsn:Solution`. PROV entities are the connective tissue between per-step GSN arguments — promotion is **entity reuse, not a new relation**. The network composes precisely because each step is a well-formed little assurance case and the joins between them are identity.

## The stack — four standards, four concerns

| Layer | Standard | Concern it carries |
|---|---|---|
| Spine | **PROV-O** | what derived from what; attribution (`prov:wasAttributedTo` = who made the judgment); time |
| Process | **P-Plan** | analytic steps, input/output variables, ordering — the pipeline skeleton |
| Argument | **ontoGSN** | why an assertion is warranted: Goal ← Strategy ← Solution, in context of Assumption / Justification |
| Verdict | **EARL** | outcome of the judgment: `earl:passed` / `earl:failed` / `earl:cantTell` + rationale |

The adequacy/sufficiency split lands on GSN's two assurance-claim-point categories, same as ADCS: assumption **adequacy** → `gsn:Assumption` (+ its `gsn:Justification`); evidence **sufficiency** → the defensibility of the `gsn:supportedBy` link, carried as a `gsn:Justification`. EARL ships `cantTell` as a first-class outcome — the JAXA move transfers untouched.

## Canonical schema — the authoritative spec (V1 / A3 cite this)

One closed node set, one edge set, one graph set. The interface contract's V1 node types and A3 id scheme reference this verbatim; this section is the schema's authoritative definition. **Node type is an explicit property, not inferred from an id prefix** (prefixes below are conventional).

**Nodes**

| Type | id prefix | Assembled from | Role |
|---|---|---|---|
| Claim | `cl:` | `gsn:Goal` | the assertion; its status is *derived*, never intrinsic |
| Evidence | `ev:` | `gsn:Solution` + `prov:Entity` | a reading pinned to a `source@version` (source held as attributes — see ASoT simplification) |
| Assumption | `am:` | `gsn:Assumption` | a modeling choice, subject to an adequacy judgment |
| Judgment | `jd:` | `earl:Assertion` (carries `earl:outcome`) | assesses assumption-*adequacy* or evidence-*sufficiency*; **carries the verdict** + rationale + grounding + attributer + contingency |
| Attestation | `at:` | `prov:Activity` + signing `prov:Agent` | a deciding authority signs over a subgraph; carries **attester (human name)** + **organization auspice** as attributes — the auspice is the hook for the org-node ontology next step |
| Step *(optional)* | `st:` | `p-plan:Step` / `gsn:Strategy` | an analytic operation; render as node or as edge metadata — not in the V1 enum tonight |

**Edges**

- `supports` — evidence → claim (`gsn:supportedBy`)
- `judges` — judgment → {claim \| assumption \| evidence} (what it assesses)
- `dependsOn` — judgment → {evidence \| assumption} (what the verdict rests on; the fixture relation)
- `assumes` — claim/step → assumption (`gsn:inContextOf`)
- `attestsOver` — attestation → subgraph
- forward-chaining is **entity identity, not an edge**: a claim that is one step's output is the same `prov:Entity` later `prov:used` as evidence downstream.

**Graphs** — `g:evidence` (evidence nodes) · `g:provenance` (source-version pins + derivation) · `g:judgments` (the argument layer: claims, assumptions, and the judgments over them) · `g:attestation` (attestations). This is the verified `.trig` shape and the nanopublication shape.

**Where the verdict lives (resolves the placement question):** on the **judgment** node. A claim is never "passed" absolutely — its displayed status is the outcome of its governing judgment, *as of* the pinned source versions, and re-runnable if they move. Both capture (Christine's notes) and rendering (the dashboard) read the verdict from the judgment, not the claim; a claim shows its governing judgment's verdict by inheritance.

**Fixture mapping:** the verified `.trig` is a thin but ASoT-faithful instance — its `ev:*` are Evidence (already pinned to source + hash + time), its verdict-bearing `as:*` are **Judgment-typed** (the prefix is cosmetic; type is the property that matters), and its cited `ds:*` are source attributes on evidence. It does not yet contain explicit Claim, Assumption, or Attestation nodes; those are added as the model fills in.

## Doctrinal precedents — assemble, don't invent (also our credibility story)

- **ICD 203 (IC Analytic Standards).** The intelligence community's tradecraft rule *is* the evidence/judgment separation: it mandates distinguishing underlying information from analytic judgment and expressing calibrated, explained confidence. For a civic audience this does what aerospace does for JAXA — "not novel; this is how high-stakes analysis is held accountable." Doctrine, not an ontology: adopt the concepts, bind via SKOS, cite as grounding.
- **Nanopublications.** An established open standard whose unit is exactly {assertion, provenance, publication-info} as three named graphs — our quadstore shape. Cite as lineage: "we didn't invent the three-graph structure."
- **Admiralty / NATO source grading** (reliability A–F × credibility 1–6) — optional, tiny SKOS vocabulary to annotate evidence sufficiency with a recognizable label. SEPIO (biomedical evidence-supports-assertion ontology) is heavier prior art for the same idea — mention-only.

## SKOS — two jobs

1. **Bind** concepts across the four ontologies where they aren't already matched (`skos:exactMatch` / `skos:closeMatch`).
2. **Reskin** for the urban-data-science audience: `skos:prefLabel` on the friendly term, `skos:exactMatch` to the formal one. The triples stay rigorous; the dashboard reads plainly.

| Formal | Accessible surface label |
|---|---|
| `gsn:Goal` / assertion | Finding / Claim |
| `gsn:Solution` (+ PROV entity from data) | Evidence / Source reading |
| `gsn:Strategy` / P-Plan step | Analysis step |
| `gsn:Assumption` | Assumption |
| `gsn:Justification` | Why this is enough |
| `earl:passed` / `failed` / `cantTell` | Supported / Not supported / Can't tell yet |
| judgment node | Judgment call |
| `prov:wasAttributedTo` | Decided by |
| `prov:wasDerivedFrom` (source@version) | Source — as of [date] |

The formal terms live in the triples; the friendly terms are a SKOS overlay the dashboard renders — rigor and legibility without choosing between them.

## Open design decisions (returned for Zargham's call)

1. **Backward traceability — blocking or advisory?** Recommendation: blocking, scoped strictly to the attested subgraph.
2. **ICD 203 / nanopub framing — surfaced in the demo narrative, or internal grounding only?**
