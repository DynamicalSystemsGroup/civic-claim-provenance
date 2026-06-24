# Project Memo — Civic Claim Provenance (Hackathon, tonight)

**To:** Joshua, Christine
**From:** Zargham, Dynamical Systems Group (DSG)
**Date:** June 24, 2026
**Re:** What we're shipping, why it fits, and who owns what — BLUF in 30 sec, full read ~5 min

---

## BLUF

We're building an **assurance layer for civic AI**: take one government claim, make its chain of evidence inspectable, and keep the human official's judgment authoritative. Three points carry the pitch.

1. **Evidence doesn't verify a claim — it supports a human's judgment that the claim holds.** This audience already works this way (the official decides and signs); the reminder is that most AI civic tools quietly break it by emitting verdicts. Ours holds the line — it traces evidence, the human renders judgment.

2. **The discipline isn't new; the domain is.** Traceable chains of evidence, provenance, and assurance arguments are already how aerospace makes complex, high-stakes decisions auditable — mature, standards-based, trusted in regulated settings. We're not inventing it; we're translating a battle-tested practice to civic needs. That's what makes it both credible *and* fresh.

3. **Cryptographic identity and signed envelopes are the next layer — scoped out tonight, designed for.** Tonight's packages are inspectable and reproducible (hashes + provenance); signing that binds identity and enables independent verification ([Typed Standards](https://typedstandards.org/)) is the natural extension we've architected toward and will keep contributing to. Signing proves *integrity and identity, not correctness* — so it complements the judgment in (1), never replaces it.

---

## Why / What

The event wants tools that help government *actually deliver*, and the judges — including **Nathan Storey** (NYC data governance, OTI) — reward legibility and trust. Most teams will wrap an LLM and ship a chatbot. That's the commodity move.

Our edge is the layer above the model: **assurance**. We take one government claim and make its *chain of evidence* inspectable, while keeping the human official's judgment authoritative. The tool assembles and traces evidence; the human decides and signs. That directly answers the "don't undermine the user's authority" bar city stakeholders care about.

We do this by porting DSG's [ADCS requirements-traceability demo](https://github.com/DynamicalSystemsGroup/ADCS-lifecycle-demo) ([live](https://dynamicalsystemsgroup.github.io/ADCS-lifecycle-demo/)) from *"how do we know this requirement is satisfied?"* to *"what is the chain of evidence for this civic claim?"* Same evidence-vs-judgment split that makes aerospace V&V trustworthy — now making a civic determination legible. The demo's own principle states it: **evidence does not verify a claim; evidence supports a human judgment that the claim holds.**

**Track fit:** NYC/NYS Challenges or Service Delivery (claim-dependent), or Open Track.

### Deliverable (tight — must run end-of-night)

A working demo that takes **one human-owned judgment over a panel of atomic evidence links**, and:

1. pulls evidence from real NYC Open Data (the verified DSNY composting datasets), each reading **pinned to its source and hashed**,
2. gives every link an honest **verdict — supported / not supported / can't-tell** — each with a rationale,
3. records a named **human attestation** (person + organization) over the panel,
4. renders it all as a **graph a stakeholder can read and interrogate**,
5. checks the reasoning with **closure rules** (every claim grounded, or honestly marked can't-tell), and
6. stores it in **Flexo** (OpenMBEE) — the same code whether it runs locally or on DSG infra.

> The *can't-tell* and *not-supported* verdicts are the point, not a gap. A tool that can honestly say "the data can't settle this" is what preserves the official's authority.

---

## What / How — assemble, don't create

~80% is existing, permissively-licensed code (DSG demo is Apache-2.0; Nathan's tooling is open source). We **build only the thin civic layer, one data adapter, and the stakeholder-legible rendering.**

| Component | Source | Gives us | Status |
|---|---|---|---|
| ADCS demo (fork) | [repo](https://github.com/DynamicalSystemsGroup/ADCS-lifecycle-demo) | Assurance core: ontology, evidence binding + hashing + PROV, SHACL closure suite, forward/backward audit, `explain` chain, local + Flexo backends | **reuse** |
| civic-ai-tools / Socrata MCP | [repo](https://github.com/npstorey/civic-ai-tools) · [site](https://civicaitools.org) | Live NYC Open Data access (559 Socrata portals), evidence-package framing, Civic Claim Vocabulary | **integrate** (interop target; vocab is pre-v0.1 — align, don't depend) |
| Flexo MMS | [layer1 service](https://github.com/Open-MBEE/flexo-mms-layer1-service) · hosted remote + local Docker | Model persistence + branch-per-layer "real MMS" story; **graph-native (RDF) versioning that complements git** — for the "why not *just* git?" question, point to [Zargham's Flexo-vs-git experiments](https://github.com/Open-MBEE/flexo-conflict-resolution-policy-research/tree/main/experiments) (semantic diff/merge across models, not line-based text) | **reuse** (a `--backend=flexo` flag) |
| NYC Open Data | [opendata.cityofnewyork.us](https://opendata.cityofnewyork.us) | The actual civic evidence | **select** (Christine's call) |

**What we actually write tonight (small):** the thin civic-claim schema in place of SysMLv2 (chief); the data adapter + graph-explorer dashboard (Joshua); the analysis and the judgment calls (Christine).

**Strategic note:** Nathan's work targets *inspectable, reproducible, verifiable* evidence packages — which is what our core already produces (content hashes + PROV + re-verification), so we hold the rigor substrate his civic layers sit on. We're also **informed by his draft [Typed Standards](https://typedstandards.org/) spec** for signed, independently-verifiable packages (we're in its review group). Worth saying aloud: Typed Standards proves *integrity and identity* — a package is intact, and who signed it — and explicitly **does not judge correctness**; our human attestation supplies exactly that judgment. We keep our packages envelope-ready but don't sign tonight. Building visibly toward his layers is a feature, not pandering — he's a collaborator and in the host orbit.

---

## Christine — you own *"what the analysis says, and why anyone should care"*

- **Do the analysis.** You're the domain expert running the composting analysis on the verified datasets — the NYC knowledge and urban-policy data science are what make it credible.
- **Author the judgments.** For each link, make the call (supported / not / can't-tell) and record the *why*: the grounding, your name, and what it rests on. The schema gives those judgments their accountable form; the judgments themselves are yours.
- **Own legibility + narrative.** You're the authority on whether each link reads to a non-technical official, and on the framing (esp. for Nathan): why evidence-vs-judgment is the trust primitive civic AI is missing.
- **What Joshua brings you:** the store and the graph-explorer dashboard, so your analysis renders and interrogates without you touching the plumbing.

## Joshua — you own *"it runs, it's real, it's solid"*

- **Fork + wire.** Fork the demo, plug civic-ai-tools' Socrata MCP in as the live evidence source, build the one query → evidence-binding adapter.
- **Manage backends.** Keep the local Dataset as the robust demo path; wire the Flexo remote push as the live flourish; capture Docker compute-provenance (which container produced which evidence) as the reproducibility story.
- **Harden + deploy.** Secure it, make the end-to-end run reproducible, own the live demo surface.
- **What Christine brings you:** the claim choice and the stakeholder framing — so your pipeline points at data that matters and the output lands with judges. No guessing what to query or why.

## Zargham (chief) — *"one project, and the rigor is real"*

- **Own the seam.** Make Christine's narrative and Joshua's pipeline a single project that matches this memo — not a polished pitch in one hand and a disjoint technical demo in the other. Every beat on screen maps to a BLUF point; the story and the system are the same artifact.
- **Own the aero-context port.** Swap the SysMLv2 structural layer for the thin civic-claim vocabulary, and carry the credibility first-hand — I presented the [ADCS demo](https://github.com/DynamicalSystemsGroup/ADCS-lifecycle-demo) at **JAXA two weeks ago**, so "trusted in regulated, high-stakes settings" (BLUF #2) is testimony, not analogy.
- **Provide the core + access.** Author of the ADCS demo and a core contributor at [OpenMBEE](https://www.openmbee.org/) (the project behind Flexo MMS); I hold access to the hosted Flexo remote, so provisioning the backend and the model server is on me.
- **What I rely on from you both:** Christine's claim choice locks what we model; Joshua's pipeline makes the evidence real. I keep the two pointed at one story and own the integrity of the assurance core end-to-end.

---

## Scope guardrails — what we are NOT building tonight

- No cryptographic envelopes/signatures — that's the [Typed Standards](https://typedstandards.org/) layer we're informed by and design *toward*, not our build. **Name it, don't build it.**
- No new epistemic vocabulary — assemble from PROV / GSN / EARL / P-Plan, don't invent.
- No topological / fragility analysis — that's a reporting-layer next step; tonight is ledger reports + graph visualization.
- No organizations-as-nodes — source and attestation auspice are attributes now; explicit org nodes are an ontology next step.

## Prep before tonight (~30 min each)

- **Christine:** review the verified data assessment (the composting datasets + the verdict ledger) so you can start the analysis and the judgment calls.
- **Joshua:** clone both repos; run `uv sync && uv run python -m pipeline.runner --auto`; confirm the Socrata MCP connects and the Flexo token works.
- **Chief:** draft the civic-claim vocabulary swap + the TDD requirements skeleton.

---

## References — dive deeper as needed

*Optional. The memo stands on its own; grab a link only where you want the detail.*

**Assurance core (DSG)**
- [ADCS lifecycle demo](https://github.com/DynamicalSystemsGroup/ADCS-lifecycle-demo) · [live demo](https://dynamicalsystemsgroup.github.io/ADCS-lifecycle-demo/) — the ontology, evidence binding, SHACL closure suite, audit, and `explain` chain we're porting.

**Backend — Flexo / OpenMBEE**
- [OpenMBEE](https://www.openmbee.org/) — the project (NumFOCUS-sponsored; JPL flight + large-telescope pedigree).
- [flexo-mms-layer1-service](https://github.com/Open-MBEE/flexo-mms-layer1-service) — Flexo's root component: version-controlled CRUD over RDF models.
- [Flexo-vs-git experiments](https://github.com/Open-MBEE/flexo-conflict-resolution-policy-research/tree/main/experiments) — the "why not *just* git?" evidence: semantic diff/merge across models.

**Civic layer (Nathan Storey)**
- [civic-ai-tools](https://github.com/npstorey/civic-ai-tools) · [civicaitools.org](https://civicaitools.org) — Socrata MCP (559 portals), evidence packages, Civic Claim Vocabulary (interop target, pre-v0.1).
- [Typed Standards](https://typedstandards.org/) — signed, independently-verifiable evidence packages (the next layer; informed-by, not built tonight).

**Data**
- [NYC Open Data](https://opendata.cityofnewyork.us) — the live evidence source.
