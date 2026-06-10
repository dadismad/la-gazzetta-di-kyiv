#!/usr/bin/env python3
"""self_upgrade.py — Omnipotent Self-Growth: analyze deployment headers with GCP

Uses gcloud to inspect bucket metadata, compare local ↔ live state,
and generate an upgrade report with recommendations.
"""
import subprocess, json, sys, os
from datetime import datetime, timezone

BUCKET = "gs://www.lagazzettadikyiv.com"
SITE = "site/"
REQUIRED_HEADERS = {
    "Cache-Control": "public,max-age=0,must-revalidate",
    "Content-Type": "text/html",
}
EXPECTED_FILES = [
    "index.html", "stories.html", "flows.html", "signal.html",
    "trades.html", "track.html", "event_horizon.html", "flow-nodes.html",
    "about.html", "capital.html", "data.html", "privacy.html", "terms.html",
    "ru/index.html",
]


def run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return r.stdout.strip(), r.stderr.strip(), r.returncode
    except Exception as e:
        return "", str(e), 1


def check_gsutil():
    _, _, code = run("which gcloud")
    return code == 0


def analyze_headers():
    print("§1  GCS HEADER AUDIT")
    issues = []
    for fname in EXPECTED_FILES:
        url = f"{BUCKET}/{fname}"
        stdout, stderr, code = run(f"gsutil stat {url} 2>&1")
        if code != 0:
            issues.append(f"  ✗ {fname}: cannot stat ({stderr[:80]})")
            continue
        # Parse stat output
        for line in stdout.split("\n"):
            line = line.strip()
            if "Cache-Control:" in line:
                cc = line.split(":", 1)[1].strip()
                if cc != REQUIRED_HEADERS["Cache-Control"]:
                    issues.append(f"  ⚠ {fname}: Cache-Control={cc}")
            if "Content-Type:" in line:
                ct = line.split(":", 1)[1].strip()
                if "html" not in ct:
                    issues.append(f"  ⚠ {fname}: Content-Type={ct}")

    if not issues:
        print("  All headers correct ✓")
    else:
        for i in issues:
            print(i)
    return len(issues) == 0


def compare_timestamps():
    print("\n§2  LOCAL ↔ LIVE DRIFT")
    local_files = {}
    for fname in EXPECTED_FILES:
        path = os.path.join(SITE, fname)
        if os.path.exists(path):
            local_files[fname] = os.path.getmtime(path)

    drifts = []
    for fname, local_mtime in local_files.items():
        url = f"{BUCKET}/{fname}"
        stdout, _, code = run(f"gsutil stat {url} 2>&1")
        if code != 0:
            drifts.append(f"  ✗ {fname}: live not found")
            continue
        for line in stdout.split("\n"):
            if "Creation time:" in line:
                ct_str = line.split(":", 1)[1].strip()
                try:
                    live_ts = datetime.strptime(ct_str[:19], "%a, %d %b %Y %H:%M:%S")
                    local_ts = datetime.fromtimestamp(local_mtime, tz=timezone.utc)
                    drift_min = abs((local_ts - live_ts.replace(tzinfo=timezone.utc)).total_seconds()) / 60
                    if drift_min > 10:
                        drifts.append(f"  ⚠ {fname}: {drift_min:.0f}min drift")
                except:
                    pass

    if not drifts:
        print("  No drift detected ✓")
    else:
        for d in drifts:
            print(d)
    return len(drifts) == 0


def generate_report():
    print("\n§3  SELF-UPGRADE REPORT")
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "gcloud_available": check_gsutil(),
        "recommendations": [],
    }

    if not report["gcloud_available"]:
        print("  ⚠ gcloud not found. Run: gcloud auth login")
        report["recommendations"].append("Authenticate gcloud: `gcloud auth login`")
        print("  Then: gcloud auth application-default login")
        report["recommendations"].append("ADC login: `gcloud auth application-default login`")
    else:
        print("  gcloud available ✓")
        # Check if we can actually list the bucket
        stdout, stderr, code = run(f"gsutil ls {BUCKET} 2>&1")
        if code != 0:
            print(f"  ⚠ Cannot access bucket: {stderr[:100]}")
            print("  Run: gcloud auth login --update-adc")
            report["recommendations"].append("Re-auth: `gcloud auth login --update-adc`")
        else:
            print(f"  Bucket accessible: {len(stdout.split(chr(10)))} objects")

    report["recommendations"].append("Run shipit.sh to deploy latest changes")
    report["recommendations"].append("Verify with refresh_context.py after deploy")

    # Write report
    report_path = "site/data/upgrade_report.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"  Report → {report_path}")

    return report


def main():
    print("═══ GAZZETTA SELF-UPGRADE ═══")
    print(f"  {datetime.now(timezone.utc).isoformat()}\n")

    header_ok = analyze_headers()
    drift_ok = compare_timestamps()
    report = generate_report()

    print("\n═══ SUMMARY ═══")
    print(f"  Headers: {'✓' if header_ok else '⚠'}")
    print(f"  Drift:   {'✓' if drift_ok else '⚠'}")
    print(f"  Recs:    {len(report['recommendations'])}")

    if not check_gsutil():
        print("\n⚠ MANUAL STEP REQUIRED:")
        print("  gcloud auth login --update-adc")
        print("  Then re-run: python scripts/self_upgrade.py")


if __name__ == "__main__":
    main()
