#!/usr/bin/env python3
"""Gazzetta di Kyiv — Self-Upgrade Engine (v1.0)
Daily code review via Gemini. Identifies poor-quality patterns,
proposes refactors, and generates a structured upgrade report.

Usage:
    .venv/bin/python scripts/self_upgrade.py              # Default: review all JS/HTML/CSS
    .venv/bin/python scripts/self_upgrade.py --file app.js  # Review single file
    .venv/bin/python scripts/self_upgrade.py --dry-run       # No API call, pattern check only

Output: data/self_upgrade_report.json
"""

import os, sys, json, re, subprocess, argparse
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Patterns that indicate poor quality
POOR_PATTERNS = {
    "empty_catch": (r"catch\s*\(\s*\w*\s*\)\s*\{\s*\}", "Empty catch block — swallows errors silently"),
    "console_log_shipping": (r"console\.(log|warn|error)\(", "Console logging in production code — should use structured logging or remove"),
    "hardcoded_credentials": (r"(api_key|token|password|secret)\s*=\s*[\"'][^\"']{10,}[\"']", "Potential hardcoded credential — use env vars"),
    "magic_number": (r"(?<![\w.])[0-9]{3,}(?![\w])", "Magic number — use named constant"),
    "inline_style": (r'style\s*=\s*["\']', "Inline style — use CSS class instead"),
    "eval_usage": (r"\beval\s*\(|\bnew\s+Function\s*\(", "eval/Function constructor — security risk"),
    "callback_hell": (r"}\s*\);\s*}\s*\);\s*}\s*\)", "Deep nesting — potential callback hell"),
    "unused_i18n": (r"data-i18n\s*=", "Check if i18n key exists in locale files"),
}

def check_patterns(filepath):
    """Scan a file for poor-quality patterns."""
    results = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return [{"file": str(filepath), "error": str(e)}]

    for pattern_name, (regex, description) in POOR_PATTERNS.items():
        matches = re.findall(regex, content, re.IGNORECASE | re.MULTILINE)
        if matches:
            results.append({
                "file": str(filepath.relative_to(PROJECT_ROOT)),
                "pattern": pattern_name,
                "severity": "HIGH" if pattern_name in ("empty_catch", "eval_usage", "hardcoded_credentials") else "MEDIUM",
                "count": len(matches),
                "description": description,
            })
    return results


def check_file_size(filepath):
    """Flag files over 2000 lines."""
    try:
        with open(filepath, "r") as f:
            lines = len(f.readlines())
    except:
        return None
    if lines > 2000:
        return {
            "file": str(filepath.relative_to(PROJECT_ROOT)),
            "pattern": "file_too_large",
            "severity": "MEDIUM",
            "description": f"File is {lines} lines — consider splitting into modules",
            "count": lines,
        }
    return None


def check_i18n_coverage():
    """Verify all i18n keys in HTML match locale files."""
    results = []
    locale_path = PROJECT_ROOT / "site" / "i18n_ru.json"
    if not locale_path.exists():
        return [{"file": "i18n_ru.json", "pattern": "missing_locale", "severity": "HIGH", "description": "Russian locale file missing"}]

    with open(locale_path, "r") as f:
        ru_keys = set(json.load(f).keys())

    # Extract all data-i18n keys from HTML files
    html_keys = set()
    for html_file in (PROJECT_ROOT / "site").glob("**/*.html"):
        with open(html_file, "r") as f:
            content = f.read()
        found = re.findall(r'data-i18n\s*=\s*["\']([^"\']+)["\']', content)
        html_keys.update(found)

    # Extract i18n.t() keys from JS
    js_keys = set()
    for js_file in (PROJECT_ROOT / "site").glob("*.js"):
        with open(js_file, "r") as f:
            content = f.read()
        found = re.findall(r'i18n\.t\s*\(\s*["\']([^"\']+)["\']', content)
        js_keys.update(found)

    all_keys = html_keys | js_keys

    missing_in_ru = all_keys - ru_keys
    unused_in_ru = ru_keys - all_keys

    if missing_in_ru:
        results.append({
            "file": "i18n_ru.json",
            "pattern": "missing_i18n_keys",
            "severity": "HIGH",
            "description": f"Missing {len(missing_in_ru)} keys in RU locale",
            "keys": sorted(missing_in_ru)[:20],
        })

    if unused_in_ru:
        results.append({
            "file": "i18n_ru.json",
            "pattern": "unused_i18n_keys",
            "severity": "LOW",
            "description": f"{len(unused_in_ru)} unused keys in RU locale (bloat)",
            "count": len(unused_in_ru),
        })

    return results


def generate_report(all_results):
    """Compile final report."""
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_issues": len(all_results),
            "by_severity": dict(Counter(r.get("severity", "UNKNOWN") for r in all_results)),
            "by_pattern": dict(Counter(r["pattern"] for r in all_results if "pattern" in r)),
        },
        "issues": all_results,
        "recommendations": [],
    }

    # Generate specific recommendations
    if any(r["pattern"] == "empty_catch" for r in all_results):
        report["recommendations"].append(
            "Replace empty catch blocks with structured error logging: `catch(e) { logError('module', e); }`"
        )
    if any(r["pattern"] == "file_too_large" for r in all_results):
        report["recommendations"].append(
            "Split large files (>2000 lines) into modules: UI, Data, State already exist — extend the pattern"
        )
    if any(r["pattern"] == "missing_i18n_keys" for r in all_results):
        report["recommendations"].append(
            "Run `scripts/validate_i18n.py` to add missing RU keys — deploy blocks on missing keys"
        )
    if any(r["pattern"] == "hardcoded_credentials" for r in all_results):
        report["recommendations"].append(
            "⚠ CRITICAL: Remove hardcoded credentials immediately and use environment variables"
        )

    return report


def main():
    parser = argparse.ArgumentParser(description="Gazzetta Self-Upgrade Engine")
    parser.add_argument("--file", help="Review a single file")
    parser.add_argument("--dry-run", action="store_true", help="Pattern check only, no API call")
    args = parser.parse_args()

    all_results = []

    if args.file:
        filepath = PROJECT_ROOT / args.file
        all_results.extend(check_patterns(filepath))
        size_issue = check_file_size(filepath)
        if size_issue:
            all_results.append(size_issue)
    else:
        # Scan all JS, HTML, CSS, and Python files (excluding venv and site hashed copies)
        scan_globs = ["*.js", "*.html", "*.css", "scripts/*.py"]
        for glob_pattern in scan_globs:
            for filepath in PROJECT_ROOT.glob(glob_pattern):
                if ".venv" in str(filepath) or "hashed" in str(filepath):
                    continue
                if filepath.name.endswith((".min.js", ".hashed.js")):
                    continue
                all_results.extend(check_patterns(filepath))
                size_issue = check_file_size(filepath)
                if size_issue:
                    all_results.append(size_issue)

        # i18n coverage check
        all_results.extend(check_i18n_coverage())

    report = generate_report(all_results)

    # Write report
    out_path = DATA_DIR / "self_upgrade_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"Self-Upgrade Report: {out_path}")
    print(f"  Issues found: {report['summary']['total_issues']}")
    for sev, count in report["summary"]["by_severity"].items():
        print(f"    {sev}: {count}")
    for rec in report["recommendations"]:
        print(f"  → {rec}")

    # Exit with error if HIGH severity issues exist
    high_count = report["summary"]["by_severity"].get("HIGH", 0)
    if high_count > 0:
        print(f"\n⚠ {high_count} HIGH-severity issues found!")
        if not args.dry_run:
            sys.exit(1)

    print("\n✓ Self-upgrade complete")


if __name__ == "__main__":
    main()
