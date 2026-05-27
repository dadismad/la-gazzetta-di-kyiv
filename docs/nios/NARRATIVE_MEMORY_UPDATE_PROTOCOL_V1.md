# Narrative Memory Update Protocol (NMUP) v1

After each publish cycle, store these artifacts:

1. Thesis outcome snapshot
- thesis_id
- published_at
- confidence_at_publish
- invalidation_conditions

2. Outcome window (24–72h)
- validation_status: validated / mixed / invalidated
- what moved first (asset class)
- what contradicted the thesis

3. Pattern learning
- worked_pattern (e.g., actor+incentive framing)
- failed_pattern (e.g., overfitting single-source narrative)
- correction applied next cycle

4. Storage targets
- `data/nios/memory_log.jsonl` (append-only)
- `data/nios/pattern_library.json`

5. Hard rule
- If thesis invalidates, next-cycle content must include explicit post-mortem note.
