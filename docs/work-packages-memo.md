# Project Memo — Work Packages, Dependencies, Responsibilities

**To:** Joshua, Christine
**From:** Zargham, Dynamical Systems Group (DSG)
**Date:** June 24, 2026
**Re:** The work breakdown for tonight — who owns what, and what depends on what. Refines the role blocks in the project memo; updated to fold in the completed live data verification.

---

## The split: three layers, one per person

Christine owns the **content** — what the analysis says. Zargham owns the **structure** — how knowledge is represented and what makes it sound. Joshua owns the **surface** — how it's stored, served, and seen. This maps one-to-one onto our node taxonomy: content fills the claim / evidence / assumption / judgment nodes; structure defines the schema and the closure rules those nodes must obey; surface is the store and the dashboard that render them.

**The integrity boundary that matters:** Christine authors the judgments, but the *form* those judgments must take — an assumption naming its attributer and grounding, a verdict carrying a rationale, evidence and judgment living in separate graphs — is Zargham's schema imposing discipline on her content. Joshua's dashboard renders the result and asserts nothing of its own. No layer can silently launder another's.

---

## Status — live data verification complete (read this first)

An independent in-browser thread (Cowork, read-only) verified the data supply chain against live NYC Open Data and returned a self-ledgered package — 19 evidence records, 11 judgment records, three named graphs, zero dangling references. What it changes for this plan:

**Locked — now `passed`, build on these:**
- Spine confirmed: `ebb7-mvp5` (DSNY Monthly Tonnage). Per-district CY2025 residential-organics analysis is fully supported — 708 = 59 districts × 12 months, **zero missing**.
- `null ≠ zero` holds emphatically (0 literal zeros across 25,060 rows) — absence is honestly unmeasured.
- District key joins to confirmed-congruent community-district geometry.

**Unblocked:**
- The **Cowork → Christine** handoff is satisfied — Christine knows which links are backable vs `cantTell` and can start WP-2 now against pinned data.
- Dataset ids pinned for plumbing: `ebb7-mvp5` (spine), `6yag-pnij` (alt-channel), `tiyn-ajjm` (participation), `5crt-au7u` (CD geometry); population candidates `xi7c-iiu2` / `9ji4-nien`.

**Clarified — these are the demo's load-bearing beats, not problems:**
- `mandate-worked` → `cantTell`: separately-coded leaves vanish after 2024/04 and fold into general organics as universal availability lands — a definitional discontinuity, with the baseline corrupted *before* the policy date.
- `participation-rate` → `failed`: `tiyn-ajjm` is availability counts, not set-out rates, and is frozen at FY2024. A clean "evidence rejected" node.
- `time-window` → `cantTell`: CY2025 is a rollout transient (districts still climbing ~4× over the year), so even the supported describing-claim describes a system mid-rollout, not equilibrium.

**One decision returned to us:** the per-capita population denominator (see *Open decisions*).

---

## Work packages

### WP-0 — Integration & narrative spine — *Zargham (shared)*
The seam. Owns the invariance contract (the notebook says the same thing regardless of what the data returns), the storyboard, and the demo runtime; ensures content + structure + surface compose into one artifact that matches the memo.
*Acceptance:* a coherent end-to-end run where every demo beat maps to a node in the graph.

### WP-1 — Knowledge representation & assurance — *Zargham*
The epistemic spine — aerospace/control + ADCS + OpenMBEE, ported to the civic payload.
- **1a — Schema:** the **canonical node set** (claim / evidence / assumption / judgment / attestation — *source held as attributes tonight*, see Roadmap) across the four named graphs (`g:evidence` / `g:provenance` / `g:judgments` / `g:attestation`), **defined authoritatively in the ontology doc** which the interface contract's V1 and A3 cite; the civic-claim vocabulary swapped in where SysMLv2 sat; alignment to Nathan's Civic Claim Vocabulary as interop target. **Now also owns the canonical district-key + JIA exclusion as the single join contract** — verification found three incompatible encodings (tonnage `('2','01')`, population `('Bronx','1')`, geometry `'201'`) plus 12 Joint Interest Areas in no CD; this normalization lives here *once*, never re-implemented in WP-2 or WP-3. Adopt the verified `.trig` vocabulary and named-graph shape (minimal `prov:`/`earl:`/`dct:`/`rdfs:` + local `p:`, stable ids; the declared `g:attestation` graph is empty in the fixture) rather than inventing one.
- **1b — Closure rules:** machine-checkable invariants — no claim without supporting evidence or an explicit `cantTell`; no assumption without an attributer and a grounding; evidence/judgment type separation enforced; every verdict carries a rationale; no orphan nodes; attestation attributed to a person. The verification package is a ready-made conformance fixture — its zero-dangling-`dependsOn` result already shows one of these invariants holding on real content.
- **1c — Flexo / MMS backing:** the quadstore and named-graph persistence on **Flexo (OpenMBEE) from the start** — the store, not an afterthought. Identical code whether Flexo runs in a local Docker container or as a DSG-hosted service; local-vs-remote is a deployment choice, not a pre-commitment.
- **1d — Interrogation primitives:** the traversal/explain queries — *why this link*, *evidence or judgment*, *who decided on what grounds*, *what would change this verdict*.
*Acceptance:* the closure suite passes a well-formed analysis and **fails a malformed one**; `explain` returns a dereferenceable chain for any node.

### WP-2 — Domain analysis & judgment authoring — *Christine*
The content, and the reason it's credible — NYC expertise, the lived use case, urban-policy data science.
- **2a — Claim framing:** state the analytical question as a requirement-style claim and decompose it into a panel of atomic, layperson-checkable links. Frame the supported describing-claim honestly as *describing a system mid-rollout* — CY2025 is a transient, not steady state — i.e. a `passed` describing-claim sitting beside a `cantTell` interpretive-claim about the very same numbers.
- **2b — Analysis:** perform the computation over the now-confirmed spine (`ebb7-mvp5`, per-district CY2025 residential organics), consuming the 19 verified evidence records; produce the per-link findings.
- **2c — Assumption & judgment authoring:** for each link that needs one, author the assumption or interpretive judgment and supply what the schema demands — the attributer, the grounding (precedent / governing theory / principle / doctrine), and the EARL verdict with its rationale.
- **2d — Legibility review:** acceptance authority on whether each link reads to a non-technical municipal stakeholder.
*Acceptance:* a populated panel where every node satisfies WP-1b and every judgment is attributable to her with stated grounds.

### WP-3 — Application, infrastructure & traceability dashboard — *Joshua*
The surface — data engineering, deployment, dashboarding.
- **3a — Data plumbing:** wire the Socrata MCP / live pulls for the pinned ids (`ebb7-mvp5`, `6yag-pnij`, `tiyn-ajjm`, `5crt-au7u`, + the chosen population source); land Christine's analysis outputs and the verified evidence records into the store Zargham's schema defines. Apply the WP-1a canonical key — do not re-implement key handling here.
- **3b — Traceability dashboard:** the interactive graph view — color by node *type*, shade by *verdict*, filterable ("show only the judgment calls," "show everything this conclusion rests on"); interrogation modes wired to WP-1d.
- **3c — Deploy & harden:** reproducible end-to-end run and the demo surface, running against a **local Flexo instance** by default; the DSG-hosted service is the same code — a deployment swap, not a dependency.
*Acceptance:* a non-technical viewer can traverse the chain, distinguish evidence from judgment at a glance, and reach any node's support — on real stored data, deployed.

---

## Dependencies

**Handoff contracts — the interfaces matter more than the boxes:**
- **Cowork → Christine — ✓ satisfied.** Verified evidence/provenance records delivered; backable-vs-`cantTell` status known per link. Christine is unblocked.
- **Christine → Zargham:** analysis outputs and judgments conforming to the schema (each judgment carries attributer + grounding + verdict + rationale). The closure rules are the gate — non-conforming content fails the suite, visibly.
- **Zargham → Joshua:** a populated, closure-validated quadstore plus the interrogation query primitives, **including the canonical district-key contract** (one normalization, applied once at the schema layer). Joshua consumes a stable graph contract, not raw data he has to interpret.

**Critical path:** WP-1a (schema) is the long pole — both Christine's authoring (2c) and Joshua's dashboard (3b) bind to it, so it freezes early, even in a thin form. Then content and surface build in parallel against the frozen schema. The closure rules (1b) must be runnable before WP-2 can be called done, since they are its acceptance gate. Integration (WP-0) runs continuously; final assembly and the Flexo push come last. The Cowork dependency that previously gated WP-2 is now cleared, so Christine's only remaining upstream is the WP-1a schema plus her own analysis (2b → 2c).

| WP | Owner | Blocked by | Blocks |
|---|---|---|---|
| 1a schema | Zargham | — | 2c, 3a, 3b |
| 1b closure rules | Zargham | 1a | WP-2 acceptance |
| 1c Flexo backing | Zargham | 1a | 3a |
| 1d interrogation | Zargham | 1a | 3b |
| 2a/2b analysis | Christine | ~~Cowork records~~ ✓ delivered | 2c |
| 2c judgment authoring | Christine | 1a, 2b | 3a (populate) |
| 3a data plumbing | Joshua | 1a, 1c | 3b |
| 3b dashboard | Joshua | 1a, 1d, 3a | demo |
| 3c deploy & harden | Joshua | 3b | demo |
| 0 integration | Zargham | all | demo |

**One-line read:** freeze the schema first; everything else parallelizes behind it.

---

## Open decisions (needed before/at kickoff)

- **Per-capita denominator (`as:percapita-denominator`) — owner: Zargham, with team input.** The data cannot settle it: CD-native population is clean but stops at the 2010 decennial (`xi7c-iiu2`, ~8.17M vs ~8.8M citywide in 2020 — a material undercount), while a 2020/ACS figure is current but messier (`9ji4-nien` or off-portal DCP). Per our own discipline this is a named human judgment on stated grounds, not a script default. **Recommendation:** keep it as a *live deferred node in the demo* — one that shows the options and says "a human must choose, here's the trade" — and, if the per-capita view needs a number, use the 2010 CD-native figure as an explicitly-labeled placeholder carrying its own staleness caveat.

---

## From plan to backlog

Each sub-package (1a–1d, 2a–2d, 3a–3c) is sized to become a single tracked issue, with its acceptance line as the definition of done. The seven downstream caveats from verification attach as constraints on the relevant issues — most onto WP-1a (key canonicalization) and WP-2b (analysis): `month` is text not date; null can't separate "no route" from "route, nothing collected"; the leaves break precedes Oct-2024; three district-key encodings; `6yag-pnij` field names differ from earlier labels; participation data is frozen at FY2024; 2020 CD population isn't cleanly on-portal.

---

## Roadmap (named tonight, not built)

Two simplifications are deliberate and should be stated, not hidden — naming them is on-brand for the method:

- **Source / organization authorities as explicit nodes — ontology-layer next step.** Tonight source authority is a bare attribute on evidence (`source@version` + hash + time). Modeling organizations/authorities as first-class nodes is well-trodden in knowledge-graph engineering; we cite it as the next ontology step rather than spend tonight on it.
- **Topological / fragility / sensitivity analysis — reporting-layer next step.** Tonight the reporting layer is ledger-like reports and graph visualizations. Computing robustness as topology (support multiplicity, articulation points, confidence-weighted cut sets) is the natural payoff and the strongest future feature, but it is next-step, not tonight.
