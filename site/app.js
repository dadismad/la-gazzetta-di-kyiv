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
  return review || 'Cross-market headlines are clustering around this theme, increasing the chance of spillover moves.';
}

function actionFor(topic){
  return 'Track confirmation in related assets before chasing price, and prioritize risk control over speed.';
}

async function load(){
  const n = await fetch('../data/narratives.json').then(r=>r.json()).catch(()=>({}));
  const reviews = (n.narrative_reviews||[]).slice(0,10);

  const updated = document.getElementById('updated');
  if(updated) updated.textContent = `Updated: ${n.generated_at || 'n/a'}`;

  const narratives = reviews.map(r=>({
    topic: (r.topic||'Narrative').toUpperCase(),
    sentence: sentenceFor(r.topic),
    context: contextFor(r.topic, r.review),
    action: actionFor(r.topic),
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
      <article class='n-card' onclick='selectNarrative(${i})'>
        <div class='n-kicker'>${x.topic}</div>
        <div class='n-headline'>${x.sentence}</div>
        <div class='n-body'>${x.context}</div>
        <div class='n-meta'><span><b>Context:</b> ${x.details[0]}</span><span><b>Action:</b> ${x.action}</span></div>
      </article>
    `).join('');
  }

  window.selectNarrative = (i)=>{
    const x = (window.__narr||[])[i]; if(!x || !detailsEl) return;
    detailsEl.innerHTML = `
      <div class='focus-kicker'>${x.topic}</div>
      <div class='focus-title'>${x.sentence}</div>
      <div class='focus-copy'>${x.context}</div>
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