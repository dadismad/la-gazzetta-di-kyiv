# Mobile Shadow UI & Trust Framework — v23.19 Design Patterns

## Mobile Shadow UI

Progressive disclosure pattern for mobile devices (≤768px). Replaces text-heavy desktop layout with large high-contrast metrics and tap-to-expand hooks.

### Large Metric Cards
```css
.mobile-metric {
  display: flex; flex-direction: column; align-items: center;
  padding: 12px 8px; min-width: 80px;
  border: 1px solid var(--divider);
}
.mobile-metric .metric-value {
  font-family: var(--mono); font-size: 22px; font-weight: 900;
}
.mobile-metric .metric-hint {
  font-family: var(--sans); font-size: 9px;
  opacity: 0.4; /* ghost text */
  text-transform: uppercase; letter-spacing: 0.08em;
}
```

### Expandable Alpha Hooks
```css
.metric-expandable { cursor: pointer; }
.metric-expandable .alpha-hook {
  font-family: var(--body); font-size: 13px; font-style: italic;
  color: var(--gold); max-height: 0; overflow: hidden;
  transition: max-height 0.3s ease;
}
.metric-expandable.expanded .alpha-hook { max-height: 80px; }
```

### Horizontal Slider with Scroll-Snap
```css
.product-nav {
  display: flex; flex-wrap: nowrap; overflow-x: auto;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
  gap: 0; padding: 4px 0;
}
.product-nav .nav-link {
  scroll-snap-align: start; flex-shrink: 0;
  padding: 6px 12px; white-space: nowrap;
}
```

## Asymmetry Gauge Dial

SVG semi-circular gauge in left sidebar. Gold arc fills proportionally to current max asymmetry score (0-100). Red needle at current value.

```html
<div class="asymmetry-gauge" id="asymmetryGauge">
  <svg viewBox="0 0 120 70" class="gauge-svg">
    <path d="M 10 65 A 50 50 0 0 1 110 65" fill="none" stroke="#E5E7EB" stroke-width="8" stroke-linecap="round"/>
    <path id="gaugeArc" d="M 10 65 A 50 50 0 0 1 110 65" fill="none" stroke="#B8860B" stroke-width="8" stroke-linecap="round" stroke-dasharray="0 157" stroke-dashoffset="0"/>
    <circle id="gaugeNeedle" cx="60" cy="65" r="3" fill="#DC2626"/>
    <text x="60" y="32" text-anchor="middle" font-family="var(--mono)" font-size="18" font-weight="900">58</text>
    <text x="60" y="46" text-anchor="middle" font-family="var(--sans)" font-size="8" fill="var(--ink-muted)">MODERATE</text>
  </svg>
</div>
```

CSS: `.gauge-svg { width: 100%; max-width: 140px; height: auto; }`

## Trust Framework Widget

Right sidebar widget displaying E-E-A-T platform credibility:

```html
<div class="side-section">
  <div class="side-section-label">TRUST FRAMEWORK</div>
  <div class="side-freshness">
    <div class="fresh-item"><span class="fresh-dot" style="background:#059669"></span><span>183 assertions</span><span class="fresh-age" style="color:#059669">✓ PASSING</span></div>
    <div class="fresh-item"><span class="fresh-dot" style="background:var(--gold)"></span><span>Cloud Brain</span><span class="fresh-age" style="color:#059669">RUNNING</span></div>
    <div class="fresh-item"><span class="fresh-dot" style="background:var(--gold)"></span><span>Expertise</span><span class="fresh-age">Mathematical</span></div>
    <div class="fresh-item"><span class="fresh-dot" style="background:var(--gold)"></span><span>Authority</span><span class="fresh-age">Source-cited</span></div>
    <div class="fresh-item"><span class="fresh-dot" style="background:#059669"></span><span>Trust</span><span class="fresh-age" style="color:#059669">Verified</span></div>
  </div>
  <a href="./methodology.html">View full methodology →</a>
  <a href="./sources.html">View sources →</a>
</div>
```

## Top Navigation Menu

Clean professional menu with 3 labeled groups:

```html
<nav class="product-nav">
  <span class="nav-group-label">INTEL</span>
  <a href="./stories.html">Stories</a> <a href="./flows.html">Flows</a>
  <a href="./event_horizon.html">Horizon</a> <a href="./flow-nodes.html">Nodes</a>
  <span class="nav-group-label">ALPHA</span>
  <a href="./signal.html">Signal</a> <a href="./trades.html">Trades</a> <a href="./track.html">Track</a>
  <span class="nav-group-label">ABOUT</span>
  <a href="./methodology.html">METHODOLOGY</a> <a href="./sources.html">SOURCES</a> <a href="./about.html">About</a>
</nav>
```

## Story Interlinking

Cross-container navigation on story teasers — links to Horizon and Flow Nodes views:

```css
.story-interlink {
  display: inline-block; font-family: var(--mono); font-size: 9px;
  font-weight: 600; padding: 2px 8px; margin-left: 6px;
  border: 1px solid var(--divider); color: var(--ink-muted);
  text-decoration: none; transition: all 0.2s;
}
.story-interlink:hover { border-color: var(--gold); color: var(--gold); }
```
