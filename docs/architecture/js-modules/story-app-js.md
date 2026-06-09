# JS Module: story-app.js (218 lines)

> Story detail page rendering for /story.html.

## Responsibilities

- Load single story from stories.json by story_id (URL param)
- Render contradiction display (they_say vs reality)
- Render capital flow box with direction/confidence/amount
- Render trade idea card with entry/exit levels
- Provide share buttons (X, Telegram, Reddit, Facebook)
- Show timeline/updates section
- Navigation: back to dashboard, next story

## Data Flow

1. Read story_id from URL query string
2. Fetch stories.json
3. Find story by story_id
4. Render all sections
5. Pre-fetch adjacent stories for navigation
