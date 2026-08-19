# TaskGuardian

Backup/diff/restore safety net for Todoist and Asana. Git is the version-history engine —
no custom diff code. Not a replacement app; runs alongside the tool you already use.

> TaskGuardian is not created by, affiliated with, or supported by Doist (Todoist) or Asana, Inc.

## Setup

```
cd ~/Developer/TaskGuardian
./.venv/bin/pip install -r requirements.txt   # already done on first build
```

Interactive setup (stores your token in macOS Keychain):

```
taskguardian init
```

Or manually:
1. Todoist personal API token: Todoist → Settings → Integrations → Developer.
   Asana personal access token: Asana → My Settings → Apps → Manage Developer Apps.
2. Store it (pick one):
   - Env var: `export TODOIST_API_TOKEN="..."` / `export ASANA_ACCESS_TOKEN="..."`
   - macOS Keychain: `security add-generic-password -a todoist_token -s taskguardian -w "TOKEN"`
3. Optional monitoring (both free, no card):
   - [healthchecks.io](https://healthchecks.io) → create a check → `export HEALTHCHECKS_URL="https://hc-ping.com/your-uuid"`
   - [ntfy.sh](https://ntfy.sh) → pick a long random topic slug → `export NTFY_TOPIC="your-random-slug"` → subscribe to it in the ntfy app

## Usage

```
taskguardian snapshot --source todoist          # pull tasks, commit if changed
taskguardian snapshot --source asana
taskguardian restore --source todoist --commit HEAD~5     # dry-run: show what's missing
taskguardian restore --source todoist --commit HEAD~5 --no-dry-run   # actually restore
taskguardian status                              # tracked-task counts + snapshot history
taskguardian status --notify                     # also push the summary via ntfy
```

Each snapshot overwrites `snapshots/<source>.json` and commits it — `git log` and `git diff`
on that one file give you full history for free.

## Scheduling (pick one)

**Local (Mac must be on):** add a `launchd` plist or cron entry calling
`~/Developer/TaskGuardian/taskguardian.py snapshot` daily.

**GitHub Actions (runs even when your Mac's off, recommended):**
1. `git remote add origin <your private repo URL>` and push.
2. Repo Settings → Secrets → Actions: add `TODOIST_API_TOKEN`, optionally `HEALTHCHECKS_URL`, `NTFY_TOPIC`.
3. `.github/workflows/snapshot.yml` is already wired — runs daily at 09:00 UTC, commits snapshots back to the repo.

## Alert threshold

A snapshot that shows the task count dropping ≥15% from the previous one triggers an ntfy alert —
that's the exact silent-deletion pattern this tool exists to catch.

## Selling this (Path A — bring-your-own-token)

Sold as the CLI itself (a standalone binary or a license-gated repo), never as a hosted service.
Buyers run it on their own machine with their own Todoist/Asana token — you never see their
credentials or task data. This is also the compliant model: Todoist's ToS prohibits transferring
access granted to *your* account, so a shared-token hosted version isn't just riskier, it's
against the terms. Each customer must generate their own token.

Pricing: one-time lifetime license ($29–39), or $19/yr — no monthly subscription (see
`LAUNCH.md` for the reasoning). License checks run against **Lemon Squeezy**'s free License API
(~5.5% total fee vs. Gumroad's ~14%, same free verify-license capability).

Licensing is off by default. To enable it:

```
export TASKGUARDIAN_LICENSE_REQUIRED=1
```

With that unset (the default for your own personal instance), every command runs unlicensed —
no gate. Once set, `snapshot`/`restore` require a valid `TASKGUARDIAN_LICENSE_KEY`
(env var or Keychain entry `taskguardian_license`), verified against Lemon Squeezy's license API,
cached for 7 days, with a 30-day offline grace period so a payment-provider outage doesn't lock
out a paying customer mid-trip.

## Packaging (standalone binary, no Python required for the buyer)

```
./.venv/bin/pip install -r requirements-dev.txt
./scripts/build_release.sh          # builds dist/taskguardian-bin for your current OS, smoke-tests it
```

`.github/workflows/release.yml` builds macOS/Linux/Windows binaries automatically and attaches
them to a GitHub release whenever a `v*` tag is pushed — no local cross-compilation needed.

## Testing

```
./.venv/bin/pip install -r requirements-dev.txt
./.venv/bin/pytest -q
./.venv/bin/ruff check taskguardian.py taskguardian/
```

15 tests cover `find_missing` diff logic, git-backed snapshot read/write/commit (against a real
isolated temp repo, not mocked), and license verification (valid/invalid/network-failure/grace-period).
Not covered: a live run against a real Todoist/Asana account — needs your token, see Setup.

## Files

```
taskguardian/
  config.py             token loading (env var → Keychain fallback)
  todoist_snapshot.py   fetch + restore via todoist-api-python
  asana_snapshot.py     fetch + restore via the official asana client
  storage.py             git-backed snapshot read/write
  restore.py             diff old vs current, report/restore missing tasks (multi-source)
  monitor.py             healthchecks.io ping + ntfy alert
  license.py             optional Lemon Squeezy license gate
taskguardian.py           CLI entrypoint (init / snapshot / restore / status)
snapshots/                git-tracked JSON snapshots (the actual backup data)
tests/                    pytest suite, 15 tests
scripts/build_release.sh  local PyInstaller standalone-binary build + smoke test
landing/                  marketing landing page
LAUNCH.md                 positioning, pricing, distribution, launch-week sequence
.github/workflows/        daily snapshot cron + tagged-release cross-platform binary builds
```
