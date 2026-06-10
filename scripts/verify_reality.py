#!/usr/bin/env python3
"""verify_reality.py — Three-lens verification script for Gazzetta di Kyiv deployments.

RETROSPECTIVE: What did the user ask for?
INTROSPECTIVE: Did we actually do it?
EXTRAPOLATIVE: Will it break tomorrow?

Run after every deploy. Non-zero exit = reality gap detected.
"""
import json, urllib.request, sys, sqlite3, os
from datetime import datetime, timezone, timedelta

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

    # ═══════════════════════════════════════════════
    # RETROSPECTIVE: What should exist?
    # ═══════════════════════════════════════════════
    print("\n── RETROSPECTIVE ──")

    # 1. Public site reachable
    for url_suffix, label in [
        ("/", "EN Homepage"),
        ("/ru/", "RU Homepage"),
        ("/stories.html", "Stories page"),
        ("/data/stories.json", "Stories JSON"),
    ]:
        url = PUBLIC_BASE + url_suffix
        headers = fetch_headers(url)
        status = "OK" if "last-modified" in headers or "etag" in headers else "FAIL"
        lm = headers.get("last-modified", headers.get("date", "?"))
        print(f"  {status:5} {label:20} {lm}")

    # 2. JSON freshness (< 60 min old)
    public_json = fetch_json(PUBLIC_BASE + "/data/stories.json")
    gen_at = public_json.get("generated_at", "")
    if gen_at:
        try:
            gen_dt = datetime.fromisoformat(gen_at.replace("Z", "+00:00"))
            age = datetime.now(timezone.utc) - gen_dt
            age_min = age.total_seconds() / 60
            status = "FRESH" if age_min < 15 else "STALE" if age_min < 60 else "FROZEN"
            print(f"\n  PUBLIC JSON age: {age_min:.1f} min — {status}")
            if age_min >= 60:
                failures.append(f"JSON frozen: {age_min:.0f} min old")
            print(f"  generated_at: {gen_at}")
            print(f"  stories: {len(public_json.get('stories',[])) + 1}")
            lead = public_json.get("lead", {})
            print(f"  lead: {lead.get('headline','?')[:80]}")
        except Exception as e:
            print(f"  ERROR parsing date: {e}")
            failures.append("Cannot parse generated_at")

    # ═══════════════════════════════════════════════
    # INTROSPECTIVE: Did we do what we claimed?
    # ═══════════════════════════════════════════════
    print("\n── INTROSPECTIVE ──")

    # 1. DB vs public story count
    db_path = os.path.join(PROJECT_DIR, "gazzetta.db")
    if os.path.exists(db_path):
        db = sqlite3.connect(db_path)
        db_count = db.execute("SELECT COUNT(*) FROM stories").fetchone()[0]
        public_count = len(public_json.get("stories", [])) + 1
        print(f"  DB stories: {db_count} | Public stories: {public_count}")
        if db_count != public_count:
            delta = db_count - public_count
            print(f"  WARNING: {delta} stories in DB not exported to public JSON")
            if delta > 5:
                failures.append(f"Export gap: {delta} stories missing from public JSON")

        # Check source diversity
        db.execute("SELECT COUNT(DISTINCT json_extract(full_json, '$.source')) FROM stories")
        source_count = db.fetchone()[0]
        print(f"  DB sources: {source_count}")
        db.close()

    # 2. No $88B spam
    stories = public_json.get("stories", [])
    all_stories = [public_json.get("lead", {})] + stories if public_json.get("lead") else stories
    from collections import Counter
    amounts = Counter()
    for s in all_stories:
        amt = s.get("capital_flow", {}).get("amount_b", 0)
        if amt > 0:
            amounts[round(amt, 1)] += 1
    dupes = {k: v for k, v in amounts.items() if v > 3}
    if dupes:
        print(f"  AMOUNT SPAM: {dupes}")
        failures.append(f"Amount spam detected: {dupes}")
    else:
        print(f"  Amount uniqueness: OK ({len(amounts)} unique values)")

    # 3. Check trade hooks are divergence format (not raw %)
    public_html = ""
    try:
        req = urllib.request.Request(PUBLIC_BASE + "/", headers={"Cache-Control": "no-cache"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            public_html = resp.read().decode()
    except:
        pass
    if "LAGGING" in public_html or "DIVERGENT" in public_html:
        print("  Trade hooks: DIVERGENCE format present ✓")
    else:
        print("  Trade hooks: divergence labels NOT found — may need deploy")
        failures.append("Trade hooks missing divergence labels")

    # ═══════════════════════════════════════════════
    # EXTRAPOLATIVE: Will it break tomorrow?
    # ═══════════════════════════════════════════════
    print("\n── EXTRAPOLATIVE ──")

    # 1. Cron health
    from subprocess import run
    result = run(["bash", "-c", "hermes cronjob list 2>/dev/null || echo 'cron check unavailable'"], 
                 capture_output=True, text=True, timeout=10)
    crons_active = result.stdout.count("scheduled") if "scheduled" in result.stdout else "? "
    print(f"  Active crons: {crons_active}")

    # 2. Pipeline files exist
    for script in ["fetch_intel.py", "intel_to_stories.py", "db_to_json.py", "approve_draft.py"]:
        path = os.path.join(PROJECT_DIR, "scripts", script)
        exists = os.path.exists(path)
        status = "✓" if exists else "✗ MISSING"
        if not exists:
            failures.append(f"Script missing: {script}")
        print(f"  {status} scripts/{script}")

    # 3. GCS bucket reachable
    gcs_headers = fetch_headers(PUBLIC_BASE + "/")
    cache = gcs_headers.get("cache-control", "MISSING")
    print(f"  Cache-Control: {cache}")

    # ═══════════════════════════════════════════════
    # VERDICT
    # ═══════════════════════════════════════════════
    print("\n" + "=" * 60)
    if failures:
        print(f"REALITY GAP DETECTED — {len(failures)} issues:")
        for f in failures:
            print(f"  ✗ {f}")
        print("=" * 60)
        sys.exit(1)
    else:
        print("REALITY VERIFIED — No gaps detected.")
        print("=" * 60)
        sys.exit(0)

if __name__ == "__main__":
    main()
