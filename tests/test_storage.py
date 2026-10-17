import json
import subprocess

import pytest

from undeleted import storage


@pytest.fixture
def isolated_repo(tmp_path, monkeypatch):
    snapshots_dir = tmp_path / "snapshots"
    monkeypatch.setattr(storage, "SNAPSHOTS_DIR", snapshots_dir)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    return tmp_path


def test_write_snapshot_creates_json_file(isolated_repo):
    path = storage.write_snapshot("todoist", [{"id": "1", "content": "buy milk"}])

    assert path.exists()
    assert json.loads(path.read_text()) == [{"id": "1", "content": "buy milk"}]


def test_commit_snapshot_commits_when_changed(isolated_repo):
    storage.write_snapshot("todoist", [{"id": "1"}])
    sha = storage.commit_snapshot("todoist", 1)

    assert sha is not None
    assert len(sha) == 40


def test_commit_snapshot_returns_none_when_unchanged(isolated_repo):
    storage.write_snapshot("todoist", [{"id": "1"}])
    storage.commit_snapshot("todoist", 1)

    storage.write_snapshot("todoist", [{"id": "1"}])  # identical content
    second_sha = storage.commit_snapshot("todoist", 1)

    assert second_sha is None


def test_read_snapshot_at_returns_historical_data(isolated_repo):
    storage.write_snapshot("todoist", [{"id": "1"}, {"id": "2"}])
    first_sha = storage.commit_snapshot("todoist", 2)

    storage.write_snapshot("todoist", [{"id": "1"}])  # task 2 disappeared
    storage.commit_snapshot("todoist", 1)

    old_snapshot = storage.read_snapshot_at("todoist", first_sha)

    assert {t["id"] for t in old_snapshot} == {"1", "2"}


# --- regression: a snapshot that is not committed must never pass silently ---
# (2026-08: `snapshots/` landed in .gitignore, plain `git add` no-opped, and
# every snapshot was silently dropped for 5 days.)

def test_snapshot_is_committed_even_if_path_is_gitignored(isolated_repo):
    (isolated_repo / ".gitignore").write_text("snapshots/\n")
    storage.write_snapshot("todoist", [{"id": "1"}])

    sha = storage.commit_snapshot("todoist", 1)

    assert sha is not None, "ignored snapshot path must still be committed"
    shown = subprocess.run(["git", "show", f"{sha}:snapshots/todoist.json"], cwd=isolated_repo,
                           capture_output=True, text=True, check=True).stdout
    assert json.loads(shown) == [{"id": "1"}]


def test_new_snapshot_is_tracked_in_git_after_commit(isolated_repo):
    storage.write_snapshot("asana", [{"id": "9"}])
    storage.commit_snapshot("asana", 1)

    tracked = subprocess.run(["git", "ls-files", "snapshots/asana.json"], cwd=isolated_repo,
                             capture_output=True, text=True, check=True).stdout.strip()
    assert tracked == "snapshots/asana.json"


def test_commit_failure_raises_instead_of_returning_none(isolated_repo):
    # No author identity and no way to infer one -> `git commit` fails.
    subprocess.run(["git", "config", "--unset", "user.email"], cwd=isolated_repo, check=True)
    subprocess.run(["git", "config", "--unset", "user.name"], cwd=isolated_repo, check=True)
    import os
    env = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull, "GIT_AUTHOR_NAME": "", "GIT_COMMITTER_NAME": "",
           "GIT_AUTHOR_EMAIL": "", "GIT_COMMITTER_EMAIL": "", "EMAIL": ""}
    for k, v in env.items():
        os.environ[k] = v
    try:
        storage.write_snapshot("todoist", [{"id": "1"}])
        with pytest.raises(storage.StorageError):
            storage.commit_snapshot("todoist", 1)
    finally:
        for k in env:
            os.environ.pop(k, None)


def test_repo_gitignore_does_not_ignore_snapshots():
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    lines = [l.strip() for l in (root / ".gitignore").read_text().splitlines()]
    assert not any(l.strip("/") in ("snapshots", "snapshots/*") for l in lines)
