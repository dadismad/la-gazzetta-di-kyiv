# debug_flows.py — $5B Default Diagnostic

End-to-end trace of the flow amount pipeline. Use when:
- Stories on the live site all show the same dollar amounts
- Need to verify db_to_json.py JOIN is working
- Want to check flow distribution before deploy

## What it prints

1. All flows in gazzetta.db with amount_b + direction + category — flags $5.0B defaults
2. All story_flow_links — which stories map to which flows with headlines
3. Compiled site/data/stories.json capital_flow values for linked stories
4. Distribution analysis — count per amount, % at $5.0B default
5. Root cause detection — is the bug in flows table, compiler, or frontend?

## Usage

```bash
cd ~/projects/gazzetta-di-kyiv && .venv/bin/python scripts/debug_flows.py
```

## Example output (before fix)

```
Flows at $5.0B: 9/12 = 75%
═══ ROOT CAUSE: FLOWS TABLE ═══
Most flows have $5.0B because the data source defaults to 5.0.
```

## Example output (after fix)

```
Flows at $5.0B: 0/12 = 0%
Distribution: $0.8B(1) $2.1B(1) $2.7B(1) $3.2B(1) $4.2B(1) $4.8B(1) $6.5B(1) $11.5B(1) $12.5B(1) $34.0B(1) $88.0B(1) $300.0B(1)
```

## Key insight

The diagnostic is read-only — it never modifies the database. Use it to confirm the fix worked before deploying.
