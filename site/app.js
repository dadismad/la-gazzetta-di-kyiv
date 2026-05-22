async function load(){
  const [n,s,t]=await Promise.all([
    fetch('../data/narratives.json').then(r=>r.json()).catch(()=>({})),
    fetch('../data/source_registry_ranked.json').then(r=>r.json()).catch(()=>({sources:[]})),
    fetch('../data/representation_techniques.json').then(r=>r.json()).catch(()=>({techniques:[]})),
  ]);
  document.getElementById('updated').textContent = `Updated: ${n.generated_at||'n/a'} · items(24h): ${n.recent_items_24h||0}`;
  const kpi = document.getElementById('kpi');
  const tops=(n.narrative_reviews||[]).slice(0,3);
  kpi.innerHTML = tops.map(x=>`<div class='card'><b>${x.topic}</b><br>Intensity ${x.intensity_score}/100<br>Momentum: ${x.momentum}</div>`).join('');
  const reviews = document.getElementById('reviews');
  reviews.innerHTML = (n.narrative_reviews||[]).map(x=>`<article class='review'><h3>${x.topic.toUpperCase()}</h3><div class='sub'>Mentions: ${x.mentions_24h} · Intensity: ${x.intensity_score} · Momentum: ${x.momentum}</div><p>${x.review}</p></article>`).join('') || '<p>No reviews yet.</p>';
  const sources = document.getElementById('sources');
  const sorted=(s.sources||[]).sort((a,b)=> (a.access||'').localeCompare(b.access||'') || ((+b.score||0)-(+a.score||0)));
  sources.innerHTML = sorted.slice(0,80).map(x=>`<tr><td><a href='${x.url}' target='_blank'>${x.name}</a></td><td>${x.platform}</td><td>${x.score}</td><td>${x.access}</td><td>${x.description||''}</td></tr>`).join('');
  const tech = document.getElementById('techniques');
  tech.innerHTML=(t.techniques||[]).slice(0,12).map(x=>`<div class='review'><b>${x.technique}</b> · evidence ${x.evidence_count} · priority ${x.adoption_priority}<p>${x.implementation_note}</p></div>`).join('') || '<p>No technique research yet.</p>';
}
load();