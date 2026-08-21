import requests

from . import config

BASE_URL = "https://api.clickup.com/api/v2"


def _headers():
    if not config.CLICKUP_TOKEN:
        raise RuntimeError("No ClickUp token found (CLICKUP_API_TOKEN env var or Keychain entry 'clickup_token')")
    return {"Authorization": config.CLICKUP_TOKEN}


def _my_team_and_user():
    resp = requests.get(f"{BASE_URL}/team", headers=_headers(), timeout=20)
    resp.raise_for_status()
    teams = resp.json()["teams"]
    if not teams:
        raise RuntimeError("No ClickUp workspaces found for this token")
    team = teams[0]
    return team["id"], team["members"][0]["user"]["id"]


def fetch_tasks():
    team_id, user_id = _my_team_and_user()
    tasks = []
    page = 0
    while True:
        resp = requests.get(
            f"{BASE_URL}/team/{team_id}/task",
            headers=_headers(),
            params={"assignees[]": user_id, "include_closed": "false", "page": page},
            timeout=20,
        )
        resp.raise_for_status()
        page_tasks = resp.json().get("tasks", [])
        if not page_tasks:
            break
        tasks.extend(page_tasks)
        page += 1
    return tasks


def restore_task(task_dict):
    list_id = (task_dict.get("list") or {}).get("id")
    if not list_id:
        raise ValueError(f"Task '{task_dict.get('name')}' has no source list id, can't restore")
    body = {"name": task_dict["name"], "description": task_dict.get("description") or ""}
    if task_dict.get("due_date"):
        body["due_date"] = int(task_dict["due_date"])
    resp = requests.post(
        f"{BASE_URL}/list/{list_id}/task",
        headers={**_headers(), "Content-Type": "application/json"},
        json=body,
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()
