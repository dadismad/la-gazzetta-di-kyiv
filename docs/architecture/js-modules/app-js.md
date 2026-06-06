# JS Module: app.js (1713 lines)

> Core application logic for data fetching, rendering, and state management.

## Module Sections

### Data Layer (lines 1-80)
- DATA_BASE, LIVING_DATA, FLOWS_BASE constants
- getDataPath(), getFlowsPath() with i18n support
- getJSON() with cache-busting and fallback
- FLOWS_POLL_INTERVAL (300000ms = 5min)

### Cache Layer (lines 81-120)
- STORIES_CACHE: story_id -> {headline, dom_card}
- capturedStoryIds: Set for accumulated rendering

### Rendering (lines 121-1713)
- Story card creation and management
- Flow visualization bars
- Signal dashboard with tension meter
- Trade idea cards with bet/benefit
- Hero section with dynamic numbers
- Sector photo integration
- Share buttons (X, Telegram, Reddit, Facebook)
- Polling/realtime update interval
- Navigation state management
- i18n text replacement

## Key Patterns

### Data Flow
1. Page loads HTML template
2. app.js initializes: detects language -> fetches data -> renders
3. Polls every 5 minutes for updated data
4. Smart merge: preserves existing DOM, appends new

### Cross-Linking
- story_id links between stories.json and flows.json
- Flow cards link to parent story detail
- Story cards show linked flows

## Dependencies
- i18n.js (must load before app.js)
- DOM elements from HTML templates
- stories.json and flows.json data files
