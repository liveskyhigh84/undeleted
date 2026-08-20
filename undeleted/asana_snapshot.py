import asana

from . import config

TASK_FIELDS = "name,notes,completed,due_on,due_at,projects.name,tags.name,assignee_status"


def _client():
    if not config.ASANA_TOKEN:
        raise RuntimeError("No Asana token found (ASANA_ACCESS_TOKEN env var or Keychain entry 'asana_token')")
    conf = asana.Configuration()
    conf.access_token = config.ASANA_TOKEN
    return asana.ApiClient(conf)


def fetch_tasks():
    client = _client()
    users_api = asana.UsersApi(client)
    tasks_api = asana.TasksApi(client)

    me = users_api.get_user("me", {"opt_fields": "gid,workspaces.gid,workspaces.name"})
    tasks = []
    for workspace in me.get("workspaces", []):
        opts = {
            "assignee": "me",
            "workspace": workspace["gid"],
            "completed_since": "now",
            "opt_fields": TASK_FIELDS,
        }
        tasks.extend(tasks_api.get_tasks(opts))
    return tasks


def restore_task(task_dict):
    client = _client()
    tasks_api = asana.TasksApi(client)
    projects = task_dict.get("projects") or []
    body = {
        "data": {
            "name": task_dict["name"],
            "notes": task_dict.get("notes", ""),
            "due_on": task_dict.get("due_on"),
            "projects": [p["gid"] for p in projects if "gid" in p],
        }
    }
    return tasks_api.create_task(body, {"opt_fields": TASK_FIELDS})
