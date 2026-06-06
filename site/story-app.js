// story-app.js — Immersive single-story intel report page
// Loads story by ?id= param, renders full intel report layout

(function() {
  'use strict';

  const STORIES_PATH = './data/stories.json';
  const STORIES_RU_PATH = './data/stories_ru.json';
  const LIVING_PATH = './data/living_stories.json';

  async function getJSON(path, fallback) {
    try {
      const r = await fetch(path + '?t=' + Date.now(), { cache: 'no-store' });
      if (!r.ok) throw new Error(String(r.status));
      return await r.json();
    } catch (e) { console.warn('Fetch:', path, e); return fallback; }
  }

  function getStoryId() {
    const p = new URLSearchParams(window.location.search);
    return p.get('id') || p.get('story') || '';
  }

  function findStory(data, id) {
    if (!data) return null;
    const stories = data.stories || [];
    if (data.lead && data.lead.story_id === id) return data.lead;
    return stories.find(s => s.story_id === id) || null;
  }

  function formatDate(ts) {
    if (!ts) return '';
    try {
      const d = new Date(ts);
      return d.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' }).toUpperCase();
    } catch { return ts; }
  }

  function tensionBadge(score) {
    const s = score || 0;
    if (s >= 67) return { cls: 'contradicted', label: window.i18n ? i18n.t('tension_max','MAX TENSION') : 'MAX TENSION' };
    if (s >= 34) return { cls: 'divergent', label: window.i18n ? i18n.t('tension_high','HIGH TENSION') : 'HIGH TENSION' };
    return { cls: 'aligned', label: window.i18n ? i18n.t('tension_building','BUILDING') : 'BUILDING' };
  }

  function buildHTML(story, allStories, currentIdx) {
    const t = window.i18n ? (k, fb) => i18n.t(k, fb) : (k, fb) => fb;
    const cf = story.capital_flow || {};
    const tension = tensionBadge(story.contradiction_score || 0);
    const category = t('sector_' + (story.sector || 'markets').toLowerCase(), (story.sector || 'MARKETS').toUpperCase());
    const severity = (story.severity || 'HIGH').toUpperCase();
    const date = formatDate(story.timestamp || story.date);

    const photo = story.photo || (cf.asset_class ? `./media/${cf.asset_class}.jpg` : '');
    const headline = story.headline || story.title || '';
    const summary = story.body || story.description || story.thesis || '';
    const theySay = story.they_say || '';
    const reality = story.reality || '';
    const claim = cf.claim || '';
    const projected = cf.projected || '';
    const positioning = cf.positioning || '';
    const amountB = cf.amount_b || 0;
    const direction = cf.direction || '';
    const confidence = cf.confidence_pct || story.confidence || 0;
    const confLabel = confidence >= 80 ? 'HIGH' : confidence >= 60 ? 'MEDIUM' : 'LOW';
    const extremum = story.extremum || '';
    const play = story.portfolio_implication || story.the_play || '';
    const catalysts = story.catalysts || [];

    const dirArrow = direction === 'inflow' ? '↑' : direction === 'outflow' ? '↓' : '';
    const dirWord = direction === 'inflow' ? 'into' : 'out of';
    const assetClass = cf.asset_class || 'equities';

    const totalStories = allStories.length;
    const hasNext = currentIdx < totalStories - 1;
    const nextStory = hasNext ? allStories[currentIdx + 1] : null;

    return `
    <article class="intel-report">
      <header class="intel-header">
        <div class="intel-meta">
          <span class="intel-category">${category}</span>
          <span class="intel-severity severity-${severity.toLowerCase()}">${t('severity_' + severity.toLowerCase(), severity)}</span>
          <time class="intel-date">${date}</time>
          <span class="tier-badge ${tension.cls}">${tension.label} <span class="tier-score">${story.contradiction_score || 0}/100</span></span>
        </div>
        <h1 class="intel-headline">${headline}</h1>
        ${photo ? `<div class="intel-photo"><img src="${photo}" alt="" loading="lazy" onerror="this.style.display='none'"/></div>` : ''}
      </header>

      <section class="intel-brief">
        <h2 class="intel-section-label">${t('intel_brief', 'INTEL BRIEF')}</h2>
        <div class="intel-summary">${summary}</div>
      </section>

      <section class="intel-play">
        <h2 class="intel-section-label play-label">${t('the_play_label', 'THE PLAY')}</h2>
        <div class="intel-play-content">${play}</div>
        ${catalysts.length ? `<div class="intel-catalysts"><span class="catalyst-tag">${t('catalysts', 'Catalysts')}:</span> ${catalysts.join(' · ')}</div>` : ''}
      </section>

      <div class="intel-contradiction">
        <section class="intel-they-say">
          <h2 class="intel-section-label they-say-label">${t('they_say', 'THEY SAY')}</h2>
          <div class="intel-they-say-content">${theySay}</div>
        </section>
        <section class="intel-reality">
          <h2 class="intel-section-label reality-label">${t('reality', 'REALITY')}</h2>
          <div class="intel-reality-content">${reality}</div>
        </section>
      </div>

      <section class="intel-capital-flow">
        <h2 class="intel-section-label cf-label">${t('capital_flow_label', 'CAPITAL FLOW')}</h2>
        <div class="intel-cf-data">
          <div class="intel-cf-amount">$${amountB}B ${dirArrow} ${assetClass}</div>
          <div class="intel-cf-meta">
            <span class="intel-cf-confidence">${confidence}% ${t('flow_confidence_pct', 'confidence')} · ${confLabel}</span>
            <span class="intel-cf-direction">${t('flow_' + direction, direction)}</span>
          </div>
          ${claim ? `<div class="intel-cf-claim">${claim}</div>` : ''}
          ${projected ? `<div class="intel-cf-projected"><span class="intel-cf-projected-label">${t('flow_projected', 'Projected')}:</span> ${projected}</div>` : ''}
          ${positioning ? `<div class="intel-cf-positioning">${positioning}</div>` : ''}
        </div>
      </section>

      <section class="intel-extremum">
        <h2 class="intel-section-label extremum-label">${t('extremum', 'EXTREMUM')}</h2>
        <div class="intel-extremum-content">${typeof extremum === 'object' ? (extremum.type + ': ' + (extremum.description || '').slice(0, 200)) : extremum}</div>
      </section>

      <div class="intel-share">
        <button onclick="copyStoryLink()" class="share-btn" title="${t('share_copy', 'Copy link')}"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg></button>
        <button onclick="shareTo('x')" class="share-btn" title="${t('share_x', 'Share on X')}"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 4l11.733 16h4.267l-11.733 -16z"/><path d="M4 20l6.768 -6.768m2.46 -2.46L20 4"/></svg></button>
        <button onclick="shareTo('facebook')" class="share-btn" title="${t('share_facebook', 'Share on Facebook')}"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg></button>
        <button onclick="shareTo('telegram')" class="share-btn" title="${t('share_telegram', 'Share on Telegram')}"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg></button>
      </div>
    </article>`;
  }

  function buildNav(storyId, allStories, currentIdx) {
    const nav = document.getElementById('storyNav');
    const pos = document.getElementById('storyPosition');
    const next = document.getElementById('storyNext');
    
    pos.textContent = `Story ${currentIdx + 1} of ${allStories.length}`;
    
    if (currentIdx < allStories.length - 1) {
      const ns = allStories[currentIdx + 1];
      next.href = '?id=' + ns.story_id;
      next.style.display = '';
    } else {
      next.style.display = 'none';
    }
    
    nav.style.display = '';
    document.title = (allStories[currentIdx].headline || 'Story') + ' — La Gazzetta di Kyiv';
  }

  async function init() {
    // Wait for i18n
    if (window.i18n && !window.i18n._ready) {
      await new Promise(r => { window.addEventListener('i18nReady', r, { once: true }); });
    }

    const storyId = getStoryId();
    if (!storyId) {
      document.getElementById('storyContent').innerHTML = '<p class="story-error">No story specified. <a href="./">Return to Dashboard</a></p>';
      return;
    }

    // Load stories
    const lang = window.i18n ? i18n.lang : 'en';
    const dataPath = lang === 'ru' ? STORIES_RU_PATH : STORIES_PATH;
    const data = await getJSON(dataPath, null);
    
    if (!data) {
      document.getElementById('storyContent').innerHTML = '<p class="story-error">Failed to load stories. <a href="./">Return to Dashboard</a></p>';
      return;
    }

    const stories = data.stories || [];
    const allStories = data.lead ? [data.lead, ...stories] : stories;
    const story = findStory(data, storyId);

    if (!story) {
      document.getElementById('storyContent').innerHTML = `<p class="story-error">Story not found. <a href="./">Return to Dashboard</a></p>`;
      return;
    }

    const idx = allStories.findIndex(s => s.story_id === storyId);
    
    document.getElementById('storyContent').innerHTML = buildHTML(story, allStories, idx);
    buildNav(storyId, allStories, idx);
  }

  // Share functions
  window.copyStoryLink = function() {
    navigator.clipboard.writeText(window.location.href).catch(() => {});
  };
  window.shareTo = function(platform) {
    const url = encodeURIComponent(window.location.href);
    const title = encodeURIComponent(document.title);
    const maps = {
      x: `https://x.com/intent/tweet?url=${url}&text=${title}`,
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${url}`,
      telegram: `https://t.me/share/url?url=${url}&text=${title}`,
    };
    if (maps[platform]) window.open(maps[platform], '_blank');
  };

  // Start
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
