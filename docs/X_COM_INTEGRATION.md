# X.com (Twitter) Integration Guide

## Status: Connected ✅ — Blocked on Credits

The `@GazzettadiKyiv` account is fully authenticated via OAuth 2.0 PKCE with the official `xurl` CLI. The account can read/search — posting is blocked by zero credits.

## Account Details
- Handle: `@GazzettadiKyiv`
- ID: `2059326509177765888`
- Email: solianins@gmail.com
- Password: Lagazzettadikyiv2026
- Created: 2026-05-26

## What's Set Up
- ✅ xurl CLI installed at `~/.local/bin/xurl`
- ✅ App registered: `GazzettadiKyivX` (Client ID: Wnk1bm9m…)
- ✅ OAuth 2.0 PKCE tokens active, auto-refresh
- ✅ Default app set to `GazzettadiKyivX`
- ✅ Read/search works: `xurl whoami`, `xurl search "..."`
- ❌ Posting blocked: "CreditsDepleted"

## Unblock: Buy Credits
1. Go to https://developer.x.com/en/portal/dashboard
2. Navigate to Billing
3. Purchase credits — minimum **$5**
4. X offers up to 20% back in xAI API credits for X API credit purchases

## Posting Syntax (once credits are loaded)
```bash
xurl post "Your tweet text here"
xurl post "Check this out" --media-id <MEDIA_ID>
xurl reply <POST_ID> "Reply text"
xurl quote <POST_ID> "Quote text"
```

See `xurl` skill for full command reference.

## Note on "Free" Access
The old X API free tier (1,500 tweets/month) no longer exists. Current X API is entirely pay-per-use. The minimum spend is $5 one-time — credits don't expire.

## Credential Storage
- Project credentials: `gazzetta-di-kyiv/secure/credentials.json` (chmod 600)
- OAuth tokens: `~/.xurl` (YAML, never read into agent context)
