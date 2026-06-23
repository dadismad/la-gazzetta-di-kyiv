# Masthead Verification v27.2

After every deploy, verify the live masthead has the correct symbols.

## Class Name Check

```js
JSON.stringify({
    left: document.querySelector('.masthead-machiavelli')?.getAttribute('title'),
    right: document.querySelector('.masthead-bulavas')?.getAttribute('title'),
    noOldClasses: !document.querySelector('.masthead-caduceus') && !document.querySelector('.masthead-bulava'),
})
// PASS: left = "Fox & Lion -- prudence and strength"
// PASS: right = "Crossed bulavas -- Hetman's maces, dual authority"
// PASS: noOldClasses = true
```

## Color Verification (gold standard)

```js
JSON.stringify({
    machiavelli: getComputedStyle(document.querySelector('.masthead-machiavelli')).color,
    bulavas: getComputedStyle(document.querySelector('.masthead-bulavas')).color,
    name: getComputedStyle(document.querySelector('.masthead-name')).color,
    nameFont: getComputedStyle(document.querySelector('.masthead-name')).fontFamily,
})
// PASS: machiavelli = "rgb(212, 175, 55)" (gold #D4AF37)
// PASS: bulavas = "rgb(212, 175, 55)" (gold #D4AF37)
// PASS: name = "rgb(139, 0, 0)" (dark red #8B0000)
// PASS: nameFont contains "Playfair Display"
```

## Hashed CSS Self-Nuke Detection

If symbols appear black (#111827) instead of gold:
1. Check CSS href: `document.querySelector('link[rel="stylesheet"]:not([href*="google"])')?.href`
2. If it references a hashed file (e.g. `styles.ab6de8dd.css`), the file was deleted by `rsync -d`
3. Fix: `sed -i '' 's/styles\.[a-f0-9]*\.css/styles.css/g' public/*.html`
4. Re-run build_site.py and deploy with `Cache-Control: no-cache`

## Reversion Check

The ghost project reversion check in verify-deploy.md must also include:
```bash
curl -sk https://www.lagazzettadikyiv.com/ | grep -o 'masthead-[a-z]*' | sort -u
# MUST show: masthead-machiavelli, masthead-bulavas
# MUST NOT show: masthead-caduceus
```
