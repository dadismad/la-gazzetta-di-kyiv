# Vision / Screenshot Review — Setup & Constraints

## Current state (June 2026)

| Path | Status | Detail |
|------|--------|--------|
| Groq vision | ❌ 403 | API returns 403 for vision models |
| OpenAI vision | ❌ Quota | Quota exhausted, no billing |
| DeepSeek vision | ❌ None | DeepSeek has no vision capability |
| Anthropic (Claude) | ❌ No key | Anthropic API key not configured |
| **Gemini API (free)** | ⚠️ Not configured | Best path — free, 1,500 req/day |
| GitHub Copilot CLI | ❌ Incompatible | Requires macOS 13.5+ (user on 11.7.4) AND Node 24+ (user on 22) |
| Google Vertex AI | ❌ Project-limited | GCP project `project-e5e0244c-b94d-41a1-810` is GCS-only — all Vertex AI model paths return 404 |

## Recommended setup: Gemini API key

1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Sign in with `pureciclismo@gmail.com` (same account as gcloud)
3. Click "Create API Key"
4. Add to `~/.hermes/.env`:
   ```
   GEMINI_API_KEY=your-key-here
   ```
5. 1,500 requests/day free — more than enough for screenshot reviews

## Why Vertex AI (gcloud) doesn't work

The project configured in gcloud (`project-e5e0244c-b94d-41a1-810`) is a Firebase/GCS project — it doesn't have Vertex AI enabled. The `gcloud ai` command group exists but only manages models/endpoints, not inference. All model paths (`gemini-2.0-flash-001`, `gemini-1.5-flash-001`, etc.) return HTTP 404. Upgrading to a full GCP project with Vertex AI would require billing setup, quota requests, and project migration — the free API key is the faster path.

## Fallback: Browser-based manual review

If no vision API is available, use `browser_navigate` to open the site, `browser_snapshot` for text content, and `browser_console` to inspect rendered state. This provides structural information but not visual design review (typography, color, layout feel). Focus group subagents use browser tools for textual/structural audits but cannot evaluate visual design without vision.
