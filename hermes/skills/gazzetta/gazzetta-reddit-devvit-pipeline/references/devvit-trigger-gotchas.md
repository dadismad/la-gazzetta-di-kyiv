# Devvit Web Trigger Gotchas

## onAppInstall vs onAppUpgrade

**The trap:** `onAppInstall` fires **only once** — when the app is first installed on a subreddit. Every subsequent `devvit install` is an **upgrade**, which fires `onAppUpgrade` (if declared) or nothing (if not declared).

**Fix:** Always declare BOTH in `devvit.json`:
```json
"triggers": {
  "onAppInstall": "/internal/triggers/on-app-install",
  "onAppUpgrade": "/internal/triggers/on-app-install"
}
```

Both can point to the same endpoint. The runtime handles dedup if both fire for the same event (unlikely but possible).

**How to know which trigger fired:** The request body carries the trigger type via `OnAppInstallRequest` or `OnAppUpgradeRequest` from `@devvit/web/shared`. But for simplicity, you can ignore the body entirely and just `try { await c.req.json() } catch {}` — the side effect (the post) is what matters.

## Trigger Request Parsing

The body is a JSON with shape like `{ installer: "...", type: "install" }` or `{ installer: "...", type: "upgrade" }`. If you don't use the payload, don't import the type — just `try { await c.req.json() } catch {}` to avoid crashes from unexpected payload shapes.

## Trigger Reliability

From Devvit docs: "Triggers are not guaranteed to deliver only once for a single event. Ensure your app logic is able to handle this case."

The `devvit install` command may return success before the trigger finishes executing. The trigger runs asynchronously on Reddit's infrastructure. There's no synchronous confirmation that the post was created.

## Error Observability

Trigger errors are logged to Devvit's internal logging. To view:
```
cd /Users/alexstocchi/lagazzettadikyiv
./node_modules/.bin/devvit logs LaGazzettadiKyiv --since 10m
```
This command may hang or timeout in limited environments. Short of that, the only signal is the `devvit install` exit code (which reports install success, not trigger success).

## Scheduler

The scheduler in `devvit.json` is more reliable than triggers for recurring posts because:
- It runs on Reddit's infrastructure with no external dependency
- Cron expressions are standard (`0 */4 * * *`)
- Each tick is independent — no statefulness required
- The endpoint receives no body (it's just a POST to the configured menu endpoint)

## Debugging Protocol

1. Check `devvit.json` for BOTH trigger declarations
2. Hardcode content in the trigger handler (eliminate import chain as a variable)
3. Deploy and ask user to check the subreddit
4. If still no post, add `console.log` statements and try to read logs via `devvit logs`
5. Test the same endpoint via a menu item (which bypasses trigger system entirely)
6. If menu items also fail, the issue is in `reddit.submitPost()` call, not the trigger
