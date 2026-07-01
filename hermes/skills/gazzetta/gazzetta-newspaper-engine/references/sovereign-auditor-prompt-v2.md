# Sovereign Auditor v2.0 — Prompt Architecture & Pipeline Integration

## Overview

The contradiction_synthesizer.py v2.0 (deployed June 2026) ingests `docs/EDITORIAL_KNOWLEDGE_BASE.md` (~4,200 chars) as a system-instruction prefix. The KB encodes four frameworks: Soros reflexivity, Druckenmiller/Taleb asymmetric betting, Shiller narrative lifecycle, and elite financial journalism aesthetics.

## Architecture

```
docs/EDITORIAL_KNOWLEDGE_BASE.md  (14KB on disk, truncated to ~4200 chars)
         │
         ▼ _load_knowledge_base()
         │
    SYSTEM_PROMPT (f-string)
         │
    ┌────┴────────────────────────────────────┐
    │  Sovereign Auditor prompt:              │
    │  1. Identify NARRATIVE PHASE            │
    │  2. ISOLATE CONTRADICTION               │
    │  3. ASSESS ASYMMETRY                    │
    │  4. DETECT REFLEXIVITY                  │
    │  5. PROVIDE INVALIDATION CONDITION      │
    │                                         │
    │  Voice constraints baked in:            │
    │  - Clinical active verbs                │
    │  - Named agents (not "markets")         │
    │  - Probabilistic anchors                │
    │  - No passive voice, no emotional framing│
    └─────────────────────────────────────────┘
         │
         ▼ DeepSeek API
         │
    JSON response with new fields:
    - headline (active voice, agent-named)
    - narrative_phase (Germination → Collapse-Refutation)
    - they_say (media consensus)
    - reality (capital flow divergence)
    - contradiction_gap (0-100)
    - capital_volume_usd
    - asymmetry (reward-to-risk or absence)
    - reflexivity_alert (positioning-as-fundamental detection)
    - invalidation (specific price/data falsification)
         │
         ▼ assemble_story()
         │
    Story dict with new Sovereign Auditor fields
         │
         ▼ merge_stories() → atomic_write_stories()
         │
    public/data/stories.json
```

## New JSON Fields

| Field | Type | Example |
|-------|------|---------|
| narrative_phase | string | "Consensus Saturation" |
| asymmetry | string | "3:1 reward-to-risk — $500M at risk against $2B repricing" |
| reflexivity_alert | string | "Positioning itself has become fundamental — outflows beget outflows" |
| invalidation | string | "Invalidated if FXI closes above $34.50" |

These fields are stored in the story dict and tagged in `stories.json`. The `tags` field now includes the Shiller lifecycle phase string (e.g., "Consensus Saturation") in addition to narrative_tag and container.

## Test Compatibility

test_platform.py v3.0 checks `tags_index` for orphan story_ids. The phase strings in `tags` create tag entries that don't correspond to story_ids. Fix: `PHASE_TAGS` set skips these entries during validation.

```python
PHASE_TAGS = {"Germination", "Viral Expansion", "Institutional Adoption",
              "Consensus Saturation", "Peak Narrative", "Contradiction Emergence",
              "Collapse-Refutation"}
for tag, story_ids in tags_index.items():
    if tag in PHASE_TAGS:
        continue  # phase tags are metadata, not container IDs
```

## Dedup Pass (v1.1)

merge_stories() calls _dedup_new_stories() with Jaccard similarity (0.65 threshold) on tokenized headlines (lowercase, stopword-stripped). Cross-checks against existing headlines AND within the new batch. Logs skip count when near-duplicates are filtered.

## KB Deployment

The KB file at `docs/EDITORIAL_KNOWLEDGE_BASE.md` MUST exist on both local and VM filesystems. If missing at runtime, the system prompt degrades to a fallback message. Deploy the KB alongside script updates:

```bash
scp docs/EDITORIAL_KNOWLEDGE_BASE.md gazzetta-prod:/tmp/
ssh gazzetta-prod "sudo mkdir -p /opt/gazzetta-di-kyiv/docs && sudo cp /tmp/EDITORIAL_KNOWLEDGE_BASE.md /opt/gazzetta-di-kyiv/docs/ && sudo chown gazzetta:gazzetta /opt/gazzetta-di-kyiv/docs/EDITORIAL_KNOWLEDGE_BASE.md"
```

## Python F-String Pitfall

SYSTEM_PROMPT is an f-string containing JSON schema examples. All braces must be double-escaped: `{{` and `}}`. Unicode em dashes (U+2014) cause SyntaxError — use `--` instead. The KB content is injected via `{_load_knowledge_base()}`.
