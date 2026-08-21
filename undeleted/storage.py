import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if getattr(sys, "frozen", False):
    # PyInstaller bundles run from a temp extraction dir that's wiped on exit —
    # __file__ there is useless for persistence. Buyers running the compiled
    # binary get a stable, private location instead.
    SNAPSHOTS_DIR = Path.home() / ".undeleted" / "snapshots"
else:
    SNAPSHOTS_DIR = Path(__file__).resolve().parent.parent / "snapshots"


def _run_git(*args):
    return subprocess.run(["git", *args], cwd=SNAPSHOTS_DIR.parent, capture_output=True, text=True, check=False)


def ensure_repo():
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    if not (SNAPSHOTS_DIR.parent / ".git").exists():
        _run_git("init")


def write_snapshot(source, tasks):
    ensure_repo()
    path = SNAPSHOTS_DIR / f"{source}.json"
    path.write_text(json.dumps(tasks, indent=2, sort_keys=True, default=str))
    return path


def commit_snapshot(source, count):
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rel_path = f"snapshots/{source}.json"
    _run_git("add", rel_path)
    status = _run_git("status", "--porcelain", "--", rel_path)
    if not status.stdout.strip():
        return None
    message = f"snapshot: {source} {stamp} ({count} tasks)"
    result = _run_git("commit", "-m", message)
    if result.returncode != 0:
        return None
    sha = _run_git("rev-parse", "HEAD").stdout.strip()
    return sha


def read_snapshot_at(source, ref):
    rel_path = f"snapshots/{source}.json"
    result = _run_git("show", f"{ref}:{rel_path}")
    if result.returncode != 0:
        raise ValueError(f"Couldn't read {rel_path} at {ref}: {result.stderr.strip()}")
    return json.loads(result.stdout)
