# Master Architecture Audit Prompt

This is the six-phase forensic audit framework used to audit the Gazzetta di Kyiv system on 2026-06-19. Load this as the execution plan whenever the user says "audit the system" or "debug everything."

The full prompt is at `/Users/alexstocchi/lagazzettadikyiv/MASTER_AUDIT_PROMPT.md` in the project root.

## Phase Structure

0. **Pre-flight** — Load skills (`gazzetta-newspaper-engine`, `gazzetta-cloud-infrastructure`, `gazzetta-knowledge-index`), read SOP
1. **Infrastructure Discovery** — Map all GCP resources, VM services, file ownership, permissions
2. **Pipeline Architecture Audit** — Read every script line by line, trace data lineage from source to reader, map every write/read/overwrite
3. **Bottleneck Investigation** — Resource limits, concurrency races, API rate limits, single points of failure, silent failure modes
4. **Live Site Verification** — Data freshness, data quality, rendering, console errors
5. **Cross-Validation** — Three independent subagents (SRE, Pipeline Engineer, Systems Architect) audit the same evidence
6. **Report** — Executive summary, architecture diagram, numbered findings, data flow map, fix plan, verification checklist

## Key Rules

- Verify, don't assume. Every claim backed by a tool call result.
- Read scripts line by line. Do not trust documentation or comments.
- Trace data, not intentions. Follow the bytes.
- Cross-validate. Multi-agent consensus is evidence.
- Prioritize by reader impact. Site dead = CRITICAL. Wasted CPU = HIGH.
- SOP rules are binding throughout the audit.
