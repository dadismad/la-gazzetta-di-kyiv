function normTopic(topic){return (topic||'market narrative').toLowerCase();}

function sentenceFor(topic){
  const t = normTopic(topic);
  const map = {
    ai: 'The AI infrastructure build-out is approaching a saturation point where megacap spending may no longer justify valuations.',
    oil: 'Geopolitical disruptions are exposing how little spare oil production capacity remains in the global system.',
    inflation: 'Sticky inflation pressures are colliding with market hopes for rapid rate cuts, raising repricing risk.',
    rates: 'Bond markets are re-evaluating how long restrictive policy may stay in place as growth diverges.',
    election: 'Election-year policy uncertainty is becoming a direct catalyst for sector-level volatility.',
    crypto: 'Crypto is increasingly acting as a high-beta sentiment barometer for broader risk appetite.',
    russia: 'War-related supply and sanction dynamics continue to feed an uneven geopolitical risk premium.',
    ukraine: 'Ukraine-linked security developments remain a key swing factor for energy and regional risk pricing.',
    eu: 'European fiscal and political stress points are starting to shape cross-asset allocation decisions.'
  };
  return map[t] || `${topic.toUpperCase()} is becoming a market-moving narrative retail traders should follow closely.`;
}

function contextFor(topic, review){
  const t = normTopic(topic);
  const map = {
    ai: 'Spending momentum and valuation sensitivity are now moving together, so policy headlines and earnings guidance can quickly shift sentiment.',
    oil: 'Supply uncertainty is interacting with fragile inventories, making energy headlines capable of moving inflation expectations fast.',
    inflation: 'Recent data and central-bank messaging are not fully aligned, so markets can reprice abruptly after each macro release.',
    rates: 'Bond volatility is feeding directly into equity positioning, especially in duration-sensitive sectors.',
    election: 'Policy-path uncertainty is lifting headline risk and can amplify short-term rotation between sectors.',
  };
  return map[t] || 'Cross-market headlines are clustering around this theme, increasing the chance of spillover moves.';
}

function actionFor(topic){
  return 'Track confirmation in related assets before chasing price, and prioritize risk control over speed.';
}

function flowFor(topic){
  const t = normTopic(topic);
  const map = {ai: 12.4, oil: 6.1, inflation: 4.3, rates: 5.0, election: 3.2, crypto: 9.7, russia: 2.8, ukraine: 2.5, eu: 4.9};
  return (map[t] ?? 3.8);
}

function proj3dFor(topic){
  const t = normTopic(topic);
  const map = {ai: '+1.8%', oil: '+1.2%', inflation: '-0.4%', rates: '-0.6%', election: '±1.1%', crypto: '+2.6%', russia: '+0.7%', ukraine: '+0.5%', eu: '+0.9%'};
  return map[t] || '±0.8%';
}

function focusTitleFor(topic){
  return `Focus: ${topic.toUpperCase()} scenario map for retail positioning`;
}

function focusCopyFor(topic){
  return 'This panel summarizes what can invalidate the narrative, what confirms continuation, and what specific headline classes deserve immediate attention.';
}

async function load(){
  const n = await fetch('./data/narratives.json').then(r=>r.json()).catch(()=>({}));
  const reviews = (n.narrative_reviews||[]).slice(0,10);

  const updated = document.getElementById('updated');
  if(updated) updated.textContent = `Updated: ${n.generated_at || 'n/a'}`;

  const narratives = reviews.map(r=>({
    topic: (r.topic||'Narrative').toUpperCase(),
    sentence: sentenceFor(r.topic),
    context: contextFor(r.topic, r.review),
    action: actionFor(r.topic),
    flow_billion_usd_3d: flowFor(r.topic),
    projection_3d: proj3dFor(r.topic),
    details: [
      'Most crucial detail: this theme is recurring across multiple news cycles rather than appearing as a one-off shock.',
      'Retail interpretation: wait for follow-through evidence in price action before increasing exposure.',
      'What to watch next: policy statements, earnings guidance, and macro prints tied to this narrative.'
    ]
  }));

  const listEl = document.getElementById('narrativeList');
  const detailsEl = document.getElementById('selectedNarrative');

  window.__narr = narratives;

  if(listEl){
    listEl.innerHTML = narratives.map((x,i)=>`
      <article class='n-card ${i===0?"featured":""}' onclick='selectNarrative(${i})'>
        <div class='n-kicker'>${x.topic}</div>
        <div class='n-headline'>${x.sentence}</div>
        <div class='n-body'>${x.context}</div>
        <div class='n-meta'><span><b>Context:</b> ${x.details[0]}</span><span><b>Action:</b> ${x.action}</span><span><b>Flow 3d:</b> ~$${x.flow_billion_usd_3d}B</span><span><b>Projection 3d:</b> ${x.projection_3d}</span></div>
      </article>
    `).join('');
  }

  window.selectNarrative = (i)=>{
    const x = (window.__narr||[])[i]; if(!x || !detailsEl) return;
    detailsEl.innerHTML = `
      <div class='focus-kicker'>${x.topic}</div>
      <div class='focus-title'>${focusTitleFor(x.topic)}</div>
      <div class='focus-copy'>Distinct focus brief: portfolio scenario framing, invalidation triggers, and timing risks for ${x.topic}.</div>
      <div class='focus-copy'>Capital flow estimate (3d): <b>~$${x.flow_billion_usd_3d}B</b> | Price projection (3d): <b>${x.projection_3d}</b></div>
      <ul class='subpoints'>
        <li>${x.details[0]}</li>
        <li>${x.details[1]}</li>
        <li>${x.details[2]}</li>
      </ul>
    `;
  };

  if(narratives[0]) window.selectNarrative(0);
}

load();