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

## Status (20 Aug 2026, session 3 — rename + ship)
- Renamed TaskGuardian → **UnDeleted** throughout: CLI command, package dir, Keychain service
  name, env var prefix (`UNDELETED_LICENSE_*`), all docs, workflows, landing page. Existing
  Keychain token migrated to the new service name, old entry deleted. `.venv` rebuilt (its
  scripts hardcoded the old absolute path after the project folder itself was renamed).
- **Security incident, resolved**: a `grep` during debugging accidentally printed a live
  `GITHUB_TOKEN` (classic PAT, plaintext in `~/.zshrc`) into the chat transcript. Turned out
  already dead (not listed under GitHub's own token pages, `gh auth status` confirmed invalid)
  — but treated as compromised regardless. Removed from `~/.zshrc`, replaced with `gh auth
  login` (browser device-code flow, keyring-backed, no dotfile secret). Also had to run `gh
  auth setup-git` and `gh auth refresh -s workflow` (missing OAuth scope blocked pushing
  `.github/workflows/*.yml`) before pushes actually worked.
- **Pushed to GitHub for real**: `github.com/liveskyhigh84/undeleted`, all 3 repo secrets
  verified present (`TODOIST_API_TOKEN`, `HEALTHCHECKS_URL`, `NTFY_TOPIC`) before the push —
  they were configured correctly even before the code existed remotely.
- **v1.0.0 tagged and pushed** — `.github/workflows/release.yml` triggered, building macOS/
  Linux/Windows binaries.
- **GitHub Pages live**: `/docs` folder on `master` (Pages only supports root or `/docs`, not
  arbitrary folders — mirrored `landing/index.html` → `docs/index.html` to work around that).
  Live at `liveskyhigh84.github.io/undeleted`.
- **Local monitoring wired and tested**: `HEALTHCHECKS_URL` retrieved from Leon's already-
  logged-in healthchecks.io account (`https://hc-ping.com/c4d07d88-...`, "My First Check"),
  `NTFY_TOPIC=undeleted-leon-8f3k2x9q` provided by Leon. Both added to `~/.zshrc`. Test ntfy
  push sent and confirmed delivered.

## Status (20 Aug 2026, session 4 — Lemon Squeezy live)
- Account created by Leon (website URL step used the new GitHub Pages URL; picked "Continue
  with Lemon Squeezy," not the newer Stripe-backed Managed Payments option, since the License
  API compatibility with Managed Payments wasn't confirmed and the existing `license.py`
  integration is built against the classic path).
- Store still shows "under review" (Lemon Squeezy manually approves new stores) — products
  and checkout links work in Test mode in the meantime, will go live on approval.
- **Two products published**, both with license keys enabled:
  - `UnDeleted` — $29 one-time, unlimited license length. Checkout:
    `https://undeleted.lemonsqueezy.com/checkout/buy/d360e60f-24b4-44c4-9019-bfeb8e0bc50d`
  - `UnDeleted — Annual` — $19/yr subscription, license tied to subscription status (no
    separate length field for subscriptions). Checkout:
    `https://undeleted.lemonsqueezy.com/checkout/buy/d7e88644-ec2c-4fab-a015-b5ad1618e640`
- Both checkout links wired into `landing/index.html` and `docs/index.html` (kept in sync),
  replacing the `href="#"` placeholders. Pushed.

## Next actions
1. Same live test for Asana once a token exists.
2. Wait for Lemon Squeezy store approval, then confirm a real Test-mode checkout completes
   end to end (license key issued, `license.py` validates it).
3. Flip `UNDELETED_LICENSE_REQUIRED=1` only on the distributed/packaged build, never the
   personal repo default, once ready to actually gate for paying customers.
4. Work the LAUNCH.md day 1/3/7 sequence once store approval lands.

Full step-by-step in the "UnDeleted: Ship Runbook" artifact — Phases 1, 2, 4, 5(partial: env
vars set, GitHub Pages done) are closed. Phase 3 (Lemon Squeezy) and 7 (launch) remain.
