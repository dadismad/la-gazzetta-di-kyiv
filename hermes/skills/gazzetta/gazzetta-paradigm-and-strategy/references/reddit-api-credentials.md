# Reddit API Credential Setup

Setting up Reddit OAuth credentials for the Gazzetta di Kyiv pipeline
(`scripts/reddit_ingest.py` and related posting tools).

## Required Environment Variables

```
REDDIT_CLIENT_ID=<string-under-app-name-on-reddit-prefs>
REDDIT_CLIENT_SECRET=<secret-from-reddit-app>
REDDIT_USERNAME=<your-reddit-username>
REDDIT_PASSWORD=<your-reddit-password>
REDDIT_USER_AGENT=<descriptive-bot-string>  e.g. "gazzetta-kyiv-bot/1.0 by u/yourname"
```

## Google-Registered Accounts

If your Reddit account was originally created via Google OAuth:

1. **Do NOT disconnect Google** — you'd lose access and can't recover a password.
2. Go to **Reddit → User Settings → Password** (https://www.reddit.com/settings/) and set a Reddit password. Reddit allows this even for Google-linked accounts.
3. Now `REDDIT_PASSWORD` works with the password-grant OAuth flow.

## Creating a Script App

1. Go to https://www.reddit.com/prefs/apps
2. Scroll to "Developed Applications" → click "create app" (or "create another app")
3. Choose **script** type
4. Set a name (e.g. "gazzetta-kyiv-bot")
5. Set a redirect URI — for script apps this is ignored; `http://localhost:8000` works
6. After creation:
   - **REDDIT_CLIENT_ID** = the string displayed under your app name (not the app name itself)
   - **REDDIT_CLIENT_SECRET** = the "secret" field

## OAuth Flow Used

The scripts use Reddit's **password grant** OAuth flow (script app type):

```
POST https://www.reddit.com/api/v1/access_token
  Authorization: Basic {base64(client_id:client_secret)}
  Content-Type: application/x-www-form-urlencoded
  Body: grant_type=password&username=<user>&password=<pass>
→ Returns access_token valid for 1 hour
→ Subsequent API calls to https://oauth.reddit.com use bearer token
```

## Credential File Location

Add to `~/.hermes/.env` or a project-local `.env.reddit` file sourced before running the pipeline.

## Related Scripts

- `scripts/reddit_ingest.py` — fetches posts from a subreddit (read-only, uses OAuth)
- `scripts/devvit_only_pipeline.py` — full pipeline that generates publish-ready payloads
- `scripts/reddit_post_payload.py` — generates the `data/reddit_post_payload.md` file

The actual posting to Reddit is done via **Devvit** (Reddit's custom app platform)
from the subreddit's moderation tools, reading the `READY_FOR_DEVVIT_POST` payload.
