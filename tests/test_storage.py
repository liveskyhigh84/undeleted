import json
import subprocess

import pytest

from taskguardian import storage


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
