from . import asana_snapshot, clickup_snapshot, storage, todoist_snapshot

_ID_FIELD = {"todoist": "id", "asana": "gid", "clickup": "id"}
_LABEL_FIELD = {"todoist": "content", "asana": "name", "clickup": "name"}
_BACKENDS = {"todoist": todoist_snapshot, "asana": asana_snapshot, "clickup": clickup_snapshot}


def find_missing(old_tasks, current_tasks, id_field="id"):
    current_ids = {t[id_field] for t in current_tasks}
    return [t for t in old_tasks if t[id_field] not in current_ids]


_TODOIST_PRIORITY = {1: "normal", 2: "medium", 3: "high", 4: "urgent"}


def _preview_detail(source, task):
    """Extra tangible detail (due date, priority, notes) shown before a real restore."""
    bits = []
    if source == "todoist":
        due = task.get("due") or {}
        if due.get("date"):
            bits.append(f"due {due['date']}")
        priority = task.get("priority")
        if priority and priority > 1:
            bits.append(_TODOIST_PRIORITY.get(priority, f"priority {priority}"))
        if task.get("description"):
            bits.append("has notes")
    elif source == "asana":
        if task.get("due_on"):
            bits.append(f"due {task['due_on']}")
        if task.get("notes"):
            bits.append("has notes")
    elif source == "clickup":
        if task.get("due_date"):
            bits.append(f"due (epoch ms) {task['due_date']}")
        priority = (task.get("priority") or {}).get("priority")
        if priority:
            bits.append(f"priority {priority}")
        if task.get("description"):
            bits.append("has notes")
    return f" ({', '.join(bits)})" if bits else ""


def restore_from(source, ref, dry_run=True):
    backend = _BACKENDS[source]
    id_field = _ID_FIELD[source]
    label_field = _LABEL_FIELD[source]

    old_tasks = storage.read_snapshot_at(source, ref)
    current_tasks = backend.fetch_tasks()
    missing = find_missing(old_tasks, current_tasks, id_field)

    if not missing:
        print(f"Nothing missing compared to {ref} — {len(current_tasks)} tasks match.")
        return []

    print(f"{len(missing)} task(s) in {ref} are missing from your current {source} list:")
    for t in missing:
        print(f"  - {t.get(label_field, '?')}{_preview_detail(source, t)}")

    if dry_run:
        print("\nDry run — nothing created. Re-run with --no-dry-run to restore these.")
        return missing

    restored = []
    for t in missing:
        new_task = backend.restore_task(t)
        restored.append(new_task)
        print(f"  Restored: {getattr(new_task, label_field, None) or new_task.get(label_field, '?')}")
    return restored
