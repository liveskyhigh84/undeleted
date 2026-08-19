# TaskGuardian — project memory

## What this is
Personal-use backup/diff/restore safety net for Todoist (Asana planned next). Born from a
GapScope run reverse-engineering Todoist's App Store reviews (18 Aug 2026) — dominant complaint
was silent task loss on sync/update, not a missing feature. Brutal verdict: STOP on building a
competing to-do app (graveyard category, Todoist can just patch the bug), GO on this narrow
companion tool instead — precedent: BackupLABS/NotionBackups.com already monetize this exact
model ($8-9/mo) for other tools, neither covers Todoist/Asana.

## Status (18 Aug 2026)
- Built: full Todoist snapshot/restore/monitor pipeline, tested for import/CLI correctness.
- NOT yet tested against a real Todoist account — needs `TODOIST_API_TOKEN` from Leon
  (Todoist → Settings → Integrations → Developer) before first live run.
- NOT yet pushed to a GitHub repo — local git repo only so far (`git init` ran in project root,
  snapshots/ commits locally). GitHub Actions workflow is written but inert until a remote exists
  + secrets are added.
- healthchecks.io / ntfy.sh — not signed up (needs Leon's own account creation, left to him
  per the "don't auto-create accounts" rule). Code supports both, degrades gracefully if unset.
- Asana integration: scaffolded in the plan, not built — ship Todoist first per the build order,
  same pattern applies when it's time.

## Architecture decision worth remembering
Git itself is the diff/version-history/restore engine — deliberately did not build a custom
diff UI or database. `snapshots/todoist.json` gets overwritten + committed each run; `git log`/
`git diff` on that one file is the entire history layer.

## Next actions (for Leon or a future session)
1. Get Todoist API token, run `taskguardian snapshot` for real, confirm output looks right.
2. Decide: local launchd/cron, or push to GitHub + Actions (recommended — runs when Mac's off).
3. Sign up for healthchecks.io + ntfy.sh (both free, no card) if the alerting layer is wanted.
