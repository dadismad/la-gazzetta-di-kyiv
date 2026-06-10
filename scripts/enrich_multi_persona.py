#!/usr/bin/env python3
"""
enrich_multi_persona.py — Generate C-Suite/Quant/Degen blocks for stories lacking multi_persona.

Uses DeepSeek API to generate three persona perspectives per story:
- C-Suite: Macro context for capital allocators
- Quant: Flow telemetry with raw metrics
- Degen/Execution: Action triggers with directional bias

Reads gazzetta.db, generates blocks, writes back.
"""

import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT / "gazzetta.db"
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
if not API_KEY:
    try:
        providers = json.loads(os.environ.get("custom_providers", "[]"))
        for p in providers:
            if "deepseek" in p.get("name", "").lower():
                API_KEY = p.get("api_key", "")
                break
    except (json.JSONDecodeError, KeyError):
        pass
API_URL = "https://api.deepseek.com/v1/chat/completions"

if not API_KEY:
    print("[enrich_multi_persona] DEEPSEEK_API_KEY not set — skipping", file=sys.stderr)
    sys.exit(0)


def llm_generate(system_prompt, user_prompt, max_tokens=800):
    """Call DeepSeek API and return generated text."""
    import urllib.request
    
    payload = json.dumps({
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.4,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"}
    }).encode("utf-8")
    
    req = urllib.request.Request(API_URL, data=payload, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    })
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            content = result["choices"][0]["message"]["content"]
            return json.loads(content)
    except Exception as e:
        print(f"  ✗ API error: {e}", file=sys.stderr)
        return None


def generate_personas(story):
    """Generate C-Suite, Quant, and Degen blocks for a story."""
    headline = story.get("headline", "")
    body = story.get("body", story.get("description", story.get("thesis", "")))
    sector = story.get("sector", "markets")
    cf = story.get("capital_flow", {})
    amount = cf.get("amount_formatted", "?" )
    direction = cf.get("direction", "?")
    asset_class = cf.get("asset_class", "?")
    
    system = """You are the Gazzetta di Kyiv multi-persona intelligence engine. 
Generate three persona perspectives for the given story. Output valid JSON only.

Each persona block must have: headline (short, 8-12 words), body (2-3 sentences), and a persona-specific field:
- c_suite: implication (1 sentence, boardroom-ready strategic implication)
- quant: metrics (dict with: signal ("WATCH"/"BUY"/"SELL" based on flow direction), confidence_pct (50-85), pace (1.0-3.0), correlation (e.g. "WTI/SPX: -0.3"))
- degen: signal (emoji + BUY/SELL/WATCH + asset ticker, e.g. "🟡 WATCH BTC"), entry (price estimate or "N/A"), stop (price or "N/A")

Respond with ONLY this JSON:
{"c_suite": {"headline": "...", "body": "...", "implication": "..."},
 "quant": {"headline": "...", "body": "...", "metrics": {"signal": "...", "confidence_pct": N, "pace": N.N, "correlation": "..."}},
 "degen": {"headline": "...", "body": "...", "signal": "...", "entry": "...", "stop": "..."}}"""

    user = f"""Story: {headline}
Body: {body[:500]}
Sector: {sector}
Capital Flow: {amount} {direction} {asset_class}

Generate C-Suite, Quant, and Degen persona blocks."""
    
    return llm_generate(system, user, max_tokens=600)


def main():
    print("[enrich_multi_persona] Starting...")
    
    if not DB_PATH.exists():
        print(f"  ✗ {DB_PATH} not found", file=sys.stderr)
        sys.exit(1)
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    # Find stories without multi_persona
    rows = conn.execute("""
        SELECT id, full_json FROM stories 
        WHERE multi_persona_raw IS NULL OR multi_persona_raw = ''
    """).fetchall()
    
    orphans = []
    for row in rows:
        story = json.loads(row["full_json"])
        if not story.get("multi_persona"):
            orphans.append(story)
    
    print(f"  Found {len(orphans)} orphan stories (no multi_persona)")
    
    if not orphans:
        print("  Nothing to do — all stories have multi_persona")
        conn.close()
        return
    
    enriched = 0
    for i, story in enumerate(orphans):
        sid = story.get("story_id", story.get("id", f"unknown_{i}"))
        headline = story.get("headline", "")[:60]
        print(f"  [{i+1}/{len(orphans)}] {headline}...", end=" ", flush=True)
        
        personas = generate_personas(story)
        if personas and all(k in personas for k in ["c_suite", "quant", "degen"]):
            story["multi_persona"] = personas
            
            # Update DB
            conn.execute(
                "UPDATE stories SET full_json = ?, multi_persona_raw = ? WHERE id = ?",
                (json.dumps(story, ensure_ascii=False), json.dumps(personas, ensure_ascii=False), sid)
            )
            conn.commit()
            enriched += 1
            print("✓")
        else:
            print("✗ (API failed, will retry next run)")
        
        # Rate limit: 1 call per second
        time.sleep(0.5)
    
    conn.close()
    print(f"\n  ✓ Enriched {enriched}/{len(orphans)} orphan stories")
    
    if enriched > 0:
        # Rebuild JSON
        import subprocess
        subprocess.run([sys.executable, str(PROJECT / "scripts" / "db_to_json.py")], check=False)
        print("  ✓ Rebuilt stories.json from DB")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
