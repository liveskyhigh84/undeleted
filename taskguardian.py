#!/Users/leonthompson/Developer/TaskGuardian/.venv/bin/python3
import argparse
import getpass
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from taskguardian import (
    asana_snapshot,
    license,
    monitor,
    restore,
    storage,
    todoist_snapshot,
)

DROP_ALERT_THRESHOLD = 0.15
_BACKENDS = {"todoist": todoist_snapshot, "asana": asana_snapshot}


def previous_task_count(source: str) -> int | None:
    path = storage.SNAPSHOTS_DIR / f"{source}.json"
    if not path.exists():
        return None
    try:
        return len(json.loads(path.read_text()))
    except (json.JSONDecodeError, OSError):
        return None


def require_license() -> bool:
    if license.is_licensed():
        return True
    print(
        "License check failed. Set TASKGUARDIAN_LICENSE_KEY to a valid Gumroad license key,\n"
        "or unset TASKGUARDIAN_GUMROAD_PRODUCT_ID for a personal/dev instance.",
        file=sys.stderr,
    )
    return False


def cmd_snapshot(args: argparse.Namespace) -> int:
    if not require_license():
        return 1

    source = args.source
    backend = _BACKENDS[source]
    before = previous_task_count(source)
    try:
        tasks = backend.fetch_tasks()
    except Exception as e:  # noqa: BLE001 — CLI boundary: any backend failure must be caught and reported, not crash
        monitor.ping_healthchecks(status="fail")
        monitor.notify(f"TaskGuardian: {source} snapshot failed — {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1

    storage.write_snapshot(source, tasks)
    sha = storage.commit_snapshot(source, len(tasks))

    if before is not None and before > 0:
        drop = (before - len(tasks)) / before
        if drop >= DROP_ALERT_THRESHOLD:
            monitor.notify(
                f"TaskGuardian: {source} task count dropped {drop:.0%} "
                f"({before} → {len(tasks)}). Possible silent deletion — check {sha or 'latest snapshot'}."
            )

    monitor.ping_healthchecks(status="success")
    print(f"Snapshot ({source}): {len(tasks)} tasks" + (f", committed {sha[:8]}" if sha else " (no change)"))
    return 0


def cmd_restore(args: argparse.Namespace) -> int:
    if not require_license():
        return 1
    missing = restore.restore_from(args.source, args.commit, dry_run=not args.no_dry_run)
    return 0 if missing is not None else 1


def cmd_status(args: argparse.Namespace) -> int:
    lines = []
    for source in ("todoist", "asana"):
        count = previous_task_count(source)
        if count is None:
            continue
        log = subprocess.run(
            ["git", "log", "--oneline", "--", f"snapshots/{source}.json"],
            cwd=storage.SNAPSHOTS_DIR.parent, capture_output=True, text=True, check=False,
        )
        snapshot_count = len(log.stdout.strip().splitlines())
        lines.append(f"{source}: {count} tasks tracked, {snapshot_count} snapshots taken")

    if not lines:
        print("No snapshots yet — run `taskguardian snapshot` first.")
        return 0

    summary = "TaskGuardian status — " + "; ".join(lines)
    print(summary)
    if args.notify:
        monitor.notify(summary)
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    print("TaskGuardian setup\n")
    source = input("Which service? [todoist/asana]: ").strip().lower()
    if source not in ("todoist", "asana"):
        print("Must be 'todoist' or 'asana'", file=sys.stderr)
        return 1

    prompt = f"{source.capitalize()} API token (input hidden): "
    token = getpass.getpass(prompt).strip()
    if not token:
        print("No token entered, aborting.", file=sys.stderr)
        return 1

    account = f"{source}_token"
    # token is briefly visible to other local processes via `ps` during this call — macOS's
    # `security add-generic-password` has no stdin input mode. Acceptable for a single-user
    # local setup wizard; not something to harden further here.
    result = subprocess.run(
        ["security", "add-generic-password", "-a", account, "-s", "taskguardian", "-w", token, "-U"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        print(f"Couldn't save to Keychain: {result.stderr.strip()}", file=sys.stderr)
        print(f"You can instead: export {source.upper()}_API_TOKEN=\"...\"" if source == "todoist"
              else "You can instead: export ASANA_ACCESS_TOKEN=\"...\"")
        return 1

    print(f"\nSaved to macOS Keychain (account: {account}). Run: taskguardian snapshot --source {source}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="taskguardian", description="Backup, diff, and restore for Todoist/Asana.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Interactive setup — store an API token in Keychain")
    p_init.set_defaults(func=cmd_init)

    p_snap = sub.add_parser("snapshot", help="Pull current tasks and commit a snapshot")
    p_snap.add_argument("--source", choices=["todoist", "asana"], default="todoist")
    p_snap.set_defaults(func=cmd_snapshot)

    p_restore = sub.add_parser("restore", help="Restore tasks missing since a given snapshot")
    p_restore.add_argument("--source", choices=["todoist", "asana"], default="todoist")
    p_restore.add_argument("--commit", default="HEAD~1", help="Git ref to restore from (default: HEAD~1)")
    p_restore.add_argument("--no-dry-run", action="store_true", help="Actually recreate missing tasks")
    p_restore.set_defaults(func=cmd_restore)

    p_status = sub.add_parser("status", help="Show tracked task counts and snapshot history")
    p_status.add_argument("--notify", action="store_true", help="Also push the summary via ntfy")
    p_status.set_defaults(func=cmd_status)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
