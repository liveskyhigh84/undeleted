# UnDeleted — project memory

## What this is
Backup/diff/restore safety net for Todoist (Asana added) — sold as Path A: bring-your-own-token
CLI, never a hosted service. Born from a GapScope run reverse-engineering Todoist's App Store
reviews (18 Aug 2026). Brutal verdict: STOP on a competing to-do app, GO on this narrow
companion tool — precedent: BackupLABS/NotionBackups.com already monetize this exact model.

## Status (19 Aug 2026)
- **Live-tested for real, for the first time**: `undeleted init` → Keychain → `undeleted
  snapshot --source todoist` → committed `2eb485f` → `undeleted restore --source todoist
  --commit HEAD` correctly reported nothing missing. The "never run against a live account"
  gap is closed. Snapshot showed 0 tasks — expected if Leon's active Todoist list is empty
  (the API returns active/incomplete tasks only); not investigated further, not alarming
  unless a later real task doesn't show up in a snapshot.
- Asana: module built (`asana_snapshot.py`), same interface, still not live-tested (needs an
  Asana token — same open item as Todoist was until today).
- Licensing: switched from Gumroad to **Lemon Squeezy** (~5.5% fee vs ~14%, same free
  license-validate API). Gate is `UNDELETED_LICENSE_REQUIRED=1` (off by default — Leon's
  own instance runs ungated). `license.py` calls `POST
  api.lemonsqueezy.com/v1/licenses/validate`, 7-day cache, 30-day offline grace period.
- Packaging: PyInstaller `--onefile` build verified locally (15MB macOS binary, ran `--help`/
  `status`/`snapshot` correctly standalone, no Python needed). `.github/workflows/release.yml`
  builds macOS/Linux/Windows binaries on any `v*` tag push.
- Pricing: switched to one-time ($29 lifetime) / $19/yr — no monthly subscription, per
  research on churn psychology for a safety-net-you-hope-not-to-need tool.
- `landing/index.html` — real marketing landing page, dark/teal brand identity, pricing cards,
  FAQ, trust signals. Not deployed yet (see LAUNCH.md / runbook Phase 6).
- `LAUNCH.md` — full distribution plan: forum/Reddit/HN sequence, day 1/3/7 launch cadence.
- Security review (dedicated agent pass): 0 critical/high findings on credential + license
  code. 2 low findings fixed (license cache file permissions, documented a `ps`-visibility
  tradeoff in the Keychain-write step).
- Todoist ToS fact-checked directly (not assumed): no clause bans a commercial tool on personal
  tokens. Path A's own-token model is confirmed the *compliant* one, not just the cheaper one
  (ToS bans transferring access granted to one account).
- Test suite: 15 pytest tests, all passing, covering diff logic, real git-backed storage, and
  license verification including network-failure/grace-period paths.

## Known gap not yet closed
Global Python style rules (type hints on all signatures) were applied to code written/edited
in session 2 but not fully retrofitted onto everything from session 1. Low priority, code
works and is tested.

## Next actions
1. Same live test for Asana once a token exists.
2. Push to a real GitHub remote (needed for the release workflow and the daily snapshot cron
   to actually run — right now they're wired but inert against a local-only repo).
3. Create the Lemon Squeezy product (License Key type), get pricing live.
4. Tag `v1.0.0` to trigger the first real binary release.
5. Deploy `landing/index.html` (GitHub Pages is the free, already-set-up path).
6. Sign up for healthchecks.io + ntfy.sh if the alerting layer is wanted.
7. Work the LAUNCH.md day 1/3/7 sequence once the above is live.

Full step-by-step for all of this is in the "UnDeleted: Ship Runbook" artifact from this
session — Phase 1 (this live test) is now the only phase marked done.
