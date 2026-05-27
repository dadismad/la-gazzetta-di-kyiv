function byId(id){ return document.getElementById(id); }

async function getJSON(path, fallback){
  try{
    const r = await fetch(path,{cache:'no-store'});
    if(!r.ok) throw new Error(String(r.status));
    return await r.json();
  }catch{ return fallback; }
}

function cleanTitle(t=''){ return String(t).replace('Narrative acceleration: ','').trim(); }
function short(s='', n=180){ const v=String(s||'').trim(); return v.length>n?`${v.slice(0,n-1)}…`:v; }

function storyItem(title, body){
  return `<div class="item"><h4>${title}</h4><p>${body}</p></div>`;
}

function leadTemplate(s, regime){
  const title = cleanTitle(s?.title || 'Narrative Repricing Risk Is Back');
  const thesis = s?.thesis || 'Narrative momentum is moving faster than consensus positioning, especially where policy confidence is thin.';
  const trigger = (s?.invalidation_triggers || [])[0] || 'Watch for a confidence break in policy guidance over the next 24–72h.';
  const retail = (s?.retail_execution || []).slice(0,2).join(' · ') || 'Use staged entries; avoid one-way concentration.';
  return `
    <h3>${title}</h3>
    <p><b>What happened:</b> ${short(thesis, 230)}</p>
    <p><b>Why a normal reader should care:</b> this changes expected risk in portfolios exposed to rates, growth multiples, and energy-sensitive sectors.</p>
    <p><b>24–72h lens:</b> ${trigger}</p>
    <p><b>Practical positioning:</b> ${retail}</p>
    <p><b>Regime context:</b> ${regime.regime_label || 'Pending'} (${Math.round((regime.confidence||0)*100)}% confidence)</p>`;
}

async function boot(){
  const setups = await getJSON('./api/v1/home/setups.json',{items:[]});
  const contradictions = await getJSON('./api/v1/home/contradictions.json',{items:[]});
  const regime = await getJSON('./api/v1/home/regime.json',{});

  const items = (setups.items || []).slice(0,9);
  const lead = items[0] || null;

  if(byId('leadStory')) byId('leadStory').innerHTML = leadTemplate(lead, regime);

  if(byId('topStoryGrid')){
    byId('topStoryGrid').innerHTML = items.slice(1,4).map(s=>`
      <article class="story-card">
        <h4>${cleanTitle(s.title)}</h4>
        <p><b>Human view:</b> ${short(s.thesis,115)}</p>
        <p><b>Action cue:</b> ${short(((s.retail_execution||[])[0]||'Reduce noise, wait for confirmation.'),95)}</p>
      </article>`).join('') || '<p>No additional briefs yet.</p>';
  }

  if(byId('macroStories')){
    const macro = items.slice(0,3).map(s=>storyItem(
      cleanTitle(s.title),
      `<b>Signal:</b> ${short(s.thesis,110)} <br><b>Transmission:</b> ${short(((s.invalidation_triggers||[])[0]||'Policy confidence shifts pricing.'),85)} <br><b>Retail action:</b> ${short(((s.retail_execution||[])[0]||'Use staged entries and risk limits.'),85)}`
    )).join('');
    byId('macroStories').innerHTML = macro || '<p>No macro stories yet.</p>';
  }

  if(byId('politicsStories')){
    const pol = (contradictions.items||[]).slice(0,3).map(c=>storyItem(
      c.claim_a || 'Policy narrative conflict',
      `<b>Incentive conflict:</b> ${short(c.claim_b||'Competing legitimacy and budget constraints.',120)} <br><b>Why readers care:</b> policy contradictions often reprice risk before official guidance updates.`
    )).join('');
    byId('politicsStories').innerHTML = pol || '<p>No politics stories yet.</p>';
  }

  if(byId('geopoliticsStories')){
    const geo = items.slice(3,6).map(s=>storyItem(
      cleanTitle(s.title),
      `<b>Flashpoint:</b> ${short(s.thesis,95)} <br><b>Spillover:</b> ${short(((s.invalidation_triggers||[])[0]||'Energy, FX and volatility channels respond first.'),95)} <br><b>Watch:</b> 24–72h transmission into oil, DXY, and equity vol.`
    )).join('');
    byId('geopoliticsStories').innerHTML = geo || '<p>No geopolitics stories yet.</p>';
  }

  if(byId('niColumnCard')){
    const c = (contradictions.items||[])[0];
    byId('niColumnCard').innerHTML = c ? `
      <article class="ni-card">
        <h3>${c.claim_a}</h3>
        <p><b>Consensus:</b> ${c.claim_b}</p>
        <p><b>Contradiction:</b> ${short(c.why_it_matters || 'Incentive mismatch between policy signaling and market positioning increases repricing risk.',170)}</p>
        <p><b>Invalidation:</b> if cross-source confirmation weakens for two consecutive cycles, reduce conviction and cut risk.</p>
        <p><b>24–72h positioning:</b> prioritize defined-risk structures; avoid over-concentrated directional bets into event windows.</p>
        <span class="badge">Actors</span><span class="badge">Incentives</span><span class="badge">Contradictions</span><span class="badge">Inval. first</span>
      </article>` : '<p>Column pending latest contradiction map.</p>';
  }
}

boot();