from undeleted.restore import (
    _BACKENDS,
    _ID_FIELD,
    _LABEL_FIELD,
    _preview_detail,
    find_missing,
)


def test_find_missing_returns_tasks_no_longer_present():
    old = [{"id": "1", "content": "a"}, {"id": "2", "content": "b"}, {"id": "3", "content": "c"}]
    current = [{"id": "1", "content": "a"}]

    missing = find_missing(old, current)

    assert {t["id"] for t in missing} == {"2", "3"}


def test_find_missing_empty_when_nothing_lost():
    old = [{"id": "1", "content": "a"}]
    current = [{"id": "1", "content": "a"}, {"id": "2", "content": "b"}]

    assert find_missing(old, current) == []


def test_find_missing_handles_empty_old_snapshot():
    assert find_missing([], [{"id": "1"}]) == []


def test_find_missing_all_missing_when_current_empty():
    old = [{"id": "1"}, {"id": "2"}]
    assert len(find_missing(old, [])) == 2


def test_find_missing_uses_custom_id_field_for_asana():
    old = [{"gid": "111", "name": "a"}, {"gid": "222", "name": "b"}]
    current = [{"gid": "111", "name": "a"}]

    missing = find_missing(old, current, id_field="gid")

    assert [t["gid"] for t in missing] == ["222"]


def test_clickup_is_registered_as_a_backend():
    assert _ID_FIELD["clickup"] == "id"
    assert _LABEL_FIELD["clickup"] == "name"
    assert "clickup" in _BACKENDS


def test_preview_detail_shows_todoist_due_and_priority():
    task = {"due": {"date": "2026-09-01"}, "priority": 4}
    assert _preview_detail("todoist", task) == " (due 2026-09-01, urgent)"


def test_preview_detail_blank_when_nothing_to_show():
    assert _preview_detail("todoist", {}) == ""


def test_preview_detail_shows_asana_due_date():
    assert _preview_detail("asana", {"due_on": "2026-09-01"}) == " (due 2026-09-01)"


def test_preview_detail_shows_clickup_priority():
    task = {"priority": {"priority": "high"}, "due_date": "1700000000000"}
    detail = _preview_detail("clickup", task)
    assert "priority high" in detail
    assert "due (epoch ms) 1700000000000" in detail
