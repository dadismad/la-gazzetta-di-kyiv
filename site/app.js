function el(id){ return document.getElementById(id); }

const BUILD_META = {
  commit: '__BUILD_COMMIT__',
  generatedAt: '__BUILD_TIME__'
};

let STATE = {
  regime: null,
  setups: [],
  divergences: [],
  contradictions: [],
  aftershocks: []
};

async function fetchJSON(path, fallback){
  try{
    const r = await fetch(path, {cache:'no-store'});
    if(!r.ok) throw new Error(`${path} ${r.status}`);
    return await r.json();
  }catch(e){
    console.warn('fetch failed', path, e.message);
    return fallback;
  }
}

function renderRegime(){
  const r = STATE.regime || {};
  const freshnessMin = Math.round((r.data_freshness_seconds || 0) / 60);
  const hasFreshness = Number.isFinite(freshnessMin) && freshnessMin > 0;
  const freshnessLabel = hasFreshness ? (freshnessMin >= 60 ? `${Math.round(freshnessMin/60)}h ago` : `${freshnessMin}m ago`) : 'Live cycle';
  const node = el('selectedNarrative');
  node.innerHTML = `
    <div class='focus-title'>Regime: ${r.regime_label || 'Pending update'}</div>
    <div class='kpi'><span>Risk State</span><b>${r.risk_state || 'Pending update'}</b></div>
    <div class='kpi'><span>Confidence</span><b>${((r.confidence||0)*100).toFixed(0)}%</b></div>
    <div class='kpi'><span>Sources</span><b>${r.source_count || 0}</b></div>
    <div class='kpi'><span>Freshness</span><b>${freshnessLabel}</b></div>
    <div class='focus-copy'><b>Doctrine:</b> Big picture over small one. Keep thesis + invalidation visible.</div>
  `;

  const heroSources = el('heroSources');
  const heroRegime = el('heroRegime');
  const heroFreshness = el('heroFreshness');
  if(heroSources) heroSources.textContent = String(r.source_count || 0);
  if(heroRegime) heroRegime.textContent = r.regime_label || 'Pending';
  if(heroFreshness) heroFreshness.textContent = freshnessLabel;
}

function renderFrames(){
  const frames = STATE.divergences;
  const target = el('frameList');
  target.innerHTML = frames.map((d,i)=>`
    <div class='frame-item ${i===0?'active':''}' data-idx='${i}'>
      <div class='frame-cat'>Belief vs Reality</div>
      <div class='frame-name'>${(d.narrative||'macro').toUpperCase()}</div>
      <div class='frame-note'>Divergence score: ${d.divergence_score ?? 'n/a'}</div>
    </div>
  `).join('') || `<div class='claim-empty'>No divergence data yet.</div>`;

  target.querySelectorAll('.frame-item').forEach(n=>{
    n.onclick=()=>{
      target.querySelectorAll('.frame-item').forEach(x=>x.classList.remove('active'));
      n.classList.add('active');
      renderClaims(Number(n.dataset.idx));
    };
  });
}

function rowForSetup(s, i){
  const sum = (s.probability_base||0)+(s.probability_bull||0)+(s.probability_bear||0);
  return `<div class='claim-row' data-id='${i}'>
    <div class='claim-head'>
      <div class='claim-idx'>${String(i+1).padStart(2,'0')}</div>
      <div><div class='claim-title'>${s.title}</div><div class='claim-sub'>${s.thesis}</div></div>
      <div class='claim-pot'>${Math.round((s.confidence||0)*100)}%</div>
    </div>
    <div class='claim-extra'>
      <div class='insight-line'><span class='badge'>Horizon</span> ${s.horizon}</div>
      <div class='insight-line'><span class='badge'>Flow 3d</span> n/a</div>
      <div class='insight-line'><span class='badge'>Projection 3d</span> n/a</div>
      <div class='insight-line'><span class='badge'>Prob.</span> Base ${s.probability_base}% / Bull ${s.probability_bull}% / Bear ${s.probability_bear}% (Σ ${sum})</div>
      <div class='insight-line'><span class='badge'>Invalidation</span> ${(s.invalidation_triggers||[]).join(' · ')}</div>
      <div class='insight-line'><span class='badge'>Retail</span> ${(s.retail_execution||[]).join(' · ')}</div>
    </div>
  </div>`;
}

function titleCase(s){ return (s||'').split(' ').map(w=>w?`${w[0].toUpperCase()}${w.slice(1)}`:'').join(' '); }

function extractActors(text=''){
  const candidates = (text.match(/\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}|AI|EU|US|NATO|China|Russia|Fed|ECB|OPEC|Ukraine)\b/g) || [])
    .filter(x => x.length > 1);
  const uniq = [...new Set(candidates)];
  return uniq.slice(0,4);
}

function narrativeHeadline(rawTitle, i){
  const base = (rawTitle || '').replace(/^narrative\s+acceleration:\s*/i,'').trim();
  if(!base) return `${String(i+1).padStart(2,'0')}. Risk narrative shifts and repricing pressure builds`;
  const cap = base.toUpperCase()==='AI' ? 'AI' : titleCase(base);
  return `${String(i+1).padStart(2,'0')}. ${cap}: claim intensity rises, repricing risk follows`;
}

function storyCardForSetup(s, i){
  const title = narrativeHeadline(s.title, i);
  const dev = s.thesis || 'Story development is building, but breadth confirmation is still incomplete.';
  const confidence = Math.round((s.confidence||0)*100);
  const pb = s.probability_bull ?? 0;
  const pbase = s.probability_base ?? 0;
  const pbr = s.probability_bear ?? 0;
  const inv = (s.invalidation_triggers||[])[0] || 'Narrative momentum reversal';

  const direction = pb >= pbr ? 'upside continuation' : 'downside repricing';
  const projection = pb >= pbr ? '+1.2% to +3.8%' : '-1.2% to -3.8%';
  const actors = extractActors(`${s.title||''} ${s.thesis||''}`).join(', ') || 'EU desks, US macro funds, policy institutions';

  return `
  <article class='story-card'>
    <div class='story-title'>${title}</div>
    <div class='story-dev'><b>Actors:</b> ${actors}</div>
    <div class='story-dev'><b>Core claim:</b> ${dev}</div>
    <div class='story-imp'><b>Transmission:</b> Liquidity and risk appetite are carrying this claim into cross-asset positioning. Model confidence is <b>${confidence}%</b> (base <b>${pbase}%</b>, upside <b>${pb}%</b>, downside <b>${pbr}%</b>).</div>
    <div class='story-fx'><b>Repricing thesis (24–72h):</b> ${direction}, expected repricing <b>${projection}</b>. <b>Invalidation:</b> ${inv}.</div>
  </article>`;
}

function renderClaims(frameIdx=0){
  const narrative = STATE.divergences[frameIdx]?.narrative;
  let setups = STATE.setups;
  if(narrative){
    setups = setups.filter(s => (s.title||'').toLowerCase().includes((narrative||'').toLowerCase()));
    if(!setups.length) setups = STATE.setups;
  }

  const railItems = STATE.contradictions.slice(0,3).map(c=>{
    const a = c.claim_a || 'Claim A';
    const b = c.claim_b || 'Claim B';
    const u = c.urgency || 'medium';
    return `${a} is challenged by ${b} (${u} urgency)`;
  });
  const rail = railItems.join(' • ');
  const list = el('claimsList');
  list.innerHTML = `${rail ? `<div class='claim-empty'><b>Stories conflict monitor:</b> ${rail}</div>`:''}` +
    (setups.map(storyCardForSetup).join('') || `<div class='claim-empty'>No active claims yet.</div>`);
}

function bindControls(){
  el('searchBox').oninput = (e)=>{
    const q=(e.target.value||'').toLowerCase();
    document.querySelectorAll('.story-card').forEach(r=>{
      r.style.display = r.innerText.toLowerCase().includes(q) ? 'block' : 'none';
    });
  };
  el('collapseAll').onclick=()=>document.querySelectorAll('.story-card').forEach(r=>{ r.style.display='block'; });
  el('expandAll').onclick=()=>document.querySelectorAll('.story-card').forEach(r=>{ r.style.display='block'; });
}

function renderBuildMeta(){
  const commitNode = el('buildCommit');
  const timeNode = el('buildTime');
  if(commitNode) commitNode.textContent = BUILD_META.commit;
  if(timeNode) timeNode.textContent = BUILD_META.generatedAt;
}

async function boot(){
  const [regime, setups, divergences, contradictions, aftershocks] = await Promise.all([
    fetchJSON('./api/v1/home/regime.json', {}),
    fetchJSON('./api/v1/home/setups.json', {items:[]}),
    fetchJSON('./api/v1/home/divergences.json', {items:[]}),
    fetchJSON('./api/v1/home/contradictions.json', {items:[]}),
    fetchJSON('./api/v1/home/aftershocks.json', {items:[]})
  ]);

  STATE.regime = regime;
  STATE.setups = setups.items || [];
  STATE.divergences = divergences.items || [];
  STATE.contradictions = contradictions.items || [];
  STATE.aftershocks = aftershocks.items || [];

  renderBuildMeta();
  renderRegime();
  renderFrames();
  renderClaims(0);
  bindControls();
}

boot();
