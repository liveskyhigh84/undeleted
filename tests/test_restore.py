from undeleted.restore import find_missing


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
