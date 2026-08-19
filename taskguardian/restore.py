from . import storage, todoist_snapshot


def find_missing(old_tasks, current_tasks):
    current_ids = {t["id"] for t in current_tasks}
    return [t for t in old_tasks if t["id"] not in current_ids]


def restore_from(source, ref, dry_run=True):
    old_tasks = storage.read_snapshot_at(source, ref)
    current_tasks = todoist_snapshot.fetch_tasks() if source == "todoist" else []
    missing = find_missing(old_tasks, current_tasks)

    if not missing:
        print(f"Nothing missing compared to {ref} — {len(current_tasks)} tasks match.")
        return []

    print(f"{len(missing)} task(s) in {ref} are missing from your current {source} list:")
    for t in missing:
        print(f"  - [{t.get('priority', '?')}] {t['content']}")

    if dry_run:
        print("\nDry run — nothing created. Re-run with --no-dry-run to restore these.")
        return missing

    restored = []
    for t in missing:
        new_task = todoist_snapshot.restore_task(t)
        restored.append(new_task)
        print(f"  Restored: {new_task.content}")
    return restored
