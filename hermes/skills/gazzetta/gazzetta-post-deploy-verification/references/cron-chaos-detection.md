# Cron Chaos — Overlapping Automation Detection

## When to Use

When the system exhibits inconsistent behavior that changes every few minutes or hours — cache headers flip, files appear and disappear, deploy sources keep switching. The user says "something keeps undoing my changes."

## The Pattern

Multiple automated jobs (cron, systemd timers, CI/CD, webhooks) touch the same resource. They conflict because they have different goals, different sources, or different configurations.

## Real Example: Gazzetta di Kyiv Deploy Chaos

**Three overlapping automation systems modifying the same GCS bucket:**

1. **Hermes cron `gazzetta-deploy`** — every 10 min, deploys local `public/` with `-d` flag. Sets `Cache-Control: max-age=0`.
2. **VM `gazzetta-shipit` timer** — every ~60 min, deploys VM `site/` with `-d` flag. Sets NO cache headers.
3. **VM `deploy_routine.sh`** (dormant) — designed for 10-min cron, sets `Cache-Control: immutable, max-age=31536000`.

Result: cache headers flipped between `no-cache` and `immutable`. One deploy source had v28 CSS, the other had only `data/`. Files deleted by one were re-uploaded by the other.

## The Fix: Purge All, Rebuild One

1. List ALL automated jobs:
   - Hermes: `cronjob list`
   - VM: `crontab -l`
   - VM: `systemctl list-timers --all | grep gazzetta`
2. Delete or disable ALL of them:
   - Hermes: `cronjob(action='remove', job_id='...')` for each
   - VM crontab: `echo '' | sudo crontab -`
   - VM timers: `sudo systemctl disable --now <timer>.timer`
3. Verify nothing is running: re-run all three list commands.
4. Intentionally rebuild only what's needed:
   - ONE deploy path
   - ONE health check
   - ONE quality gate
   - Each as a single timer or cron, with clear ownership and no overlapping resource access.

## Detection Heuristics

- Cache headers keep changing → multiple jobs setting metadata on the same objects
- Files appear and disappear from GCS → `rsync -d` from different sources
- Site works then breaks every 10-60 minutes → overlapping schedules
- Some deploys have HTML/CSS, others don't → deploy sources have different content
- Fix verified at T+0, broken at T+5 → a competing job ran between verification and now
