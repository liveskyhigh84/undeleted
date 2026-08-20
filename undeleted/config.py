import os
import subprocess


def _from_keychain(account):
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-a", account, "-s", "undeleted", "-w"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def get_token(env_var, keychain_account):
    token = os.environ.get(env_var)
    if token:
        return token
    return _from_keychain(keychain_account)


TODOIST_TOKEN = get_token("TODOIST_API_TOKEN", "todoist_token")
ASANA_TOKEN = get_token("ASANA_ACCESS_TOKEN", "asana_token")
HEALTHCHECKS_URL = os.environ.get("HEALTHCHECKS_URL")
NTFY_TOPIC = os.environ.get("NTFY_TOPIC")

LICENSE_REQUIRED = os.environ.get("UNDELETED_LICENSE_REQUIRED", "").lower() in ("1", "true", "yes")
LICENSE_KEY = get_token("UNDELETED_LICENSE_KEY", "undeleted_license")
