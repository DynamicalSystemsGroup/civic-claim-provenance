# Cowork Task — Verify the NYC Composting Evidence Supply Chain (read-only)

*Paste this into Claude Cowork with Chrome access. It runs as a parallel, independent check on what data is actually available and what it can and cannot support. We are NOT trying to reach a conclusion about composting policy — we are establishing a realistic data supply chain with every modeling assumption and interpretive judgment made explicit and local, so each can be ledgered as RDF and reasoned over on its own.*

## Your role and the standard of work

You are verifying, hands-on, claims another analyst made from dataset *metadata only*. They could read schemas but could not reach the live API. Your job is to confirm or refute their findings against live data and to inventory two datasets they couldn't finish. Treat "I can't tell from the available data" as a first-class, valuable result — it is often the correct finding, and recording *why* is the point.

## Hard constraints (read-only)

- Public NYC Open Data only. **No** sign-ins, account creation, app-token signup, form submissions, downloads to disk beyond what you need to read, purchases, posting, or changing any setting. If any page requires authentication or a login wall, **stop and report** rather than working around it.
- Prefer the SODA/SoQL API over the web UI for reproducibility. Resource endpoint pattern: `https://data.cityofnewyork.us/resource/{id}.json` with SoQL params (`$select`, `$where`, `$group`, `$limit`, `$order`). Anonymous access is fine within rate limits; do not register for a token.
- For **every** data retrieval, record an **Evidence Record** (schema below). For **every** modeling or interpretive decision, record an **Assumption Record**. One decision per record — keep them atomic and local.
- Do not draw policy conclusions. The deliverable is the supply chain and its limits.

## Record schemas

**Evidence Record:** `id` (stable local, e.g. `ev:ebb7-2025-resorg`) · `dataset_id` · `title` · `landing_page_url` · `query_url` (exact) · `retrieved_at` (UTC) · `rows_returned` · `payload_sha256` (hash the raw response text if you can) · `finding` (1–2 sentences of what the data showed).

**Assumption / Judgment Record:** `id` (e.g. `as:percapita-denominator`) · `decision` (the question) · `options_considered` · `chosen` (or "deferred — needs human judgment") · `rationale` · `earl_outcome` (`passed` = doable from available data / `failed` = rejected as unsupportable / `cantTell` = data cannot adjudicate) · `depends_on` (evidence record ids).

## Verification targets

### A. `ebb7-mvp5` — DSNY Monthly Tonnage (the spine)
- **A1.** Confirm coverage reaches the latest months (metadata claims through `2026 / 05`) and recent months are populated.
- **A2.** For calendar year 2025, count how many of the 59 borough+district combinations have a **non-null** `resorganicstons` value. List any that are missing. *This decides whether a per-district 2025 analysis is even possible.* → EARL on "per-district 2025 residential-organics analysis is supported."
- **A3.** Confirm **null ≠ zero**: find district-months where `resorganicstons` is null vs. exactly `0`, and confirm nulls are returned as null, not coerced. → evidence for the "absence is unmeasured, not zero" link.
- **A4.** Test the **leaves reclassification**: the `leavesorganictons` field description says DSNY stopped separately collecting leaves after the Oct-2024 citywide expansion. Pull `leavesorganictons` and `resorganicstons` for several districts across Jul 2024–May 2025. Does leaves drop to null/0 while residential organics steps up around Oct 2024? → evidence for "did the mandate work? = `cantTell` by definitional discontinuity."
- **A5.** Confirm the key is composite: that `communitydistrict` values repeat across boroughs and must be paired with `borough`/`borough_id`.

### B. `6yag-pnij` — DSNY Other Organics (alternative channels)
- **B1.** Pull all rows; confirm it is annual by fiscal year and **citywide only** (no district, no month).
- **B2.** Confirm post-FY2021 behavior (DSNY Green Market column near 0 recently; non-DSNY nonprofit column continues at hundreds–thousands of tons). Note the magnitudes.
- **B3.** → EARL on "alternative-channel diversion can be attributed to a community district" (expected `cantTell`; record the reason).

### C. Participation dataset — `dsny-organics-collection-participation`
- **C1.** Locate it on the portal; capture its dataset id, fields, and granularity.
- **C2.** → EARL on "this provides a participation *rate* by district/time" vs. "only program-availability counts (households/buildings/schools reached)." This determines whether participation can ever complement tonnage as evidence.

### D. Per-capita denominator — an explicit interpretive judgment (do NOT silently pick one)
- **D1.** Identify candidate residential-population-by-community-district sources (e.g., decennial "New York City Population By Community Districts," ACS tables, DCP population). Capture ids/urls.
- **D2.** For each: vintage, geography (community district vs. something needing a crosswalk), and whether it counts residents or households.
- **D3.** Record the denominator choice as an Assumption Record with `chosen: deferred — needs human judgment`, listing options and tradeoffs. The whole point is that this judgment is visible and local, not buried in a script.
- **D4.** Verify the `ebb7-mvp5` claim that **sanitation districts correspond to community districts** — find authoritative confirmation or flag any mismatch (this is load-bearing for the join).

### E. Map geometry (stretch)
- **E1.** Confirm a community-district boundary geometry source exists for visualization; capture id/url. No analysis needed.

## Output

1. **Markdown report** with: (a) a one-paragraph "what is and isn't possible" summary, (b) a table of Evidence Records, (c) a table of Assumption/Judgment Records.
2. **Machine-readable block** for quadstore ingestion: emit the records as triples (Turtle is fine) using **named graphs** to separate concerns —
   - graph `<g:evidence>` for retrievals,
   - graph `<g:provenance>` for query URLs / timestamps / hashes (`prov:wasDerivedFrom`, `prov:generatedAtTime`),
   - graph `<g:judgments>` for assumptions and interpretive decisions (`earl:outcome` ∈ {`earl:passed`,`earl:failed`,`earl:cantTell`}, with a free-text rationale).
   Use small, stable local identifiers and a minimal vocabulary; don't invent a large ontology. The aim is that each evidence node and each judgment node can be selected and reasoned over independently.
3. **Surprises / blockers** section: anything missing, moved, auth-walled, or inconsistent with the metadata findings above — reported, not worked around.

## What success looks like

Not "the analysis is done." Success is: every link we'd put in the evidence chain is now backed by a live retrieval or honestly marked `cantTell` with a recorded reason, and every modeling judgment (denominator, district key, null handling, channel attribution, time window) sits as its own inspectable record. Strong, practical understanding of the data supply chain — including, especially, where it runs out.
