# Project Starter Kit — DSG × Civic Claim Provenance

*A traceability/assurance layer for civic AI: take a government claim, make its chain of evidence inspectable, and keep the human official's judgment authoritative. We port DSG's aerospace requirements-traceability discipline (ADCS / OpenMBEE / Flexo) to a civic analysis, grounding it in real NYC Open Data. The demo's product is the **accountable process**, not any particular result.*

This kit is what a teammate needs to start. Each document stands alone; the order below is the fastest path in.

## The five core documents

1. **Project memo** — `hackathon-project-memo.md`
   Why/what, hackathon fit, the deliverable, the BLUF, and the three talking points. Start here for orientation and the pitch.

2. **Policy analysis brief & data assessment** — `policy-analysis-and-data-assessment.md`
   The illustrative analytic payload (the composting case) and, underneath it, the verified data layer — confirmed dataset ids, the EARL verdict ledger, and the caveats to carry downstream. The concrete problem and what is actually real.

3. **Assembled ontology & doctrine** — `ontology-and-doctrine.md`
   The epistemic vocabulary we assemble rather than invent (PROV-O, P-Plan, ontoGSN, EARL), the three traceability constructs, the doctrinal precedents (ICD 203, nanopublications), the SKOS reskin for legibility, and the **canonical schema** (the authoritative node/edge/graph spec the interface cites) under an **authoritative-source-of-truth** principle. How reasoning is represented.

4. **Interface contracts** — `interface-contracts.md`
   How the three of us work in parallel from day one: the hard Z→Joshua store/view contract (Flexo Layer 1 + frozen view shapes + the verified `.trig` as seed fixture) and the soft Z→Christine capture-discipline contract. How to start building before the ontology is finished.

5. **Work breakdown & responsibilities** — `work-packages-memo.md`
   WP-0…WP-3 with owners, acceptance criteria, dependencies, the critical path (freeze the schema first), and the seed for a backlog. Who does what, and in what order.

## Suggested reading order

Orientation → concrete problem → representation → how to start → who does what:
**1 → 2 → 3 → 4 → 5.** For building immediately, jump to 4; for the pitch, 1 and the Part-1 brief in 2.

## Supporting material (inputs, not core docs)

- **`cowork-data-verification-task.md`** — the read-only verification task spec handed to the parallel Cowork thread.
- **Verification package** — `HANDOFF_nyc_composting_verification.md`, `nyc_composting_evidence_supply_chain.md`, and `evidence_supply_chain.trig`. The data-layer ground truth: 19 evidence records, 11 judgment records, three named graphs, reproducible query URLs, payload hashes. The `.trig` is also the seed fixture referenced in the interface contracts.
- **`graph-explorer-stub.trig`** — a small synthetic, clearly-illustrative graph that exercises all five node types and every edge relation, so the dashboard can be built against day-one data the thin verification fixture doesn't yet cover.

## Status at kit assembly (2026-06-24)

Data layer verified and dataset ids pinned. The schema is unified across the pack: one canonical node set (claim / evidence / assumption / judgment / attestation) defined authoritatively in doc 3 and cited by the interface contract; the verdict lives on the judgment node; the graph is an *authoritative* source of truth (it cites and pins its sources), not a single one. All three layers can start in parallel against the interface contracts and the seed fixtures.

**Genuinely open decisions** (carried in the docs, for the team): the per-capita denominator (doc 2; recommend a live deferred node); whether backward traceability is blocking or advisory; whether ICD 203 / nanopublication framing is surfaced in the narrative (doc 3).

**Named as next-step, not built tonight:** organizations/authorities as explicit nodes (ontology layer); topological / fragility analysis (reporting layer); cryptographic signing (Typed Standards). Source and attestation auspice are attributes for now.
