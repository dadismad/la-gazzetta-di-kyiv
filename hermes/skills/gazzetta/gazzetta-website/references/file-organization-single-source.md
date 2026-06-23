# File Organization — Single Source of Truth (v26.7)

## The Problem

The Gazzetta project had 25 HTML files at root level AND copies in `site/`. Root CSS/JS also duplicated. Every session, the agent edited the wrong file — either root (never deployed) or site/ (actually deployed). The user screamed "the site doesn't change even after you say you changed it" because root edits went nowhere.

## The Rule

**ALL deployable HTML/CSS/JS lives ONLY in `site/`.** There are NO HTML/CSS/JS files in the project root. If you see them, delete them — they're obsolete duplicates that will confuse you.

## Directory Map

```
~/projects/gazzetta-di-kyiv/
├── site/              ← ONLY place to edit (deployed to GCS)
│   ├── index.html     ← main page
│   ├── styles.css     ← ALL CSS (hashed for deployment)
│   ├── app.js         ← main JS
│   ├── i18n.js        ← translations
│   ├── sector.js      ← sector taxonomy
│   ├── story-app.js   ← story detail page JS
│   ├── data/          ← JSON data (deployed)
│   └── ...20 HTML pages total
├── scripts/           ← ALL Python/shell scripts
├── data/              ← Source data (NOT deployed directly)
├── archive/           ← Saved old unique HTML (not deployed)
├── docs/audits/       ← Old audit reports
├── config.yaml
└── shipit.sh
```

## Deploy Path

Edit `site/` → `gsutil cp` → `gs://www.lagazzettadikyiv.com/`

No intermediate build step. No root duplication. No ambiguity.

## Verification

```bash
# Root should have ZERO HTML files
ls ~/projects/gazzetta-di-kyiv/*.html 2>/dev/null
# Should return: "No such file or directory"

# All HTML lives in site/
ls ~/projects/gazzetta-di-kyiv/site/*.html | wc -l
# Should return: 20+
```
