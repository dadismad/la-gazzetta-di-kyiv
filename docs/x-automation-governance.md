# X Automation Governance — Gazzetta di Kyiv

## Objective
Operate `@GazzettadiKyiv` as a high-signal macro channel with controlled automation, evidence links, and strict risk controls.

## Current capability state
- App registered in xurl: `GazzettadiKyivX`
- App-auth (bearer) configured for data collection routes.
- OAuth2 user-post auth: not completed yet.
- Blocking issue: X API account currently reports `CreditsDepleted` on read requests.

## Automation policy
1. **No blind autoposting**
   - Every post must include explicit claim + trigger/invalidation signal.
2. **Length guardrail**
   - Max 275 chars for single post automation.
3. **No duplicate spam**
   - Reject if near-duplicate of prior 3 posts.
4. **Evidence-first**
   - Include one source anchor or internal evidence URL in thread follow-up.
5. **Escalation**
   - If API returns auth/credits errors 3 times in a row, pause posting lane and alert.

## Procedures

### P1 — Collection health check
- Run: `python3 scripts/x_collect_account_data.py`
- Outcome states:
  - `ok` = collection healthy
  - `blocked_credits` = billing issue in X developer account
  - `blocked_auth_or_api` = auth or API access issue

### P2 — Post from generated text
- Prepare a file with final text (<=275 chars)
- Run: `python3 scripts/x_post_from_file.py data/x/outgoing_post.txt`
- Requires OAuth2 user auth in xurl.

### P3 — Incident response
- If `CreditsDepleted`: top up X developer credits, then re-run P1.
- If `Unauthorized`: re-run OAuth2 login for app and validate with `xurl whoami`.
- If repeated 429s: increase interval and reduce query fan-out.

## Security policy
- Never print raw keys/tokens in logs or Telegram messages.
- Secrets remain in local credential stores (`~/.xurl`, local env only).
- Rotate any secrets that were ever shared in chat.

## Operational checkpoints
- Daily 08:00 UTC: collection health
- Every 8h: content candidate generation
- Posting only when health state is `ok` and policy checks pass
