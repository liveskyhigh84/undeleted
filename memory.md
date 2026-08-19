# TaskGuardian — project memory

## What this is
Backup/diff/restore safety net for Todoist (Asana added) — sold as Path A: bring-your-own-token
CLI, never a hosted service. Born from a GapScope run reverse-engineering Todoist's App Store
reviews (18 Aug 2026). Brutal verdict: STOP on a competing to-do app, GO on this narrow
companion tool — precedent: BackupLABS/NotionBackups.com already monetize this exact model.

## Status (18 Aug 2026, session 2)
- Todoist: full snapshot/restore/monitor pipeline, tested (unit + CLI).
- Asana: snapshot/restore module built (`asana_snapshot.py`), same interface as Todoist,
  wired into `restore.py`'s multi-source dispatch. NOT tested against a real Asana account
  (needs a token — same as Todoist's untested-live status).
- License gate: `license.py`, Gumroad license API, optional (off unless
  `TASKGUARDIAN_GUMROAD_PRODUCT_ID` is set) — Leon's own instance runs ungated by default.
  7-day recheck cache, 30-day offline grace period.
- `taskguardian init` — interactive Keychain setup wizard (mitigates the CLI-only-interface
  blindspot somewhat; doesn't remove it — still no GUI/web option).
- `taskguardian status [--notify]` — snapshot-count/task-count digest, pushable via ntfy
  (retention/churn mitigation: reminds a subscriber what's being protected).
- Real test suite: `tests/` — 15 pytest tests, all passing. Covers `find_missing` diff logic,
  git-backed storage (real isolated temp repo, not mocked), license verification incl.
  network-failure/grace-period paths. Directly closes the "restore only tested in dry-run"
  blindspot with actual verification — though still not a live-account test.
- `ruff check` clean (fixed import sorting, unused imports, blind-exception-catch at the CLI
  boundary — justified with `# noqa: BLE001`, subprocess `check=False` explicitness).
- Todoist ToS fact-check done (WebFetch on doist.com/terms-of-service +
  developer.todoist.com/api/v1/): no clause bans a commercial tool on personal tokens.
  Two real requirements found and applied: app name can't lead with "Todoist" (already fine —
  "TaskGuardian"), and a "not affiliated with Doist" disclaimer is required (added to README).
  Section 12(g) bans "transferring access granted under these Terms" — this is *why* Path A
  (each customer's own token, never Leon's) isn't just safer, it's the compliant model.

## Known gap not yet closed
Global Python style rules (type hints on all signatures, black/isort formatting) were applied
to new/edited code this session (`taskguardian.py`, `license.py` config additions) but NOT
retrofitted onto the files written in session 1 (`storage.py`, `restore.py`'s original half,
`monitor.py`, `todoist_snapshot.py`) beyond what ruff's autofix touched. Low priority — code
works and is tested — but flag before a real style/lint gate is added to CI.

## Next actions (for Leon or a future session)
1. Get a Todoist token, run `taskguardian snapshot` for real — first live-account test.
2. Same for Asana once a token exists.
3. Decide: keep licensing off (pure personal tool) or set up a Gumroad product + enable the gate
   for Path A sale.
4. Push to a GitHub repo if going the paid-repo-access route, or package as a license-gated
   download if going the license-key route.
5. Sign up for healthchecks.io + ntfy.sh (free) if the alerting layer is wanted.
