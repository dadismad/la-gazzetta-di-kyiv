#!/usr/bin/env python3
"""
translate_content.py v2.0 — Resilient Translation with Checkpointing

Translates EN stories → RU using DeepSeek API.
- Batches of 3 (avoids timeout)
- Checkpoints to gazzetta.db after each batch
- Resumes from last checkpoint on restart
- Writes data/stories_ru.json and site/data/stories_ru.json

Usage:
  DEEPSEEK_API_KEY=sk-... python3 scripts/translate_content.py
  python3 scripts/translate_content.py --resume   (continue from checkpoint)
  python3 scripts/translate_content.py --dry-run   (show what would be translated)
"""

import json, os, sys, time, sqlite3, requests
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT / "gazzetta.db"
DATA = PROJECT / "data"
SITE_DATA = PROJECT / "site" / "data"
BATCH_SIZE = 3
CHECKPOINT_TABLE = "translation_checkpoint"

def get_api_key():
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if key: return key
    # Try Hermes config
    try:
        cp = os.environ.get("custom_providers", "")
        for p in json.loads(cp):
            if "deepseek" in p.get("name", "").lower():
                return p.get("api_key", "")
    except: pass
    return ""

def init_checkpoint_table(conn):
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {CHECKPOINT_TABLE} (
            story_id TEXT PRIMARY KEY,
            translated_at TEXT,
            status TEXT DEFAULT 'done'
        )
    """)
    conn.commit()

def get_checkpointed(conn):
    rows = conn.execute(f"SELECT story_id FROM {CHECKPOINT_TABLE} WHERE status='done'").fetchall()
    return {r[0] for r in rows}

def save_checkpoint(conn, story_id):
    conn.execute(
        f"INSERT OR REPLACE INTO {CHECKPOINT_TABLE} (story_id, translated_at, status) VALUES (?, ?, 'done')",
        (story_id, datetime.now(timezone.utc).isoformat())
    )
    conn.commit()

def translate_text(text, api_key):
    if not text or not isinstance(text, str): return text
    try:
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": f"Russian translation, professional financial analyst tone. Keep all numbers, tickers, symbols intact. Return ONLY the translation:\n\n{text[:400]}"}],
                "temperature": 0.3, "max_tokens": 500
            },
            timeout=15
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip()
        return text
    except Exception as e:
        print(f"    API error: {e}")
        return text

def main():
    dry_run = "--dry-run" in sys.argv
    resume = "--resume" in sys.argv

    api_key = get_api_key()
    if not api_key and not dry_run:
        print("ERROR: DEEPSEEK_API_KEY not set")
        sys.exit(1)

    # Load EN and RU data
    with open(DATA / "stories.json") as f:
        en_data = json.load(f)

    ru_path = DATA / "stories_ru.json"
    if ru_path.exists():
        with open(ru_path) as f:
            ru_data = json.load(f)
    else:
        ru_data = {"generated_at": "", "lead": None, "stories": []}

    # Initialize checkpoint DB
    conn = sqlite3.connect(str(DB_PATH))
    init_checkpoint_table(conn)
    checkpointed = get_checkpointed(conn)

    # Build RU lookup
    ru_by_id = {s["story_id"]: s for s in ru_data.get("stories", [])}

    # Find stories needing translation
    en_all = [en_data.get("lead")] if en_data.get("lead") else []
    en_all.extend(en_data.get("stories", []))

    to_translate = []
    for s in en_all:
        if not s: continue
        sid = s.get("story_id", "")
        if sid in checkpointed:
            continue  # Already done in this or previous run
        ru_s = ru_by_id.get(sid)
        if ru_s and any(0x0400 <= ord(c) <= 0x04FF for c in str(ru_s.get("headline", ""))):
            # Already has Cyrillic — mark checkpointed
            save_checkpoint(conn, sid)
            continue
        to_translate.append((s, ru_s if ru_s else None))

    if not to_translate:
        print("All stories already translated! ✓")
        conn.close()

        # Ensure RU data is synced to site/
        import shutil
        shutil.copy(str(ru_path), str(SITE_DATA / "stories_ru.json"))
        print("Synced to site/data/stories_ru.json")
        return

    print(f"Stories to translate: {len(to_translate)}")
    if dry_run:
        for s, _ in to_translate[:5]:
            print(f"  {s['story_id'][:60]}...")
        conn.close()
        return

    # Process in batches
    total = len(to_translate)
    done = 0
    for batch_start in range(0, total, BATCH_SIZE):
        batch = to_translate[batch_start:batch_start + BATCH_SIZE]
        print(f"\n── Batch {batch_start//BATCH_SIZE + 1}: {len(batch)} stories ──")

        for i, (en_s, ru_s) in enumerate(batch):
            sid = en_s["story_id"]
            headline = en_s.get("headline", "")[:80]
            print(f"  {done+i+1}/{total}: {headline}...")

            # Translate key fields
            fields = {
                "headline": en_s.get("headline", ""),
                "summary": en_s.get("summary", ""),
                "they_say": en_s.get("they_say", ""),
                "reality": en_s.get("reality", ""),
            }

            if ru_s:
                # Update existing RU entry
                for field, text in fields.items():
                    if text and not any(0x0400 <= ord(c) <= 0x04FF for c in str(ru_s.get(field, ""))):
                        ru_s[field] = translate_text(text, api_key)
                ru_s.pop("_untranslated", None)
            else:
                # Create new RU entry
                new_ru = dict(en_s)
                for field, text in fields.items():
                    if text:
                        new_ru[field] = translate_text(text, api_key)
                new_ru.pop("_untranslated", None)
                ru_data["stories"].append(new_ru)

            save_checkpoint(conn, sid)
            time.sleep(0.3)

        done += len(batch)

        # Save RU data after each batch
        ru_data["generated_at"] = datetime.now(timezone.utc).isoformat()
        with open(ru_path, "w") as f:
            json.dump(ru_data, f, ensure_ascii=False, indent=2)

        # Sync to site
        import shutil
        shutil.copy(str(ru_path), str(SITE_DATA / "stories_ru.json"))

        cyrillic = sum(1 for s in ru_data["stories"] if any(0x0400 <= ord(c) <= 0x04FF for c in str(s.get("headline", ""))))
        print(f"  Saved: {cyrillic}/{len(ru_data['stories'])} Cyrillic headlines")

    conn.close()

    # Final count
    cyrillic_final = sum(1 for s in ru_data["stories"] if any(0x0400 <= ord(c) <= 0x04FF for c in str(s.get("headline", ""))))
    print(f"\n✓ Translation complete: {cyrillic_final}/{len(ru_data['stories'])} stories with Cyrillic")
    print(f"  Next run: python3 scripts/translate_content.py --resume")

if __name__ == "__main__":
    main()
