// La Gazzetta di Kyiv — Contradiction-First Narrative Intelligence
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
  } catch (e) { console.warn('Fetch failed:', path); return fallback; }
}

function short(s, n) { const v = String(s||'').trim(); return v.length>n ? v.slice(0,n-1)+'…' : v; }

// ── Date line ──
(function() {
  const el = byId('dateLine');
  if (!el) return;
  const now = new Date();
  const days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  const months = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  el.textContent = `${days[now.getDay()]}, ${months[now.getMonth()]} ${now.getDate()}, ${now.getFullYear()}`;
})();

// ── Find the best contradiction for a story ──
function findContradiction(setup, contradictions) {
  const items = contradictions?.items || contradictions || [];
  const topic = (setup.setup_id || setup.title || '').toLowerCase().replace('n21_','');
  const match = items.find(c => (c.narrative || '').toLowerCase() === topic);
  if (match && match.claim_a && match.claim_b) {
    return { claimA: match.claim_a, claimB: match.claim_b, urgency: match.urgency || 'medium' };
  }
  // fallback: construct from setup data
  const thesis = setup.thesis || '';
  return {
    claimA: 'Consensus pricing reflects status quo continuation',
    claimB: thesis || 'Second-order effects remain underpriced',
    urgency: 'medium'
  };
}

// ── Render lead story ──
function renderLead(setup, contradictions) {
  const con = findContradiction(setup, contradictions);
  const headline = setup.title || setup.event || 'Narrative Signal';
  const thesis = setup.thesis || '';

  const consensusEl = byId('leadConsensus');
  const realityEl = byId('leadReality');
  const headlineEl = byId('leadHeadline');
  const thesisEl = byId('leadThesis');
  const implicationEl = byId('leadImplication');

  if (consensusEl) consensusEl.textContent = `«${con.claimA}»`;
  if (realityEl) realityEl.textContent = `«${con.claimB}»`;
  if (headlineEl) headlineEl.textContent = headline;
  if (thesisEl) thesisEl.textContent = thesis;
  if (implicationEl) {
    const actors = (setup.actors || []).slice(0, 3).join(', ');
    const horizon = setup.horizon || '24–72 hours';
    implicationEl.textContent = actors
      ? `The actors: ${actors}. The window: ${horizon}. The gap between consensus and reality is where capital moves.`
      : `Repricing window: ${horizon}. This contradiction resolves when one side is proven wrong.`;
  }
}

// ── Render story stack ──
function renderStack(setups, contradictions) {
  const el = byId('storyStack');
  if (!el) return;
  if (!setups.length) {
    el.innerHTML = '<p style="color:var(--ink-muted);text-align:center;padding:30px;font-style:italic">Fresh intelligence arriving next cycle.</p>';
    return;
  }

  el.innerHTML = setups.map((setup, i) => {
    const con = findContradiction(setup, contradictions);
    return `
      <article class="story-item">
        <div class="con-pair">
          <div class="they-say">
            <strong>They say</strong>
            ${short(con.claimA, 160)}
          </div>
          <div class="reality-say">
            <strong>Reality</strong>
            ${short(con.claimB, 160)}
          </div>
        </div>
        <h3>${setup.title || setup.event || 'Story'}</h3>
        <p class="story-thesis">${short(setup.thesis || '', 240)}</p>
      </article>`;
  }).join('');
}

// ── Render sidebar ──
function renderSidebar(regime, setups) {
  // Regime
  const rEl = byId('regimeStatus');
  if (rEl && regime) {
    const label = regime.regime_label || 'Narrative Transition';
    const risk = regime.risk_state || 'neutral';
    const conf = regime.confidence ? `${Math.round(regime.confidence * 100)}%` : '—';
    rEl.innerHTML = `${label}<div class="regime-meta">Risk: ${risk} · Confidence: ${conf} · Sources: ${regime.source_count || '—'}</div>`;
  }

  // Signal bars
  const sEl = byId('signalMap');
  if (sEl && setups) {
    sEl.innerHTML = setups.slice(0, 6).map(s => {
      const conf = Math.round((s.confidence || 0.5) * 100);
      const topic = (s.setup_id || s.title || '').replace('n21_','').replace('Narrative acceleration: ','');
      return `
        <div class="signal-bar">
          <span class="signal-topic">${short(topic, 10)}</span>
          <div class="signal-fill" style="width:${conf}%"></div>
          <span style="font-size:10px;color:var(--ink-muted);font-family:var(--sans)">${conf}%</span>
        </div>`;
    }).join('');
  }

  // Source count
  const scEl = byId('sourceCount');
  if (scEl && regime) {
    scEl.innerHTML = `<strong style="font-family:var(--serif);font-size:24px;color:var(--gold-dark)">${regime.source_count || '—'}</strong><br><span style="font-family:var(--sans);font-size:11px;color:var(--ink-muted)">active sources this cycle</span>`;
  }

  // Footer freshness
  const ffEl = byId('footerFreshness');
  if (ffEl && regime) {
    const ts = regime.generated_at;
    if (ts) {
      try { ffEl.textContent = `Updated ${new Date(ts).toLocaleTimeString()}`; }
      catch { ffEl.textContent = ''; }
    }
  }
}

// ── Boot ──
async function boot() {
  const [regime, setupsData, contradictions] = await Promise.all([
    getJSON(API.regime, null),
    getJSON(API.setups, null),
    getJSON(API.contradictions, null),
  ]);

  const setups = setupsData?.items || [];
  const lead = setups[0] || null;
  const stack = setups.slice(1, 7);

  if (lead) renderLead(lead, contradictions);
  renderStack(stack, contradictions);
  renderSidebar(regime, setups);
}

boot();
