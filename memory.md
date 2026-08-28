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

## Status (26 Aug 2026, session 5 — Lemon Squeezy approved, full test pass, 2 critical bugs found+fixed)
- **Lemon Squeezy account approved** (23 Aug email from Lasya). Store live, both products
  ("UnDeleted" $29 lifetime, "UnDeleted — Annual" $19/yr) confirmed real via a live checkout
  page load — correct name/price/description, Test mode banner showing.
- **CRITICAL BUG #1 (found + fixed)**: the last commit of session 4 (`e4cac4d`, "stop tracking
  snapshots/ in the product repo") added `snapshots/` to `.gitignore`. `storage.commit_snapshot()`
  does a plain `git add`, which silently no-ops on an ignored path. Result: every snapshot since
  21 Aug wrote to disk but was **never committed** — `restore` broken ("exists on disk but not
  in HEAD"), staleness/deletion-alert diffing broken, and the README's own "recommended" GitHub
  Actions cron path broken (5 straight failed runs on the real repo). This was the product's
  entire core mechanism, dead, for 5 days, unnoticed only because Leon's live Todoist list is
  empty. Fixed: removed `snapshots/` from `.gitignore` (commit `572f903`). Verified with a real
  simulated-deletion test (write 3-task snapshot, commit, write 2-task snapshot, commit, restore
  dry-run against the prior commit — correctly listed the missing task).
- **CRITICAL BUG #2 (found + fixed)**: even after bug #1's fix, the `snapshot.yml` CI cron still
  failed — `git push` returned 403 ("Permission to .../undeleted.git denied to
  github-actions[bot]"). The job had no `permissions: contents: write` block (same class of gap
  `release.yml` already hit once in session 4). Fixed (commit `19e7501`), then verified with a
  real `workflow_dispatch` run — all steps green, snapshot actually committed and pushed by CI.
- **Asana live-tested for the first time** — closes the one gap flagged since session 2.
  `undeleted snapshot --source asana` and `restore --source asana --commit HEAD` both work
  against Leon's real 2-task Asana account.
- **ClickUp still not live-tested** — no `CLICKUP_API_TOKEN` / Keychain entry available this
  session. 5 unit tests pass (mocked), but the real ClickUp API has never been hit.
- **Local dev environment was broken** — no `.venv` existed, so `pytest` silently collected 0
  tests ("No tests collected", no error surfaced). Rebuilt `.venv`, installed
  `requirements-dev.txt`; full suite now 25/25 passing, `ruff` clean.
- **Frozen binary rebuilt and smoke-tested**: `pyinstaller` build succeeds, `--help` works,
  license gate correctly blocks `snapshot` with "License check failed" when no
  `UNDELETED_LICENSE_KEY` is set (buyers-without-a-key path confirmed correct).
- **Real Lemon Squeezy Test-mode checkout attempted via browser automation, not completed** —
  the payment iframe re-renders/loses field state on every validation pass (email field got
  clobbered twice, a "Save info for faster checkout" Link flow appeared demanding a phone
  number, coordinates kept drifting). Burned several turns fighting it; stopped rather than
  keep retrying, handed it back to Leon to do manually instead.
- **Real license key validated (26 Aug, follow-up)** — Leon completed the Test-mode purchase
  himself (order #4564481, $29, key `43690A75-08D8-44A8-8925-858BE80326E2`). Ran
  `UNDELETED_LICENSE_KEY=<key> ./dist/undeleted-bin snapshot --source todoist` — accepted
  cleanly, `Snapshot (todoist): 0 tasks, committed 3dbb8e65`, exit 0. **The full purchase →
  license → gate-unlock path is now confirmed end to end, real key, not mocked.** This closes
  the last blocking item.
- **ClickUp live-tested (26 Aug, follow-up)** — Leon added a real `CLICKUP_API_TOKEN`. Ran
  `./undeleted.py snapshot --source clickup` — `Snapshot (clickup): 6 tasks, committed
  53d78ede`. Ran `./undeleted.py restore --source clickup --commit HEAD` — `Nothing missing
  compared to HEAD — 6 tasks match.` Both exit 0 against a real workspace. **Every source
  (Todoist, Asana, ClickUp) is now live-tested. No open technical items remain.**

## Status: ready to launch
All engineering blockers closed. 25/25 tests passing, ruff clean, CI cron confirmed green,
all three task-manager sources live-tested, real Lemon Squeezy purchase → license key →
gate-unlock confirmed end to end. Nothing left but `LAUNCH.md`'s day 1/3/7 distribution
sequence — see that file for the full plan (Show HN + r/todoist day 1, forum replies +
directory submissions day 3, `awesome-cli-apps` PR + SEO post day 7).

Full step-by-step in the "UnDeleted: Ship Runbook" artifact and the "UnDeleted Launch Runbook"
published artifact. Phases 1–6 closed. Phase 7 (launch) is the only thing left, and it's a
distribution task, not a technical one.

## Status (26 Aug, session 6 — store actually live, LICENSE added, r/todoist ruled out)
- **Store is genuinely live now.** Session 5's "ready to launch" was wrong on one count: the
  checkout was still in Test mode days after Lemon Squeezy's approval — confirmed directly on
  the live checkout page. Fixed for real this session: activated live mode, used "Copy to Live
  Mode" on both products (test-mode products don't carry over automatically), and updated the
  checkout links — copying to live mode issues **new product IDs**, so the old test-mode links
  in `landing/index.html`/`docs/index.html` would only ever have processed test payments.
  New live links: lifetime `ad95782f-6f4d-4b1a-ae4c-a00b756b68d0`, annual
  `e1638e88-7d20-4ce9-baff-94f824461a7c`. Verified both directly (no "Test mode" banner) and
  confirmed GitHub Pages is serving the updated links. **This is the real remaining blocker
  from every prior session closed.**
- **MIT LICENSE added.** Repo had none — GitHub defaults to all-rights-reserved, so "open
  source, audit it yourself" on the landing page wasn't actually true, and `awesome-cli-apps`
  (which requires a free/OSS license) would have rejected the PR outright. Confirmed GitHub now
  detects it (`licenseInfo.key: "mit"`).
- **GitHub star/watch CTA shipped** (session 5's plan, actually built this time) — added to
  README and landing page trust-strip as the zero-setup interest signal, since a real
  email-capture form would have needed a new third-party account nobody had set up.
- **r/todoist is ruled out as a self-promo channel — checked the actual current rules, not
  assumed.** Rule 3: "No AI generated comments" — explicit permanent-ban risk, moderator
  discretion. Rule 7: "No self-promotion," flat, no disclosed-founder carve-out visible. The
  drafted Show HN/r/todoist copy is AI-written and is a founder pitching their own paid
  product — posting it as drafted would risk a permanent ban, not just a removed post. Did not
  post; backed out of the submit form with nothing typed in.
- **Found a real, current, on-topic thread while checking r/todoist**: "Will we ever get a real
  backup / restore / export?" (r/todoist, 10 days old, `Spirited-Bridge8405`, Todoist Pro
  subscriber, frustrated about a broken search-index bug Todoist support escalated and never
  fixed). One reply in that thread ("build your own backup with the API in 10 minutes if
  you're using Claude already") is a live, real-world instance of the exact free-DIY
  competitive threat the brutal review flagged. Good candidate for the LAUNCH.md day-7 "DM
  people who publicly complained" tactic — direct outreach, not a self-promo post, sidesteps
  rule 7.
- **Show HN still blocked on login** — checked, not logged into Hacker News in this browser.
  Same as Lemon Squeezy: needs Leon's own login, can't be done for him.

## Status (27 Aug, session 7 — market-audit fixes shipped, terminal-trove submitted)
- **All 5 market-audit fixes shipped to the live landing page**, pushed and deployed:
  proof quote replaced with an honest zero-customers framing (was flagged independently by 3
  of 5 audit agents), a named comparison table (Todoist-native, ProBackup.io) added conceding
  the feature-depth gap and winning on ownership/price/portability, OG/Twitter/canonical/
  JSON-LD SoftwareApplication tags added (page had none, was unshareable and unindexed), and
  ClickUp added to the hero/meta copy (was pricing-card-only before).
- **A real terminal-output preview image now exists and is committed**:
  `assets/terminal-preview.png` (built from actual `undeleted.py` output, not staged/fake),
  served via raw.githubusercontent.com. Closes the "no image asset" gap that was blocking the
  terminal-trove submission.
- **Submitted to terminal-trove.com — confirmed live**, "Thank you for your submission"
  received. Caught and fixed a real accuracy problem along the way: the form auto-filled
  `pip install undeleted` / `pipx install undeleted` / `uv install undeleted` install
  commands, which are all **wrong** — UnDeleted isn't published to PyPI. Removed those,
  replaced with the actual install path (GitHub Releases binary download).
- **alternativeto.net — stopped at account creation, on purpose.** Creating an account (even
  via Google/GitHub/Apple OAuth) is the same "create accounts / authenticate" action that's
  off-limits regardless of the request behind it. Navigated to the sign-up modal so it's one
  click away, but this one is Leon's to actually do — starts the 7-day clock the moment he does.

## Status (28 Aug, session 8 — HN Show HN blocked, Reddit DM sent)
- **alternativeto.net account created** (28 Aug) — 7-day clock running, eligible ~4 Sept.
  Email still needs verifying (banner live, Leon's own inbox, not something I can do).
- **Show HN is blocked, not just "not logged in" anymore.** Leon logged in and attempted to
  submit; HN's own automated response says Show HN is "temporarily restricted... because of a
  massive influx" of unfamiliar accounts, and pointed to the newsguidelines/newswelcome/showhn
  pages. Confirmed via `news.ycombinator.com/submitted?id=liveskyhigh84` — **zero submissions
  exist**, so the post never actually got created. There's nothing to add a first-comment to.
  Real next step per HN's own guidance: participate normally (comments, upvotes, maybe a
  non-Show-HN link) for a while first, then retry Show HN later. Not a same-session fix.
- **Fixed a real inconsistency in the drafted HN/Reddit copy before anything got used**: both
  the Show HN body and the r/todoist body still had the old unsourced "recurring pattern" /
  "dozens of threads" claims that were already replaced on the live landing page (per the
  market-audit fixes, session 7). Rewrote both to match the honest zero-customers framing now
  actually on the site — validated clean against ai-tells-validator after two revision passes
  (first pass introduced a "not X, I just Y" contrast pattern, fixed). Runbook artifact
  republished with the corrected copy.
- **Sent the Reddit DM to `Spirited-Bridge8405`** (the real, current "Will we ever get a real
  backup / restore / export?" thread author from session 6) — confirmed "Message sent" toast.
  This was explicit, per-message user approval for this specific send, not a standing
  authorization to message people generally.

## Next actions
1. Verify email on alternativeto.net (Leon's inbox).
2. Wait out the alternativeto.net 7-day account-age gate (~4 Sept), then submit.
3. HN: no action available this session — read newsguidelines.html/newswelcome.html, participate
   normally for a while, retry Show HN later. Corrected copy is ready in the Launch Runbook
   artifact whenever that day comes.
4. r/todoist: still open — skip it, or write a genuinely personal, non-AI, disclosed-founder
   version if Leon wants a presence there. The corrected drafted copy is still AI-authored and
   still not safe to post as a public submission (rule 3), even though it's now honest.
5. Everything else from session 5's Next Actions is still accurate and unaffected.
