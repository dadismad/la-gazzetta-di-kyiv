#!/usr/bin/env python3
"""
Gazzetta di Kyiv — Content-Hashed Asset Builder
Replaces query-string cache busting (?v=22.22) with immutable content hashing.

BEFORE: <link rel="stylesheet" href="./styles.css?v=22.22"/>
AFTER:  <link rel="stylesheet" href="./styles.3412707c.css"/>

When the CSS changes → new SHA256 → new filename → CDN treats as new file.
No manual version bumps across 20+ HTML files. No stale cache edge cases.
"""
import hashlib, os, sys, re, json, shutil
from pathlib import Path

SITE_DIR = Path(os.path.expanduser("~/projects/gazzetta-di-kyiv/site"))
ASSETS = ["styles.css", "styles-modern.css", "app.js", "i18n.js", "sector.js", "story-app.js"]
DRY_RUN = "--dry-run" in sys.argv

def hash_file(path: Path) -> str:
    """SHA256 of file contents, first 8 hex chars."""
    return hashlib.sha256(path.read_bytes()).hexdigest()[:8]

def build():
    manifest = {}
    
    # Step 1: Compute hashes and create hashed copies
    for asset in ASSETS:
        src = SITE_DIR / asset
        if not src.exists():
            print(f"  SKIP {asset} — not found")
            continue
        
        h = hash_file(src)
        name, ext = os.path.splitext(asset)
        hashed_name = f"{name}.{h}{ext}"
        dst = SITE_DIR / hashed_name
        
        manifest[asset] = {"hash": h, "hashed_name": hashed_name}
        
        if not DRY_RUN:
            shutil.copy2(src, dst)
        print(f"  {asset:25s} → {hashed_name}")
    
    # Step 2: Rewrite HTML references
    html_files = sorted(SITE_DIR.glob("*.html"))
    
    for html_path in html_files:
        content = html_path.read_text()
        original = content
        modified = False
        
        for asset, info in manifest.items():
            name, ext = os.path.splitext(asset)
            # Match: href="./asset.css" or href="./asset.css?v=..." or href="./asset.HHHHHHHH.css" (already hashed)
            for attr in ['href', 'src']:
                # Match unhashed: ./asset.css or ./asset.css?v=...
                pattern_unhashed = re.compile(
                    rf'({attr}=["\']\.\/{re.escape(asset)})(\?v=[\d.]+)?(["\'])',
                    re.IGNORECASE
                )
                new_attr = f'{attr}="./{info["hashed_name"]}"'
                content = pattern_unhashed.sub(new_attr, content)
                
                # Match already-hashed: ./name.HHHHHHHH.ext (any 8-char hex hash)
                pattern_hashed = re.compile(
                    rf'{attr}=["\']\.\/{re.escape(name)}\.[0-9a-f]{{8}}\.{ext.lstrip(".")}["\']',
                    re.IGNORECASE
                )
                content = pattern_hashed.sub(new_attr, content)
        
        if not DRY_RUN:
            html_path.write_text(content)
        if content != original:
            print(f"  {html_path.name:30s} → rewritten")
    
    # Step 3: Write manifest
    manifest_path = SITE_DIR / "build-manifest.json"
    if not DRY_RUN:
        manifest_path.write_text(json.dumps(manifest, indent=2))
    
    print(f"\n  Manifest: {manifest_path}")
    print(f"  Assets:   {len(manifest)} hashed")
    print(f"  HTML:     {len(html_files)} pages scanned")
    
    return manifest

if __name__ == "__main__":
    build()
