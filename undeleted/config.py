import os
import subprocess
import sys


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
CLICKUP_TOKEN = get_token("CLICKUP_API_TOKEN", "clickup_token")
HEALTHCHECKS_URL = os.environ.get("HEALTHCHECKS_URL")
NTFY_TOPIC = os.environ.get("NTFY_TOPIC")

IS_FROZEN = getattr(sys, "frozen", False)

_license_env = os.environ.get("UNDELETED_LICENSE_REQUIRED")
if _license_env is not None:
    LICENSE_REQUIRED = _license_env.lower() in ("1", "true", "yes")
else:
    # Default: gated when running as a built binary (what buyers download),
    # open when running from source (your own dev/personal use). An explicit
    # env var above always overrides this, in either direction.
    LICENSE_REQUIRED = IS_FROZEN

LICENSE_KEY = get_token("UNDELETED_LICENSE_KEY", "undeleted_license")
