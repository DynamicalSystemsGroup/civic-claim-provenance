# analysis/ — Christine's workspace (Controller / C)

Your layer. Do the analysis however it wants to be done — pandas, scipy, a notebook,
whatever is natural. No RDF, no schema conformance needed *here*.

The one thing you owe (the C→M seam): capture every judgment so it's **explainable at
logging time** — *"I chose X because Y, on grounds Z."* Use
[`../fixtures/capture-template.md`](../fixtures/capture-template.md): one row per link,
each carrying decision · chosen · verdict (`passed`/`failed`/`cantTell`) · grounding ·
your name as attributer · rationale.

When a set of rows is ready, hand them to Zargham (M) — he lifts them into a conformant
`fixtures/*.trig`, loads Flexo, and refreshes the cache; your findings then appear in
Joshua's dashboard with **zero UI change**.

Pinned datasets to analyze (verified): `ebb7-mvp5` (DSNY Monthly Tonnage, the spine),
`6yag-pnij`, `tiyn-ajjm`, `5crt-au7u` (CD geometry); population candidates `xi7c-iiu2` /
`9ji4-nien`. See `../docs/policy-analysis-and-data-assessment.md`.
