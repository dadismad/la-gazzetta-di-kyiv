function el(id){ return document.getElementById(id); }

async function fetchJSON(path, fallback){
  try {
    const r = await fetch(path, { cache: 'no-store' });
    if (!r.ok) throw new Error(`${r.status}`);
    return await r.json();
  } catch {
    return fallback;
  }
}

function setupCard(s){
  const conf = Math.round((s.confidence || 0) * 100);
  return `<article class='card'>
    <h3>${s.title}</h3>
    <p><b>Claim:</b> ${s.thesis}</p>
    <p><b>Probabilities:</b> Base ${s.probability_base}% · Bull ${s.probability_bull}% · Bear ${s.probability_bear}%</p>
    <p><b>Invalidation:</b> ${(s.invalidation_triggers || []).join(' · ')}</p>
    <p><b>Retail execution:</b> ${(s.retail_execution || []).join(' · ')}</p>
    <span class='tag'>Confidence ${conf}%</span><span class='tag'>Horizon ${s.horizon || '24-72h'}</span>
  </article>`;
}

function contradictionCard(c){
  return `<article class='card'>
    <h3>${c.claim_a}</h3>
    <p><b>Counter-claim:</b> ${c.claim_b}</p>
    <p><b>Urgency:</b> ${c.urgency} · <b>Window:</b> ${c.invalidation_window}</p>
  </article>`;
}

function renderStaticBlocks(){
  el('geopoliticalFlashpoints').innerHTML = `
    <ul class='compact'>
      <li>Black Sea / energy corridor security risk and sanctions path uncertainty.</li>
      <li>NATO procurement cycle vs fiscal fatigue in Europe.</li>
      <li>China growth signaling vs property/debt drag narrative conflict.</li>
    </ul>`;

  el('prestigeSport').innerHTML = `
    <article class='card'>
      <h3>Formula 1 · Sovereign branding race</h3>
      <p>Teams and hosts compete on prestige, capital attraction, and technology signaling.</p>
    </article>
    <article class='card'>
      <h3>Cycling / Tennis / Yachting</h3>
      <p>Luxury sponsorship cycles, tourism diplomacy, and aspirational consumer demand remain core lenses.</p>
    </article>`;

  el('volatilityWatch').innerHTML = `
    <div class='kpi'><span>Rates volatility (MOVE lens)</span><b>Elevated</b></div>
    <div class='kpi'><span>Equity vol (VIX lens)</span><b>Compressed but fragile</b></div>
    <div class='kpi'><span>Energy shock sensitivity</span><b>High</b></div>`;

  el('crossAssetContagion').innerHTML = `
    <ul class='compact'>
      <li>Energy narrative → inflation expectations → rates repricing → equity multiple compression.</li>
      <li>AI capex narrative → equity leadership concentration → duration sensitivity in growth assets.</li>
      <li>Geopolitical escalation → safe-haven bid (USD/gold) + regional beta underperformance.</li>
    </ul>`;
}

async function boot(){
  const regime = await fetchJSON('./api/v1/home/regime.json', {});
  const setups = await fetchJSON('./api/v1/home/setups.json', { items: [] });
  const contradictions = await fetchJSON('./api/v1/home/contradictions.json', { items: [] });
  const divergences = await fetchJSON('./api/v1/home/divergences.json', { items: [] });

  el('heroRegime').textContent = regime.regime_label || 'Pending';
  el('heroConfidence').textContent = regime.confidence ? `${Math.round(regime.confidence * 100)}%` : '-';
  el('heroSources').textContent = regime.source_count || '-';
  el('heroUpdated').textContent = regime.updated_at || '-';

  const topSetups = (setups.items || []).slice(0, 6);
  el('dominantNarratives').innerHTML = topSetups.map(s => `<span class='tag'>${s.title.replace('Narrative acceleration: ','')}</span>`).join('');
  el('narrativeVelocity').innerHTML = topSetups.map((s,i)=>`<div class='kpi'><span>${i+1}. ${s.title.replace('Narrative acceleration: ','')}</span><b>${Math.round((s.confidence||0)*100)}%</b></div>`).join('');
  el('contradictionMap').innerHTML = (contradictions.items || []).slice(0,5).map(contradictionCard).join('');
  el('convictionSetups').innerHTML = topSetups.map(setupCard).join('');

  el('regimeDashboard').innerHTML = `
    <div class='kpi'><span>Regime Label</span><b>${regime.regime_label || 'Pending'}</b></div>
    <div class='kpi'><span>Risk State</span><b>${regime.risk_state || 'Pending'}</b></div>
    <div class='kpi'><span>Confidence</span><b>${regime.confidence ? `${Math.round(regime.confidence*100)}%` : '-'}</b></div>
    <div class='kpi'><span>Data Freshness</span><b>${regime.data_freshness_seconds || '-'}s</b></div>
  `;

  el('retailSignals').innerHTML = topSetups.map(s=>`<article class='card'><h3>${s.title}</h3><p><b>Positioning angle:</b> ${(s.retail_execution||[]).join(' · ')}</p><p><b>Invalidation first:</b> ${(s.invalidation_triggers||[])[0] || 'N/A'}</p></article>`).join('')
    + (divergences.items||[]).slice(0,2).map(d=>`<article class='card'><h3>${d.narrative} divergence</h3><p><b>Market belief:</b> ${d.market_belief}</p><p><b>Hidden risk:</b> ${d.observed_reality}</p></article>`).join('');

  renderStaticBlocks();
}

boot();
