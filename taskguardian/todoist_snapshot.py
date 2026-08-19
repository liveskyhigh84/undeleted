from todoist_api_python.api import TodoistAPI

from . import config


def fetch_tasks():
    if not config.TODOIST_TOKEN:
        raise RuntimeError("No Todoist token found (TODOIST_API_TOKEN env var or Keychain entry 'todoist_token')")
    api = TodoistAPI(config.TODOIST_TOKEN)
    tasks = []
    for page in api.get_tasks():
        tasks.extend(t.to_dict() for t in page)
    return tasks


def restore_task(task_dict):
    api = TodoistAPI(config.TODOIST_TOKEN)
    due = task_dict.get("due") or {}
    return api.add_task(
        content=task_dict["content"],
        description=task_dict.get("description") or None,
        project_id=task_dict.get("project_id"),
        section_id=task_dict.get("section_id"),
        labels=task_dict.get("labels") or None,
        priority=task_dict.get("priority"),
        due_string=due.get("string") if due else None,
    )
