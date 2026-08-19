# TaskGuardian

Personal backup/diff/restore safety net for Todoist. Git is the version-history engine —
no custom diff code. Not a replacement app; runs alongside Todoist.

## Setup

```
cd ~/Developer/TaskGuardian
./.venv/bin/pip install -r requirements.txt   # already done on first build
```

1. Get a Todoist personal API token: Todoist → Settings → Integrations → Developer.
2. Store it (pick one):
   - Env var: `export TODOIST_API_TOKEN="..."` (add to `~/.zshrc` to persist)
   - macOS Keychain: `security add-generic-password -a todoist_token -s taskguardian -w "TOKEN"`
3. Optional monitoring (both free, no card):
   - [healthchecks.io](https://healthchecks.io) → create a check → `export HEALTHCHECKS_URL="https://hc-ping.com/your-uuid"`
   - [ntfy.sh](https://ntfy.sh) → pick a long random topic slug → `export NTFY_TOPIC="your-random-slug"` → subscribe to it in the ntfy app

## Usage

```
taskguardian snapshot                    # pull tasks, commit if changed
taskguardian restore --commit HEAD~5     # dry-run: show what's missing vs 5 snapshots ago
taskguardian restore --commit HEAD~5 --no-dry-run   # actually recreate missing tasks
```

Each snapshot overwrites `snapshots/todoist.json` and commits it — `git log -- snapshots/todoist.json`
and `git diff <ref> -- snapshots/todoist.json` give you full history and diffs for free.

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

## Not built yet (per the plan — ship Todoist first)

- Asana snapshot/restore (module scaffold not started — same pattern as Todoist once this is proven)
- Two-way sync — this is backup/restore only, additive on restore, never destructive

## Files

```
taskguardian/
  config.py            token loading (env var → Keychain fallback)
  todoist_snapshot.py  fetch + restore via todoist-api-python
  storage.py           git-backed snapshot read/write
  restore.py           diff old vs current, report/restore missing tasks
  monitor.py           healthchecks.io ping + ntfy alert
taskguardian.py         CLI entrypoint (snapshot / restore)
snapshots/              git-tracked JSON snapshots (the actual backup data)
.github/workflows/      GitHub Actions daily cron
```
