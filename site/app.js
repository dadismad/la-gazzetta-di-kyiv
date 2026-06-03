// Gazzetta di Kyiv — Narrative Intelligence Terminal
// Loads live data from pipeline API endpoints

const API = {
  regime: './api/v1/home/regime.json',
  setups: './api/v1/home/setups.json',
  contradictions: './api/v1/home/contradictions.json',
  stories: './data/website_stories_latest.json',
};

function byId(id) { return document.getElementById(id); }

async function getJSON(path, fallback) {
  try {
    const r = await fetch(path, { cache: 'no-store' });
    if (!r.ok) throw new Error(String(r.status));
    return await r.json();
  } catch (e) {
    console.warn(`Failed to load ${path}:`, e.message);
    return fallback;
  }
}

function short(s, n) {
  const v = String(s || '').trim();
  return v.length > n ? v.slice(0, n - 1) + '…' : v;
}

function urgencyClass(urgency) {
  if (!urgency) return '';
  const u = urgency.toLowerCase();
  if (u === 'high') return 'urgency-high';
  if (u === 'medium') return 'urgency-medium';
  return 'urgency-low';
}

function confClass(conf) {
  if (conf >= 0.75) return 'confidence-high';
  if (conf >= 0.55) return 'confidence-medium';
  return 'confidence-low';
}

function confLabel(conf) {
  if (conf >= 0.75) return 'High';
  if (conf >= 0.55) return 'Medium';
  return 'Low';
}

function timeAgo(iso) {
  if (!iso) return '';
  try {
    const then = new Date(iso);
    const now = new Date();
    const min = Math.floor((now - then) / 60000);
    if (min < 1) return 'now';
    if (min < 60) return `${min}m ago`;
    const hrs = Math.floor(min / 60);
    if (hrs < 24) return `${hrs}h ago`;
    return `${Math.floor(hrs / 24)}d ago`;
  } catch { return ''; }
}

// ── Render story cards from setups ──
function storyCardMarkup(setup, idx, total) {
  const title = setup.title || setup.event || 'Story in Play';
  const thesis = setup.thesis || setup.summary || '';
  const contradiction = setup.claim_b || 'Cross-source confirmation pending.';
  const actors = setup.actors || [];
  const probBase = setup.probability_base ?? setup.scenarios?.[0]?.probability;
  const probBull = setup.probability_bull ?? setup.scenarios?.[1]?.probability;
  const probBear = setup.probability_bear ?? setup.scenarios?.[2]?.probability;
  const confidence = setup.confidence ?? 0.55;
  const execution = setup.retail_execution || [];
  const invalidation = setup.invalidation_triggers || [];
  const urgency = setup.urgency || (idx === 0 ? 'high' : idx < 3 ? 'medium' : 'low');
  const isLead = idx === 0;

  return `
    <article class="story-card ${isLead ? 'story-lead' : ''}"
             data-expandable="true" tabindex="0" role="button"
             aria-expanded="false">
      <span class="story-priority ${urgencyClass(urgency)}">${urgency.toUpperCase()} SIGNAL</span>
      <h3>${short(title, 96)}</h3>
      <p class="story-thesis">${short(thesis, isLead ? 220 : 150)}</p>
      ${contradiction ? `<p class="story-contradiction"><strong>Contradiction:</strong> ${short(contradiction, 150)}</p>` : ''}
      <span class="story-expand-hint">↘ expand</span>
      <div class="story-details">
        ${actors.length ? `<p><strong>Key actors:</strong> ${actors.slice(0, 5).join(', ')}</p>` : ''}
        ${execution.length ? `<p><strong>Execution:</strong> ${execution.slice(0, 2).join('; ')}</p>` : ''}
        ${invalidation.length ? `<p><strong>Invalidation:</strong> ${invalidation[0]}</p>` : ''}
        <div class="story-meta">
          ${probBase != null ? `<span>Base ${probBase}%</span>` : ''}
          ${probBull != null ? `<span>Bull ${probBull}%</span>` : ''}
          ${probBear != null ? `<span>Bear ${probBear}%</span>` : ''}
          <span class="${confClass(confidence)}">Confidence: ${confLabel(confidence)}</span>
        </div>
      </div>
    </article>`;
}

// ── Regime bar ──
function renderRegimeBar(regime) {
  const bar = byId('regimeBar');
  if (!bar) return;
  const label = regime?.regime_label || 'Narrative Transition';
  const risk = regime?.risk_state || 'neutral';
  const conf = regime?.confidence ? `${Math.round(regime.confidence * 100)}%` : '—';
  bar.innerHTML = `
    <span class="regime-label">${label}</span>
    <span class="regime-meta">Risk: ${risk}</span>
    <span class="regime-meta">Confidence: ${conf}</span>
    <span class="regime-meta">Sources: ${regime?.source_count || '—'}</span>
  `;
}

// ── Focus Panel ──
function renderFocusPanel(regime, setups, contradictions) {
  // Narrative Regime
  const regimeEl = byId('focusRegime');
  if (regimeEl && regime) {
    const label = regime.regime_label || 'Narrative Transition';
    const risk = regime.risk_state || 'neutral';
    regimeEl.innerHTML = `
      <p>Current: <strong style="color:#fff">${label}</strong></p>
      <p>Risk state: <strong>${risk}</strong></p>
      <p>Sources tracked: ${regime.source_count || '—'}</p>
    `;
  }

  // Signal Strength
  const signalEl = byId('focusSignal');
  if (signalEl && setups) {
    const count = setups.length || setups.items?.length || 0;
    const avgConf = setups.length
      ? Math.round(setups.reduce((s, x) => s + (x.confidence || 0.5), 0) / setups.length * 100)
      : 0;
    signalEl.innerHTML = `
      <div class="signal-value">${count}</div>
      <div class="signal-label">Active narratives</div>
      <p style="margin-top:4px">Avg confidence: ${avgConf}%</p>
    `;
  }

  // Top Contradictions
  const cEl = byId('focusContradictions');
  if (cEl && contradictions) {
    const items = (contradictions.items || contradictions).slice(0, 4);
    if (!items.length) {
      cEl.innerHTML = '<p>No contradictions surfaced.</p>';
    } else {
      cEl.innerHTML = items.map(c => `
        <div class="contradiction-item">
          <div class="topic">${c.narrative || c.topic || '—'}</div>
          <div>${short(c.claim_b || c.observed_reality || '', 120)}</div>
        </div>
      `).join('');
    }
  }

  // Cross-Asset Exposure
  const assetEl = byId('focusAssets');
  if (assetEl && setups) {
    const assets = new Map();
    const items = setups.slice(0, 5);
    items.forEach(s => {
      const tags = s.asset_tags || [];
      const dir = s.narrative_primary ? 'neutral' : (s.probability_bull > 20 ? 'bullish' : 'bearish');
      tags.forEach(t => assets.set(t, dir));
    });
    if (!assets.size) {
      assetEl.innerHTML = '<p>Asset exposure pending data refresh.</p>';
    } else {
      assetEl.innerHTML = [...assets.entries()].map(([tag, dir]) =>
        `<span class="asset-tag ${dir}">${tag.toUpperCase()}</span>`
      ).join('');
      assetEl.innerHTML += '<p style="margin-top:8px;font-size:11px">Exposure map from active narratives</p>';
    }
  }
}

// ── Expand/collapse ──
function wireExpandable() {
  const cards = [...document.querySelectorAll('[data-expandable]')];
  cards.forEach(card => {
    const toggle = () => {
      const expanded = card.getAttribute('aria-expanded') === 'true';
      if (expanded) {
        card.setAttribute('aria-expanded', 'false');
        card.classList.remove('is-expanded');
        const hint = card.querySelector('.story-expand-hint');
        if (hint) hint.textContent = '↘ expand';
        return;
      }
      cards.forEach(c => {
        c.setAttribute('aria-expanded', 'false');
        c.classList.remove('is-expanded');
        const h = c.querySelector('.story-expand-hint');
        if (h) h.textContent = '↘ expand';
      });
      card.setAttribute('aria-expanded', 'true');
      card.classList.add('is-expanded');
      const hint = card.querySelector('.story-expand-hint');
      if (hint) hint.textContent = '↗ collapse';
    };

    card.addEventListener('click', toggle);
    card.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); }
    });
  });
}

// ── Freshness ──
function renderFreshness(setups, regime) {
  const el = byId('freshness');
  if (!el) return;
  const ts = setups?.generated_at || regime?.generated_at;
  if (ts) {
    el.textContent = `Updated ${timeAgo(ts)}`;
  }
}

// ── Boot ──
async function boot() {
  const [regime, setupsData, contradictionsData, storiesData] = await Promise.all([
    getJSON(API.regime, null),
    getJSON(API.setups, null),
    getJSON(API.contradictions, null),
    getJSON(API.stories, null),
  ]);

  const setups = setupsData?.items || [];
  const contradictions = contradictionsData?.items || [];

  renderRegimeBar(regime);

  // Stories — prefer website stories if available, fall back to setups
  const leadEl = byId('leadStory');
  const stackEl = byId('storyStack');

  if (setups.length) {
    if (leadEl) leadEl.innerHTML = storyCardMarkup(setups[0], 0, setups.length);
    if (stackEl) {
      stackEl.innerHTML = setups.slice(1, 8).map((s, i) => storyCardMarkup(s, i + 1, setups.length)).join('');
    }
  } else {
    if (leadEl) leadEl.innerHTML = '<p style="color:var(--text-muted);padding:20px">Intelligence update pending. Pipeline collecting data.</p>';
    if (stackEl) stackEl.innerHTML = '';
  }

  renderFocusPanel(regime, setups, contradictions);
  renderFreshness(setupsData, regime);
  wireExpandable();
}

boot();
