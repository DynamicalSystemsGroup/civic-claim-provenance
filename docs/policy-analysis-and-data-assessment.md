# Policy Analysis Brief & Data Inventory / Assessment

**To:** Joshua, Christine
**From:** Zargham, Dynamical Systems Group (DSG)
**Date:** June 24, 2026
**Re:** The illustrative analytic payload and the verified data layer underneath it. Part 1 frames the analysis; Part 2 is the ground-truth data assessment the build stands on.

---

# Part 1 — Policy Analysis Brief

## What this is, and what it is not

This is **illustrative scaffolding for the demo, not a policy finding.** The product is the *accountable process* — an analysis whose every assumption and judgment is explicit, local, attributed, and interrogatable. The composting case is a pluggable payload, chosen because its judgment calls are unusually rich. Read every verdict below as "what an accountable analysis would record," never as "what the city should do." The demo says the same thing regardless of how the numbers come out.

## Civic context (verified)

NYC's **Zero Waste Act** (City Council, 2023; primary sponsor CM Shahana Hanif) made residential curbside composting mandatory. Citywide availability began **October 2024**; enforcement (fines) began **April 1, 2025** after a six-month grace period — tiered fines (1–8 units $25/$50/$100; 9+ units $100/$200/$300) plus a 4+-unit storage requirement. Enforcement was then **rolled back within ~3 weeks** to only buildings over 30 units with more than four warnings, until 2026. Baseline residential diversion is low (~5%).

## The analytical question, framed as a requirement-style claim

- **Descriptive claim — the tool substantiates:** residential-organics tonnage per capita varies across community districts.
- **Normative judgment — reserved to the policymaker:** whether and where that variation warrants incentives, drop-off sites, or landlord engagement. The "should" belongs to the policymaker, not the data.

The seam between these two is the whole point: the tool assembles and traces the descriptive evidence; the human owns the normative call and signs it.

## What we can and cannot say (the verified boundary)

The supply chain is **solid for *describing*** per-district residential-organics tonnage in CY2025, and **runs out exactly where *interpretation* begins.** Causal attribution ("did the mandate work?"), participation rate, alternative-channel geography, and the per-capita denominator are each blocked — and recorded as blocked, with reasons. That boundary is not a weakness of the demo; it *is* the demo.

## The evidence/judgment panel (illustrative)

A single human-owned judgment over a panel of atomic links, each a plain statement carrying an EARL verdict (`passed` / `failed` / `cantTell`) and a rationale; the machine asserts none of them. The verified verdicts are in Part 2. The load-bearing teaching beats: a `passed` *describing* claim (per-district 2025 tonnage) sitting beside a `cantTell` *interpretive* claim about the very same numbers; a clean `failed` (participation rate); and a `cantTell` deferred to a named human (the denominator).

---

# Part 2 — Data Inventory & Assessment

## Provenance of this assessment

Live-verified **read-only** against public NYC Open Data via anonymous SODA/SoQL on **2026-06-24** by an independent verification thread. Every record carries an exact, reproducible `query_url`; load-bearing scalar payloads carry SHA-256 hashes; the machine-readable ledger (`evidence_supply_chain.trig`) parses as a three-named-graph dataset with **zero dangling references**. 19 evidence records, 11 judgment records.

## Confirmed datasets (build on these)

| Role | id | Granularity / key | Note |
|---|---|---|---|
| Spine (tonnage) | `ebb7-mvp5` | month × (borough_id, communitydistrict) | `month` is TEXT `"YYYY / MM"`; 59 districts |
| Alt-channel | `6yag-pnij` | fiscal year, citywide | no geography; DSNY col = 0 since FY2021 |
| Participation | `tiyn-ajjm` | fiscal-year cohort, citywide | "Historic", frozen at Oct-2024 |
| Denominator (CD-native) | `xi7c-iiu2` | 59 CDs, decennial 1970–2010 | residents; newest vintage 2010 |
| Denominator (2020-capable) | `9ji4-nien` | CD, LEP table w/ `community_district_population` | 2020 via newer ACS period |
| Geometry | `5crt-au7u` (+ `6ak9-vek3` water) | `boro_cd = borough_id×100 + CD` | excludes/flags 12 JIAs |
| Geometry (operational) | `i6mn-amj2` | DSNY districts | congruent to CDs |

## Spine schema highlights — `ebb7-mvp5`

- Monthly, by (borough_id, communitydistrict); **59** districts; coverage **1990/01 → 2026/05**.
- `resorganicstons` (residential food waste, DSNY code 45) is the composting field: **null in 21,552 of 25,060 rows, and never literally `0`** — absence is honestly unmeasured, not zero.
- Total DSNY organics = `resorganicstons` + `schoolorganictons` + `leavesorganictons` + `xmastreetons` + `otherorganicstons`.
- Per-district CY2025 is complete: **708 = 59 × 12, zero missing.**

## Verdict ledger (verified — tally: 6 passed · 4 cantTell · 1 failed)

| Judgment | Outcome | Why (short) |
|---|---|---|
| `as:perdistrict-2025` — per-district CY2025 analysis supported | **passed** | 708 = 59×12, zero missing |
| `as:null-not-zero` — absence read as unmeasured | **passed** | 21,552 nulls, 0 exact-zeros |
| `as:composite-key` — (borough_id, communitydistrict) required | **passed** | CD numbers recur across boroughs |
| `as:sanitation-eq-cd` — DSNY districts == CDs | **passed** | column note + DSNY Districts both state congruent |
| `as:join-key-normalization` — joinable after canonicalizing keys | **passed** | three encodings; join only after normalizing |
| `as:geometry-available` — CD geometry exists (`5crt-au7u`) | **passed** | MultiPolygon present; filter 12 JIAs |
| `as:mandate-worked` — Oct-2024 step-up = mandate working | **cantTell** | leaves vanish after 2024/04, fold into organics — confounded |
| `as:channel-attribution` — alt-channel → CD | **cantTell** | `6yag-pnij` citywide-annual, no geography |
| `as:time-window` — CY2025 as steady state | **cantTell** | rollout transient; districts still climbing ~4× over the year |
| `as:percapita-denominator` — which population denominator | **cantTell** | deferred — needs human judgment (see below) |
| `as:participation-rate` — participation rate by district/time | **failed** | `tiyn-ajjm` is availability counts, not set-out rates; frozen |

## Caveats to carry downstream (7)

1. **`month` is text, not a date** (`"YYYY / MM"` with spaces). Range/`starts_with` ordering works; date functions don't. Parse before temporal math.
2. **`resorganicstons` is never literally `0`** — clean evidence that absence = null, but you cannot distinguish "active route, nothing collected" from "no route." Both are null.
3. **Leaves discontinuity precedes the stated date** — column note says leaves stopped "since Oct-2024," but the last non-null leaves anywhere is **2024/04**; the whole fall-2024 season is already absent. The definitional break is real and slightly earlier than the narrative.
4. **Three incompatible district-key encodings** — tonnage `('2','01')`, population `('Bronx','1')`, geometry `'201'`. Naive joins silently mis-match; canonicalize once at the schema layer (WP-1a).
5. **`6yag-pnij` field names differ from earlier labels** — live fields are `tons_collected_dsny` / `tons_collected_non_dsny`. Semantics match; labels don't.
6. **Participation data is frozen** — `tiyn-ajjm` is "Historic," ends FY2024, and is availability counts, not rates.
7. **2020 CD population isn't cleanly on-portal** — CD-native `xi7c-iiu2` stops at 2010 (~8.17 M vs ~8.8 M citywide in 2020, a material undercount). This is *why* the denominator is deferred. 12 JIAs (parks/airports) belong to no CD — filter from joins.

## Open decision — per-capita denominator

The data cannot settle it: currency (2020/ACS) vs CD-native cleanliness (2010 decennial), and residents vs households. Per our discipline this is a **named human judgment on stated grounds, not a script default.** Recommendation: keep it a **live deferred node in the demo** that shows the options and says "a human must choose, here's the trade"; if the per-capita view needs a number, use the 2010 CD-native figure as an explicitly-labeled placeholder carrying its own staleness caveat.
