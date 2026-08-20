from . import asana_snapshot, storage, todoist_snapshot

_ID_FIELD = {"todoist": "id", "asana": "gid"}
_LABEL_FIELD = {"todoist": "content", "asana": "name"}
_BACKENDS = {"todoist": todoist_snapshot, "asana": asana_snapshot}


def find_missing(old_tasks, current_tasks, id_field="id"):
    current_ids = {t[id_field] for t in current_tasks}
    return [t for t in old_tasks if t[id_field] not in current_ids]


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
        print(f"  - {t.get(label_field, '?')}")

    if dry_run:
        print("\nDry run — nothing created. Re-run with --no-dry-run to restore these.")
        return missing

    restored = []
    for t in missing:
        new_task = backend.restore_task(t)
        restored.append(new_task)
        print(f"  Restored: {getattr(new_task, label_field, None) or new_task.get(label_field, '?')}")
    return restored
