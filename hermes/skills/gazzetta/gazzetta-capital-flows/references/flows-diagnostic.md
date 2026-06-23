# Flows Page Diagnostic — Correct DOM Selectors

## Symptom

User reports "capital flow analysis doesn't work" on `flows.html`. Browser_snapshot shows no content.

## Quick Check

```js
// In browser_console on flows.html, after 3s async wait:
[CAPITAL_FLOWS_DATA?.length, document.querySelectorAll('.flow-row').length]
```

## Correct Selectors

| What | Selector | Notes |
|------|----------|-------|
| Flow data items | `CAPITAL_FLOWS_DATA.length` | Global array populated by `fetchFlows()` |
| Rendered flow rows | `document.querySelectorAll('.flow-row')` | **NOT `.flow-item`** — that class doesn't exist |
| Container element | `document.getElementById('flowsList')` | **NOT `[data-compat="flowsList"]`** — that's a compatibility shim only |
| Hero stat placeholder | `StaticText "—"` in snapshot | Gets populated by `updateMastheadFlows()` after data loads |

## Possible States

| CAPITAL_FLOWS_DATA | .flow-row count | Diagnosis |
|---|---|---|
| 0 | 0 | `flows.json` not fetched — check network, check `/data/flows.json` returns 200 |
| 199 | 0 | Data loaded but `renderCapitalFlows()` not called — check `#flowsList` exists in DOM |
| 199 | 167 | Working — some flows deduplicated by `aggregateFlows()` |
| undefined | 0 | `app.js` not loaded — check script tag hash reference vs GCS |
