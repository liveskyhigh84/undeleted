import requests

from . import config


def ping_healthchecks(status="success"):
    if not config.HEALTHCHECKS_URL:
        return
    url = config.HEALTHCHECKS_URL if status == "success" else f"{config.HEALTHCHECKS_URL}/fail"
    try:
        requests.get(url, timeout=10)
    except requests.RequestException:
        pass


def notify(message):
    if not config.NTFY_TOPIC:
        print(f"[notify, no NTFY_TOPIC set] {message}")
        return
    try:
        requests.post(f"https://ntfy.sh/{config.NTFY_TOPIC}", data=message.encode("utf-8"), timeout=10)
    except requests.RequestException:
        pass
