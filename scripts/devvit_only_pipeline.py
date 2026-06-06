#!/usr/bin/env python3
"""devvit_only_pipeline.py — End-to-end Devvit data pipeline orchestration.

Runs: devvit_ingest.py → generate_candidates_fallback.py → phase2_scoring.py → build_site.py
Used by: gazzetta-devvit-only-pipeline cron (every 480m)
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(PROJECT, "scripts")


def run_step(name, script):
    """Run a pipeline step, return (ok, output)."""
    script_path = os.path.join(SCRIPTS, script)
    if not os.path.exists(script_path):
        return False, f"SCRIPT_MISSING: {script_path}"

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=PROJECT,
        )
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)


def main():
    results = {}
    now = datetime.now(timezone.utc).isoformat()

    # Step 1: Ingest
    ok, out = run_step("devvit_ingest", "devvit_ingest.py")
    results["ingest"] = {"ok": ok, "output": out[:500]}

    # Step 2: Generate candidates (always runs, may use fallback)
    ok, out = run_step("generate_candidates", "generate_candidates_fallback.py")
    results["candidates"] = {"ok": ok, "output": out[:500]}

    # Step 3: Score
    ok, out = run_step("phase2_scoring", "phase2_scoring.py")
    results["scoring"] = {"ok": ok, "output": out[:500]}

    # Step 4: Build site
    ok, out = run_step("build_site", "build_site.py")
    results["build"] = {"ok": ok, "output": out[:500]}

    # Summary
    all_ok = all(r["ok"] for r in results.values())
    summary = {
        "ok": all_ok,
        "pipeline": "devvit_only",
        "run_at": now,
        "steps": {k: v["ok"] for k, v in results.items()},
        "details": results,
    }

    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    main()
