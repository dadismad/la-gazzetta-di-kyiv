async function load(){
  const [n,s,t]=await Promise.all([
    fetch('../data/narratives.json').then(r=>r.json()).catch(()=>({})),
    fetch('../data/source_registry_ranked.json').then(r=>r.json()).catch(()=>({sources:[]})),
    fetch('../data/representation_techniques.json').then(r=>r.json()).catch(()=>({techniques:[]})),
  ]);

  const reviews=(n.narrative_reviews||[]);
  const updated=document.getElementById('updated');
  if(updated) updated.textContent=`Updated: ${n.generated_at||'n/a'} · items(24h): ${n.recent_items_24h||0}`;

  const regimesEl=document.getElementById('regimes');
  if(regimesEl){
    const regimes=reviews.slice(0,6).map(x=>({name:x.topic.toUpperCase(),dom:x.intensity_score,momentum:x.momentum}));
    regimesEl.innerHTML=regimes.map(r=>`<div class='regime-item'><div class='title'>${r.name}</div><div class='muted'>Dominance: ${r.dom}% · ${r.momentum}</div></div>`).join('');
  }

  const listEl=document.getElementById('narrativeList');
  if(listEl){
    listEl.innerHTML=reviews.map((x,i)=>`<div class='n-item' onclick='selectNarrative(${i})'><span class='badge'>${x.topic.slice(0,3).toUpperCase()}</span><div><div class='title'>${x.topic.toUpperCase()}</div><div>${x.review}</div></div><div>${x.intensity_score}%</div><div>${(Math.max(1,Math.round((x.intensity_score||0)/12))).toFixed(1)}x</div></div>`).join('');
    window.__reviews=reviews;
    if(reviews[0]) selectNarrative(0);
  }

  const sel=document.getElementById('selectedNarrative');
  window.selectNarrative=(i)=>{
    if(!sel) return;
    const x=(window.__reviews||[])[i]; if(!x) return;
    sel.innerHTML=`<div class='muted'>Selected Narrative</div><h3>${x.topic.toUpperCase()}</h3><div class='big-score'>${x.intensity_score}</div><p>${x.review}</p><p class='muted'>Mentions 24h: ${x.mentions_24h} · Momentum: ${x.momentum}</p>`;
  };

  const reviewsEl=document.getElementById('reviews');
  if(reviewsEl){
    reviewsEl.innerHTML=reviews.map(x=>`<article class='review'><b>${x.topic.toUpperCase()}</b><div class='muted'>Mentions: ${x.mentions_24h} · Intensity: ${x.intensity_score} · Momentum: ${x.momentum}</div><p>${x.review}</p></article>`).join('');
  }

  const sources=document.getElementById('sources');
  if(sources){
    sources.innerHTML=(s.sources||[]).slice(0,120).map(x=>`<tr><td><a href='${x.url}' target='_blank'>${x.name}</a></td><td>${x.platform}</td><td>${x.score}</td><td>${x.access}</td></tr>`).join('');
  }

  const tech=document.getElementById('techniques');
  if(tech){
    tech.innerHTML=(t.techniques||[]).slice(0,12).map(x=>`<div class='review'><b>${x.technique}</b> · evidence ${x.evidence_count} · priority ${x.adoption_priority}<p>${x.implementation_note}</p></div>`).join('');
  }
}
load();