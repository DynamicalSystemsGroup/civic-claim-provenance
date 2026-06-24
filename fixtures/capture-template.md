# Judgment capture template (Contract B2)

One row per link / judgment. Every judgment must be explainable AT LOGGING TIME:
"I chose X because Y, on grounds Z." No silent judgments in code.

| link/claim | backing evidence (ev:* id or query_url+ts) | decision | chosen | verdict (passed/failed/cantTell) | grounding (precedent/theory/principle) | attributer (your name) | rationale (the why) | depends-on |
|---|---|---|---|---|---|---|---|---|
| e.g. variation describable | ev:demo-tonnage | Is CY2025 tonnage describable? | supported | passed | complete series 708=59x12 | C. Analyst | zero missing across 25,060 rows | ev:demo-tonnage |

When complete, Z lifts these rows into conformant `jd:*`/`ev:*` nodes in a `.trig`,
then: `uv run ccp load <file>.trig && uv run ccp refresh` — the dashboard updates with zero UI change.
