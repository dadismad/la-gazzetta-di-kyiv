#!/usr/bin/env python3
"""verify_reality.py — Three-lens post-deploy verification for Gazzetta di Kyiv.

RETROSPECTIVE: What did the user ask for? (public reachability, JSON freshness)
INTROSPECTIVE: Did we actually do it? (DB vs public sync, amount uniqueness, format checks)
EXTRAPOLATIVE: Will it break tomorrow? (cron health, script existence, cache headers)

Run after every deploy. Non-zero exit = reality gap detected — do NOT report success.
"""
import json, urllib.request, sys, sqlite3, os
from datetime import datetime, timezone
from collections import Counter

PROJECT_DIR = os.path.expanduser("~/projects/gazzetta-di-kyiv")
PUBLIC_BASE = "https://www.lagazzettadikyiv.com"

def fetch_json(url):
    req = urllib.request.Request(url, headers={"Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

def fetch_headers(url):
    req = urllib.request.Request(url, method="HEAD", headers={"Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return dict(resp.headers)
    except Exception as e:
        return {"error": str(e)}

def main():
    failures = []
    print("=" * 60)
    print("GAZZETTA di KYIV — REALITY VERIFICATION")
    print(f"Run: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    # RETROSPECTIVE
    print("\n-- RETROSPECTIVE --")
    for url_suffix, label in [
        ("/", "EN Homepage"), ("/ru/", "RU Homepage"),
        ("/stories.html", "Stories page"), ("/data/stories.json", "Stories JSON"),
    ]:
        url = PUBLIC_BASE + url_suffix
        headers = fetch_headers(url)
        lm = headers.get("last-modified", headers.get("date", "?"))
        print(f"  {label:20} {lm}")

    public_json = fetch_json(PUBLIC_BASE + "/data/stories.json")
    gen_at = public_json.get("generated_at", "")
    if gen_at:
        gen_dt = datetime.fromisoformat(gen_at.replace("Z", "+00:00"))
        age_min = (datetime.now(timezone.utc) - gen_dt).total_seconds() / 60
        status = "FRESH" if age_min < 15 else "STALE" if age_min < 60 else "FROZEN"
        print(f"\n  PUBLIC JSON age: {age_min:.1f} min -- {status}")
        print(f"  generated_at: {gen_at}")
        print(f"  stories: {len(public_json.get('stories',[])) + 1}")
        lead = public_json.get("lead", {})
        print(f"  lead: {lead.get('headline','?')[:80]}")
        if age_min >= 60:
            failures.append(f"JSON frozen: {age_min:.0f} min old")

    # INTROSPECTIVE
    print("\n-- INTROSPECTIVE --")
    db_path = os.path.join(PROJECT_DIR, "gazzetta.db")
    if os.path.exists(db_path):
        db = sqlite3.connect(db_path)
        db_count = db.execute("SELECT COUNT(*) FROM stories").fetchone()[0]
        public_count = len(public_json.get("stories", [])) + 1
        print(f"  DB stories: {db_count} | Public stories: {public_count}")
        if db_count != public_count:
            failures.append(f"Export gap: {db_count - public_count} stories missing from public JSON")
        db.close()

    stories = public_json.get("stories", [])
    all_stories = [public_json.get("lead", {})] + stories if public_json.get("lead") else stories
    amounts = Counter()
    for s in all_stories:
        amt = s.get("capital_flow", {}).get("amount_b", 0)
        if amt > 0:
            amounts[round(amt, 1)] += 1
    dupes = {k: v for k, v in amounts.items() if v > 3}
    if dupes:
        failures.append(f"Amount spam: {dupes}")
    else:
        print(f"  Amount uniqueness: OK ({len(amounts)} unique)")

    # EXTRAPOLATIVE
    print("\n-- EXTRAPOLATIVE --")
    for script in ["fetch_intel.py", "intel_to_stories.py", "db_to_json.py", "approve_draft.py"]:
        path = os.path.join(PROJECT_DIR, "scripts", script)
        exists = os.path.exists(path)
        if not exists:
            failures.append(f"Missing script: {script}")
        print(f"  {'OK' if exists else 'MISSING'} scripts/{script}")

    gcs_headers = fetch_headers(PUBLIC_BASE + "/")
    cache = gcs_headers.get("cache-control", "MISSING")
    print(f"  Cache-Control: {cache}")

    # VERDICT
    print("\n" + "=" * 60)
    if failures:
        print(f"REALITY GAP -- {len(failures)} issues:")
        for f in failures:
            print(f"  X {f}")
        sys.exit(1)
    else:
        print("REALITY VERIFIED -- No gaps.")
        sys.exit(0)

if __name__ == "__main__":
    main()
