# Root-vs-Site File Overwrite Pitfall — CRITICAL

**Session: 2026-06-10. Cost: Two-World Architecture deploy failure. Public site served old HTML while agent claimed success.**

## The Bug

The root files at `~/projects/gazzetta-di-kyiv/` are canonical. The `site/` directory is the deployment target. When you:

1. Patch `site/index.html` with changes
2. Run `cp index.html site/index.html` to "sync"

The ROOT `index.html` (which is the OLD version) overwrites your patched `site/index.html`. All changes are silently lost. The deploy goes through with the old HTML.

## Why This Is So Destructive

- `shipit.sh` runs to completion (exit code 0)
- GCS rsync reports success
- Tests pass
- Agent reports "all changes deployed"

But the public URL shows the OLD HTML. The user sees no changes. Agent has no idea because it never verified the public URL.

## Detection

After deploy, compare ROOT to CDN:
```bash
diff <(curl -s https://www.lagazzettadikyiv.com/ | grep -c 'EXPECTED_STRING') \
     <(grep -c 'EXPECTED_STRING' index.html)
```

Must match. If not → patches went to `site/` and got overwritten.

## Correct Workflow

1. Patch ROOT files: `index.html`, `app.js`, `styles.css`
2. THEN copy to site/: `cp index.html site/index.html && cp app.js site/app.js && cp styles.css site/styles.css`
3. Deploy: `bash shipit.sh`
4. Run Anti-Lying Protocol (see `gazzetta-interpret-review-execute` skill)
