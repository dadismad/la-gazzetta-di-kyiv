// La Gazzetta di Kyiv — Concrete Editorial Language
// Loads hand-written stories with direct, specific claims.

const DATA = './data/stories.json';

function byId(id) { return document.getElementById(id); }

async function getJSON(path, fallback) {
  try {
    const r = await fetch(path, { cache: 'no-store' });
    if (!r.ok) throw new Error(String(r.status));
    return await r.json();
  } catch (e) { console.warn('Fetch failed:', path); return fallback; }
}

// ── Date line ──
(function() {
  const el = byId('dateLine');
  if (!el) return;
  const now = new Date();
  const days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  const months = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  el.textContent = `${days[now.getDay()]}, ${months[now.getMonth()]} ${now.getDate()}, ${now.getFullYear()}`;
})();

// ── Render lead story ──
function renderLead(lead) {
  const consensusEl = byId('leadConsensus');
  const realityEl = byId('leadReality');
  const headlineEl = byId('leadHeadline');
  const thesisEl = byId('leadThesis');
  const implicationEl = byId('leadImplication');

  if (consensusEl) consensusEl.textContent = `«${lead.they_say}»`;
  if (realityEl) realityEl.textContent = `«${lead.reality}»`;
  if (headlineEl) headlineEl.textContent = lead.headline;
  if (thesisEl) thesisEl.textContent = lead.thesis;
  if (implicationEl) {
    implicationEl.textContent = `The actors: ${lead.actors || 'Multiple parties'}. The window: ${lead.horizon || '24–72 hours'}. The gap between consensus and reality is where capital moves.`;
  }
}

// ── Render story stack ──
function renderStack(stories) {
  const el = byId('storyStack');
  if (!el) return;
  if (!stories.length) {
    el.innerHTML = '<p style="color:var(--ink-muted);text-align:center;padding:30px;font-style:italic">Fresh intelligence arriving next cycle.</p>';
    return;
  }

  el.innerHTML = stories.map(s => `
    <article class="story-item">
      <div class="con-pair">
        <div class="they-say">
          <strong>They say</strong>
          ${s.they_say}
        </div>
        <div class="reality-say">
          <strong>Reality</strong>
          ${s.reality}
        </div>
      </div>
      <h3>${s.headline}</h3>
      ${s.sector ? `<p class="story-thesis" style="font-family:var(--sans);font-size:10px;color:var(--sky);text-transform:uppercase;letter-spacing:0.08em">${s.sector}</p>` : ''}
    </article>`).join('');
}

// ── Render sidebar with human-facing labels ──
function renderSidebar(lead, stories) {
  // Regime — show what it means, not just the label
  const rEl = byId('regimeStatus');
  if (rEl && lead) {
    rEl.innerHTML = `
      <div style="font-family:var(--serif);font-size:20px;font-weight:700;color:var(--ink);margin-bottom:6px">Repricing Risk</div>
      <div style="font-family:var(--sans);font-size:12px;color:var(--ink-muted);line-height:1.5">
        Markets are repricing Middle East energy corridor risk. Gulf states are directly affected — not just watching. The OECD has flagged a <em>dark scenario</em> for prolonged crisis.
      </div>`;
  }

  // Signal Map → renamed to "Today's Stories"
  const sEl = byId('signalMap');
  if (sEl && stories) {
    const label = sEl.parentElement?.querySelector('h3');
    if (label) label.textContent = 'In This Edition';
    sEl.innerHTML = stories.map(s => `
      <div style="padding:5px 0;border-bottom:1px solid var(--divider-light);font-size:13px;line-height:1.4;color:var(--ink-light)">
        <span style="font-family:var(--sans);font-size:9px;color:var(--sky);text-transform:uppercase;letter-spacing:0.06em;display:block">${s.sector || 'story'}</span>
        ${s.headline}
      </div>`).join('');
  }

  // Source count with context
  const scEl = byId('sourceCount');
  if (scEl) {
    const label = scEl.parentElement?.querySelector('h3');
    if (label) label.textContent = 'Data Freshness';
    scEl.innerHTML = `
      <div style="font-family:var(--sans);font-size:11px;color:var(--ink-muted);line-height:1.5">
        Compiled from RSS feeds, Reddit, and financial news sources. Updated every 12 hours.
      </div>`;
  }

  // Footer freshness
  const ffEl = byId('footerFreshness');
  if (ffEl) {
    const now = new Date();
    ffEl.textContent = `Updated ${now.toLocaleTimeString()}`;
  }
}

// ── Boot ──
async function boot() {
  const data = await getJSON(DATA, null);

  if (!data || !data.lead) {
    // Graceful fallback
    const leadEl = byId('leadHeadline');
    if (leadEl) leadEl.textContent = 'Intelligence update in progress';
    return;
  }

  renderLead(data.lead);
  renderStack(data.stories || []);
  renderSidebar(data.lead, data.stories || []);
}

boot();
