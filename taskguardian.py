#!/Users/leonthompson/Developer/TaskGuardian/.venv/bin/python3
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from taskguardian import monitor, restore, storage, todoist_snapshot

DROP_ALERT_THRESHOLD = 0.15


def previous_task_count(source):
    path = storage.SNAPSHOTS_DIR / f"{source}.json"
    if not path.exists():
        return None
    try:
        return len(json.loads(path.read_text()))
    except (json.JSONDecodeError, OSError):
        return None


def cmd_snapshot(args):
    before = previous_task_count("todoist")
    try:
        tasks = todoist_snapshot.fetch_tasks()
    except Exception as e:
        monitor.ping_healthchecks(status="fail")
        monitor.notify(f"TaskGuardian: snapshot failed — {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1

    storage.write_snapshot("todoist", tasks)
    sha = storage.commit_snapshot("todoist", len(tasks))

    if before is not None and before > 0:
        drop = (before - len(tasks)) / before
        if drop >= DROP_ALERT_THRESHOLD:
            monitor.notify(
                f"TaskGuardian: task count dropped {drop:.0%} "
                f"({before} → {len(tasks)}). Possible silent deletion — check {sha or 'latest snapshot'}."
            )

    monitor.ping_healthchecks(status="success")
    print(f"Snapshot: {len(tasks)} tasks" + (f", committed {sha[:8]}" if sha else " (no change)"))
    return 0


def cmd_restore(args):
    missing = restore.restore_from("todoist", args.commit, dry_run=not args.no_dry_run)
    return 0 if missing is not None else 1


def main():
    parser = argparse.ArgumentParser(prog="taskguardian", description="Backup, diff, and restore for Todoist.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_snap = sub.add_parser("snapshot", help="Pull current tasks and commit a snapshot")
    p_snap.set_defaults(func=cmd_snapshot)

    p_restore = sub.add_parser("restore", help="Restore tasks missing since a given snapshot")
    p_restore.add_argument("--commit", default="HEAD~1", help="Git ref to restore from (default: HEAD~1)")
    p_restore.add_argument("--no-dry-run", action="store_true", help="Actually recreate missing tasks")
    p_restore.set_defaults(func=cmd_restore)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
