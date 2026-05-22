#!/usr/bin/env python3
"""
CEO Orchestrator for Gazzetta di Kyiv
- Reviews full stack/process landscape
- Classifies into program groups
- Runs health/status checks
- Recommends improvements
- Creates paradigm-compliance flags for new tasks
"""
import json, datetime, subprocess, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
if not (ROOT / 'site').exists():
    alt = pathlib.Path('/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv')
    if alt.exists():
        ROOT = alt
DATA = ROOT / "data"
OPS = ROOT / "ops"
OUT = DATA / "ceo_status.json"
CATALOG = DATA / "process_catalog.json"

PROCESS_GROUPS = {
    "ingestion": [
        "social_umbrella_collector.py",
        "gazzetta_source_strategy_update.py"
    ],
    "analysis": [
        "gazzetta_pipeline_audit.py",
        "gazzetta_representation_research.py",
        "build_site.py"
    ],
    "publishing": [
        "gazzetta_phase2_publish.py",
        "refresh-and-deploy.yml"
    ],
    "governance": [
        "OPERATING_MANDATE.md",
        "VARIANT_PROMPT.md"
    ],
    "design_management": [
        "design_compare.py",
        "design_dev_runner.py"
    ]
}

DESCRIPTIONS = {
    "ingestion": "Collects and normalizes multi-source narrative signals.",
    "analysis": "Computes narrative intelligence, QA, and rendering artifacts.",
    "publishing": "Build/deploy delivery pipeline for public site updates.",
    "governance": "Mandates, quality controls, and editorial constraints.",
    "design_management": "Continuously validates UI against target editorial design heuristics."
}

BEST_PRACTICE_SIGNALS = [
    "Clear ownership by process group",
    "Scheduled oversight with fixed cadences",
    "Objective health checks + machine-readable outputs",
    "Separation of concerns: ingestion / analysis / publishing / governance",
    "Closed-loop improvement recommendations"
]


def exists_any(name):
    candidates = [ROOT / "scripts" / name, ROOT / "ops" / name, ROOT / "docs" / name, ROOT / ".github/workflows" / name]
    return any(p.exists() for p in candidates)


def run(cmd):
    p = subprocess.run(cmd, shell=True, cwd=str(ROOT), capture_output=True, text=True)
    return {"ok": p.returncode == 0, "code": p.returncode, "out": p.stdout[-1200:], "err": p.stderr[-1200:]}


def main():
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    catalog = {
        "generated_at": now,
        "objective": "Enterprise-grade autonomous narrative newsroom operations",
        "groups": []
    }

    for g, items in PROCESS_GROUPS.items():
        present = [x for x in items if exists_any(x)]
        missing = [x for x in items if x not in present]
        catalog["groups"].append({
            "group": g,
            "description": DESCRIPTIONS[g],
            "programs": items,
            "present": present,
            "missing": missing,
            "coverage_pct": round((len(present) / len(items)) * 100, 1) if items else 100,
        })

    DATA.mkdir(parents=True, exist_ok=True)
    CATALOG.write_text(json.dumps(catalog, indent=2), encoding="utf-8")

    checks = {
        "design_compare": run("python3 ops/design_compare.py"),
        "pipeline_audit_file": {"ok": (DATA / "pipeline_audit.json").exists()},
        "narratives_file": {"ok": (DATA / "narratives.json").exists()},
        "site_index": {"ok": (ROOT / "site/index.html").exists()},
    }

    score = 0
    score += 30 if checks["design_compare"].get("ok") else 0
    score += 20 if checks["pipeline_audit_file"]["ok"] else 0
    score += 20 if checks["narratives_file"]["ok"] else 0
    score += 20 if checks["site_index"]["ok"] else 0
    score += 10 if all(g["coverage_pct"] >= 60 for g in catalog["groups"]) else 0

    recommendations = []
    if not checks["design_compare"].get("ok"):
        recommendations.append("Fix design drift first: run ops/design_dev_runner.py and patch homepage.")
    if not checks["pipeline_audit_file"]["ok"]:
        recommendations.append("Create/update daily pipeline audit artifact and schedule watchdog.")
    if score < 85:
        recommendations.append("Increase governance rigor: add explicit SLOs (freshness, uptime, content completeness).")
    recommendations.append("For new tasks outside known groups, create a new group-level overseer script before execution.")

    status = {
        "generated_at": now,
        "ceo_program": "active",
        "overall_health_score": score,
        "summary": {
            "groups": len(catalog["groups"]),
            "best_practice_signals": BEST_PRACTICE_SIGNALS,
        },
        "checks": checks,
        "recommendations": recommendations,
        "progress_view": {
            "states": ["running", "partially_covered", "needs_improvement"],
            "problem_policy": "identify -> classify -> assign overseer -> verify twice/day"
        }
    }

    OUT.write_text(json.dumps(status, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "status_file": str(OUT), "catalog_file": str(CATALOG), "score": score}, indent=2))


if __name__ == "__main__":
    main()
