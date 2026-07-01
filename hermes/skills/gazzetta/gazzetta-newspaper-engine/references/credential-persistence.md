# Credential Persistence — Critical Pitfall

## The Rule

**When the user provides a credential (API key, token, secret, password), persist it to the appropriate .env file IMMEDIATELY in the same turn. Do not wait to be asked. Do not store it in memory alone.**

Memory is injected into every turn and may be visible in logs. `.env` files are not. The `.env` file is the single source of truth for credentials. Memory captures "where the credentials live" — not the credentials themselves.

## What Went Wrong (June 22, 2026)

The user provided API keys in the Telegram conversation. The agent processed them but never wrote them to the VM `.env` file. When the context window cleared (new session), the keys were lost. The user was forced to provide them again. This is a failure of credential hygiene.

## Correct Pattern

```python
# When user says "here is the FRED API key: abc123"
# IMMEDIATELY:
ssh gazzetta-prod "echo 'FRED_API_KEY=abc123' | sudo tee -a /opt/gazzetta-di-kyiv/.env"
# THEN verify:
ssh gazzetta-prod "sudo cat /opt/gazzetta-di-kyiv/.env | grep FRED_API_KEY"
# THEN confirm to user:
# "FRED_API_KEY saved to VM .env. Pipeline will pick it up next cycle."
```

## Credential Locations

| Credential | Where It Lives | How It's Loaded |
|------------|---------------|-----------------|
| DEEPSEEK_API_KEY | `/opt/gazzetta-di-kyiv/.env` (VM) + GCP Secret Manager | governor.py _secret() → env |
| TELEGRAM_BOT_TOKEN | GCP Secret Manager | governor.py _secret() → env |
| ALPHAVANTAGE_API_KEY | GCP Secret Manager | governor.py _secret() → env |
| CFTC_API_KEY | NOT NEEDED — CFTC SODA is public | N/A |
| FRED_API_KEY | `/opt/gazzetta-di-kyiv/.env` (VM) | os.environ.get() in fetch_fred.py |
| GCP Service Account | `397576418262-compute@developer.gserviceaccount.com` (VM metadata) | Automatic |

## Verification Command

After adding any credential, run the pipeline test:

```bash
ssh gazzetta-prod "sudo -u gazzetta /opt/gazzetta-di-kyiv/venv/bin/python -c \"
import os; 
key = os.environ.get('FRED_API_KEY', '');
print('FRED_KEY: SET' if key else 'FRED_KEY: MISSING')
\""
```

## Never

- Never store credentials in memory (they appear in every context injection)
- Never store credentials in chat-only context (they vanish when the window clears)
- Never assume the user will remember to provide a key twice
- Never skip the verification step after writing
