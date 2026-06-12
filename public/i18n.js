// i18n.js — Internationalization for Gazzetta di Kyiv (English-only)
// Retained for data-i18n attribute support and dynamic UI label resolution.

(function() {
  'use strict';

  const currentLang = 'en';
  let translations = {};

  // Public API — always English, no language switching
  window.i18n = {
    get lang() { return currentLang; },
    t: function(key, fallback) { return translations[key] || fallback || key; },
    init: function() {
      window.i18n._ready = true;
      window.dispatchEvent(new Event('i18nReady'));
    }
  };
})();

// Auto-initialize
i18n.init();
