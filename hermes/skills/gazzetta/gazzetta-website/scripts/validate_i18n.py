#!/usr/bin/env python3
"""i18n Key Validation — ensures 100% translation coverage before deploy.

Extracts all i18n keys from:
  1. HTML data-i18n attributes
  2. JS i18n.t('key', ...) calls  
  3. JS template literals ${i18n.t('key',...)}

Compares against translation JSON files. Fails if any key is missing.
Returns exit code 1 if coverage < 100%.

Usage: GAZZETTA_ROOT=/path python3 scripts/validate_i18n.py
"""
import json, re, sys, os
from pathlib import Path
from glob import glob

PROJECT_ROOT = Path(os.environ.get("GAZZETTA_ROOT", os.path.expanduser("~/projects/gazzetta-di-kyiv")))
SITE_DIR = PROJECT_ROOT / "site"

def extract_html_keys(html_path):
    """Extract all data-i18n keys from HTML files."""
    keys = set()
    for pattern in [str(html_path / "**/*.html"), str(html_path / "*.html")]:
        for f in glob(pattern, recursive=True):
            text = Path(f).read_text(errors='ignore')
            for m in re.finditer(r'data-i18n="([^"]+)"', text):
                keys.add(m.group(1))
            for m in re.finditer(r"data-i18n='([^']+)'", text):
                keys.add(m.group(1))
    return keys

def extract_js_keys(js_path):
    """Extract all i18n.t('key', ...) calls from JS files."""
    keys = set()
    for pattern in [str(js_path / "**/*.js"), str(js_path / "*.js")]:
        for f in glob(pattern, recursive=True):
            text = Path(f).read_text(errors='ignore')
            for m in re.finditer(r"i18n\.t\(\s*['\"]([^'\"]+)['\"]", text):
                keys.add(m.group(1))
            for m in re.finditer(r"\$\{i18n\.t\(\s*['\"]([^'\"]+)['\"]", text):
                keys.add(m.group(1))
    return keys

def load_translation_keys(json_path):
    """Load all keys from a translation JSON file."""
    if not json_path.exists():
        return set(), {}
    data = json.loads(json_path.read_text())
    return set(data.keys()), data

def main():
    errors = 0
    
    html_keys = extract_html_keys(SITE_DIR)
    js_keys = extract_js_keys(SITE_DIR)
    canonical = html_keys | js_keys
    
    print(f"Canonical keys: {len(canonical)} (HTML: {len(html_keys)}, JS: {len(js_keys)})")
    
    locale_files = sorted(glob(str(SITE_DIR / "i18n_*.json")))
    if not locale_files:
        print("No i18n_*.json files found — skipping")
        return 0
    
    for lf in locale_files:
        locale_name = Path(lf).stem.replace("i18n_", "")
        locale_keys, _ = load_translation_keys(Path(lf))
        missing = canonical - locale_keys
        extra = locale_keys - canonical
        
        coverage = len(canonical - missing)
        print(f"\n{locale_name.upper()}: {coverage}/{len(canonical)} keys covered")
        
        if missing:
            print(f"  MISSING ({len(missing)}):")
            for k in sorted(missing):
                print(f"    - {k}")
            errors += len(missing)
        
        if extra:
            print(f"  Extra (dead weight): {len(extra)}")
    
    if errors:
        print(f"\nFAIL: {errors} missing keys. Deploy blocked.")
        return 1
    print(f"\nPASS: 100% coverage.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
