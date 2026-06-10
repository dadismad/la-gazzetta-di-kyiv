// story-app.js — Immersive single-story intel report page
// v2.0: Modular rewrite — eliminated scope fragility, proper async init
// Loads story by ?id= param, renders full intel report layout
// Supports sector filtering via ?sector=markets|geopolitics|wealth|pleasure

(function() {
  'use strict';

  const STORIES_PATH = './data/stories.json';
  const STORIES_RU_PATH = './data/stories_ru.json';

  async function getJSON(path, fallback) {
    try {
      const r = await fetch(path + '?t=' + Date.now(), { cache: 'no-store' });
      if (!r.ok) throw new Error(String(r.status));
      return await r.json();
    } catch (e) { console.warn('story-app fetch:', path, e); return fallback; }
  }

  function getStoryId() {
    const p = new URLSearchParams(window.location.search);
    return p.get('id') || p.get('story') || '';
  }

  function getSectorFilter() {
    const p = new URLSearchParams(window.location.search);
    return p.get('sector') || '';
  }

  function findStory(data, id) {
    if (!data) return null;
    const stories = data.stories || [];
    if (data.lead && data.lead.story_id === id) return data.lead;
    return stories.find(function(s) { return s.story_id === id; }) || null;
  }

  function formatDate(ts) {
    if (!ts) return '';
    try {
      var d = new Date(ts);
      return d.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' }).toUpperCase();
    } catch (e) { return ts; }
  }

  function tensionBadge(score) {
    var s = score || 0;
    if (s >= 67) return { cls: 'contradicted', label: window.i18n ? i18n.t('tension_max','MAX TENSION') : 'MAX TENSION' };
    if (s >= 34) return { cls: 'divergent', label: window.i18n ? i18n.t('tension_high','HIGH TENSION') : 'HIGH TENSION' };
    return { cls: 'aligned', label: window.i18n ? i18n.t('tension_building','BUILDING') : 'BUILDING' };
  }

  function buildHTML(story, allStories, currentIdx) {
    var t = window.i18n ? function(k, fb) { return i18n.t(k, fb); } : function(k, fb) { return fb; };
    var cf = story.capital_flow || {};
    var tension = tensionBadge(story.contradiction_score || 0);
    var category = t('sector_' + (story.sector || 'markets').toLowerCase(), (story.sector || 'MARKETS').toUpperCase());
    var severity = (story.severity || 'HIGH').toUpperCase();
    var date = formatDate(story.timestamp || story.date || story.generated_at);
    var photo = story.photo || (cf.asset_class ? './media/' + cf.asset_class + '.jpg' : '');
    var headline = story.headline || story.title || '';
    var summary = story.body || story.description || story.thesis || '';
    var theySay = story.they_say || '';
    var reality = story.reality || '';
    var claim = cf.claim || '';
    var projected = cf.projected || '';
    var positioning = cf.positioning || '';
    var amountB = cf.amount_b || 0;
    var direction = cf.direction || '';
    var confidence = cf.confidence_pct || story.confidence || 0;
    var confLabel = confidence >= 80 ? 'HIGH' : confidence >= 60 ? 'MEDIUM' : 'LOW';
    var extremum = story.extremum || '';
    var play = story.portfolio_implication || story.the_play || '';
    var catalysts = story.catalysts || [];
    var dirArrow = direction === 'inflow' ? '↑' : direction === 'outflow' ? '↓' : '';
    var dirWord = direction === 'inflow' ? 'into' : 'out of';
    var assetClass = cf.asset_class || 'equities';
    var totalStories = allStories.length;
    var hasNext = currentIdx < totalStories - 1;
    var nextStory = hasNext ? allStories[currentIdx + 1] : null;

    return [
      '<article class="intel-report">',
      '<header class="intel-header">',
      '<div class="intel-meta">',
      '<span class="intel-category">' + category + '</span>',
      '<span class="intel-severity severity-' + severity.toLowerCase() + '">' + t('severity_' + severity.toLowerCase(), severity) + '</span>',
      '<time class="intel-date">' + date + '</time>',
      '<span class="tier-badge ' + tension.cls + '">' + tension.label + ' <span class="tier-score">' + (story.contradiction_score || 0) + '/100</span></span>',
      '</div>',
      '<h1 class="intel-headline">' + headline + '</h1>',
      photo ? '<div class="intel-photo"><img src="' + photo + '" alt="" loading="lazy" onerror="this.style.display=\'none\'"/></div>' : '',
      '</header>',
      '<section class="intel-brief">',
      '<h2 class="intel-section-label">' + t('intel_brief', 'INTEL BRIEF') + '</h2>',
      '<div class="intel-summary">' + summary + '</div>',
      '</section>',
      '<section class="intel-play">',
      '<h2 class="intel-section-label play-label">' + t('the_play_label', 'THE PLAY') + '</h2>',
      '<div class="intel-play-content">' + play + '</div>',
      catalysts.length ? '<div class="intel-catalysts"><span class="catalyst-tag">' + t('catalysts', 'Catalysts') + ':</span> ' + catalysts.join(' · ') + '</div>' : '',
      '</section>',
      '<div class="intel-contradiction">',
      '<section class="intel-they-say">',
      '<h2 class="intel-section-label they-say-label">' + t('they_say', 'THEY SAY') + '</h2>',
      '<div class="intel-they-say-content">' + theySay + '</div>',
      '</section>',
      '<section class="intel-reality">',
      '<h2 class="intel-section-label reality-label">' + t('reality', 'REALITY') + '</h2>',
      '<div class="intel-reality-content">' + reality + '</div>',
      '</section>',
      '</div>',
      '<section class="intel-capital-flow">',
      '<h2 class="intel-section-label cf-label">' + t('capital_flow_label', 'CAPITAL FLOW') + '</h2>',
      '<div class="intel-cf-data">',
      '<div class="intel-cf-amount">$' + amountB + 'B ' + dirArrow + ' ' + assetClass + '</div>',
      '<div class="intel-cf-meta">',
      '<span class="intel-cf-confidence">' + confidence + '% ' + t('flow_confidence_pct', 'confidence') + ' · ' + confLabel + '</span>',
      '<span class="intel-cf-direction">' + t('flow_' + direction, direction) + '</span>',
      '</div>',
      claim ? '<div class="intel-cf-claim">' + claim + '</div>' : '',
      projected ? '<div class="intel-cf-projected"><span class="intel-cf-projected-label">' + t('flow_projected', 'Projected') + ':</span> ' + projected + '</div>' : '',
      positioning ? '<div class="intel-cf-positioning">' + positioning + '</div>' : '',
      '</div>',
      '</section>',
      '<section class="intel-extremum">',
      '<h2 class="intel-section-label extremum-label">' + t('extremum', 'EXTREMUM') + '</h2>',
      '<div class="intel-extremum-content">' + (typeof extremum === 'object' ? (extremum.type + ': ' + (extremum.description || '').slice(0, 200)) : extremum) + '</div>',
      '</section>',
      '<div class="intel-share">',
      '<button onclick="copyStoryLink()" class="share-btn" title="' + t('share_copy', 'Copy link') + '"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg></button>',
      '<button onclick="shareTo(\'x\')" class="share-btn" title="' + t('share_x', 'Share on X') + '"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 4l11.733 16h4.267l-11.733 -16z"/><path d="M4 20l6.768 -6.768m2.46 -2.46L20 4"/></svg></button>',
      '<button onclick="shareTo(\'facebook\')" class="share-btn" title="' + t('share_facebook', 'Share on Facebook') + '"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg></button>',
      '<button onclick="shareTo(\'telegram\')" class="share-btn" title="' + t('share_telegram', 'Share on Telegram') + '"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg></button>',
      '</div>',
      '</article>'
    ].join('\n');
  }

  function buildNav(storyId, allStories, currentIdx) {
    var nav = document.getElementById('storyNav');
    var pos = document.getElementById('storyPosition');
    var next = document.getElementById('storyNext');
    if (!nav || !pos || !next) return;
    pos.textContent = 'Story ' + (currentIdx + 1) + ' of ' + allStories.length;
    if (currentIdx < allStories.length - 1) {
      var ns = allStories[currentIdx + 1];
      next.href = '?id=' + ns.story_id;
      next.style.display = '';
    } else {
      next.style.display = 'none';
    }
    nav.style.display = '';
    document.title = (allStories[currentIdx].headline || 'Story') + ' — La Gazzetta di Kyiv';
  }

  // ═══════════════ v23.8: Gazzetta Namespace ═══════════════
  window.Gazzetta = window.Gazzetta || {};
  Gazzetta.Story = {};

  async function init() {
    // Wait for i18n
    if (window.i18n && !window.i18n._ready) {
      await new Promise(function(r) { window.addEventListener('i18nReady', r, { once: true }); });
    }

    var storyId = getStoryId();
    var sectorFilter = getSectorFilter();
    var contentEl = document.getElementById('storyContent');
    
    if (!storyId && !sectorFilter) {
      if (contentEl) contentEl.innerHTML = '<p class="story-error">No story specified. <a href="./">Return to Dashboard</a></p>';
      return;
    }

    // Load stories
    var lang = window.i18n ? i18n.lang : 'en';
    var dataPath = lang === 'ru' ? STORIES_RU_PATH : STORIES_PATH;
    var data = await getJSON(dataPath, null);
    
    if (!data) {
      if (contentEl) contentEl.innerHTML = '<p class="story-error">Failed to load stories. <a href="./">Return to Dashboard</a></p>';
      return;
    }

    var stories = data.stories || [];
    var allStories = data.lead ? [data.lead].concat(stories) : stories;

    // Sector filter mode: render filtered story list
    if (sectorFilter && !storyId) {
      renderSectorList(sectorFilter, allStories);
      return;
    }

    // Single story mode
    var story = findStory(data, storyId);
    if (!story) {
      if (contentEl) contentEl.innerHTML = '<p class="story-error">Story not found. <a href="./">Return to Dashboard</a></p>';
      return;
    }

    var idx = allStories.findIndex(function(s) { return s.story_id === storyId; });
    if (contentEl) contentEl.innerHTML = buildHTML(story, allStories, idx);
    buildNav(storyId, allStories, idx);
  }

  // Sector filter: render filtered story list (replaces sector pages)
  function renderSectorList(sector, allStories) {
    var contentEl = document.getElementById('storyContent');
    if (!contentEl) return;
    
    var sectorNames = { markets: 'Markets', geopolitics: 'Geopolitics', wealth: 'Wealth', pleasure: 'Pleasure' };
    var sectorName = sectorNames[sector] || sector;
    
    // Filter stories by sector
    var filtered = allStories.filter(function(s) {
      return (s.sector || '').toLowerCase() === sector.toLowerCase();
    });
    
    if (!filtered.length) {
      contentEl.innerHTML = '<div class="sector-hero"><h2>' + sectorName + '</h2><p>No stories in this sector yet.</p></div>' +
        '<div class="sector-nav"><a href="./stories.html">← All Stories</a> | ' +
        '<a href="?sector=markets">Markets</a> | <a href="?sector=geopolitics">Geopolitics</a> | ' +
        '<a href="?sector=wealth">Wealth</a> | <a href="?sector=pleasure">Pleasure</a></div>';
      return;
    }
    
    var items = filtered.map(function(s) {
      var cf = s.capital_flow || {};
      var date = formatDate(s.timestamp || s.date || s.generated_at);
      return '<article class="story-card">' +
        '<div class="card-meta"><span class="severity severity-' + (s.severity || 'high').toLowerCase() + '">' + (s.severity || 'HIGH') + '</span>' +
        '<time>' + date + '</time></div>' +
        '<h2><a href="./story.html?id=' + s.story_id + '">' + (s.headline || s.title || '') + '</a></h2>' +
        '<p>' + ((s.body || s.description || '').slice(0, 200)) + '...</p>' +
        (cf.amount_b ? '<div class="cf-hint">$' + cf.amount_b + 'B ' + (cf.direction || '') + '</div>' : '') +
        '</article>';
    });
    
    contentEl.innerHTML = '<div class="sector-hero"><h2>' + sectorName + '</h2><p>' + filtered.length + ' stories</p></div>' +
      '<div class="sector-nav"><a href="./stories.html">← All Stories</a> | ' +
      '<a href="?sector=markets">Markets</a> | <a href="?sector=geopolitics">Geopolitics</a> | ' +
      '<a href="?sector=wealth">Wealth</a> | <a href="?sector=pleasure">Pleasure</a></div>' +
      '<div class="articles-list">' + items.join('') + '</div>';
    
    document.title = sectorName + ' — La Gazzetta di Kyiv';
  }

  Gazzetta.Story.init = init;
  Gazzetta.Story.renderSectorList = renderSectorList;

  // Share functions
  window.copyStoryLink = function() {
    navigator.clipboard.writeText(window.location.href).catch(function() {});
  };
  window.shareTo = function(platform) {
    var url = encodeURIComponent(window.location.href);
    var title = encodeURIComponent(document.title);
    var maps = {
      x: 'https://x.com/intent/tweet?url=' + url + '&text=' + title,
      facebook: 'https://www.facebook.com/sharer/sharer.php?u=' + url,
      telegram: 'https://t.me/share/url?url=' + url + '&text=' + title,
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
