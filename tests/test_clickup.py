from unittest.mock import MagicMock, patch

import pytest

from undeleted import clickup_snapshot


def test_headers_raises_without_token():
    with patch.object(clickup_snapshot.config, "CLICKUP_TOKEN", None), \
         pytest.raises(RuntimeError, match="No ClickUp token"):
        clickup_snapshot._headers()


def test_headers_uses_raw_token_no_bearer_prefix():
    with patch.object(clickup_snapshot.config, "CLICKUP_TOKEN", "pk_123"):
        assert clickup_snapshot._headers() == {"Authorization": "pk_123"}


def test_fetch_tasks_paginates_until_empty_page():
    team_resp = MagicMock()
    team_resp.json.return_value = {"teams": [{"id": "1", "members": [{"user": {"id": "9"}}]}]}
    team_resp.raise_for_status.return_value = None

    page0 = MagicMock()
    page0.json.return_value = {"tasks": [{"id": "a"}, {"id": "b"}]}
    page0.raise_for_status.return_value = None

    page1 = MagicMock()
    page1.json.return_value = {"tasks": []}
    page1.raise_for_status.return_value = None

    with patch.object(clickup_snapshot.config, "CLICKUP_TOKEN", "pk_123"), \
         patch.object(clickup_snapshot.requests, "get", side_effect=[team_resp, page0, page1]) as mock_get:
        tasks = clickup_snapshot.fetch_tasks()

    assert [t["id"] for t in tasks] == ["a", "b"]
    assert mock_get.call_count == 3


def test_restore_task_requires_list_id():
    with pytest.raises(ValueError, match="no source list id"):
        clickup_snapshot.restore_task({"name": "orphan task"})


def test_restore_task_posts_to_source_list():
    resp = MagicMock()
    resp.json.return_value = {"id": "new-task"}
    resp.raise_for_status.return_value = None

    task = {"name": "Ship it", "description": "notes", "due_date": "1700000000000", "list": {"id": "list-1"}}

    with patch.object(clickup_snapshot.config, "CLICKUP_TOKEN", "pk_123"), \
         patch.object(clickup_snapshot.requests, "post", return_value=resp) as mock_post:
        result = clickup_snapshot.restore_task(task)

    assert result == {"id": "new-task"}
    url, kwargs = mock_post.call_args[0][0], mock_post.call_args[1]
    assert url == "https://api.clickup.com/api/v2/list/list-1/task"
    assert kwargs["json"]["name"] == "Ship it"
    assert kwargs["json"]["due_date"] == 1700000000000
