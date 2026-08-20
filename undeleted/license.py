import json
import time
from pathlib import Path

import requests

from . import config

CACHE_PATH = Path.home() / ".undeleted" / "license_cache.json"
RECHECK_SECONDS = 7 * 24 * 3600
OFFLINE_GRACE_SECONDS = 30 * 24 * 3600


def _read_cache() -> dict | None:
    if not CACHE_PATH.exists():
        return None
    try:
        return json.loads(CACHE_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _write_cache(valid: bool) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps({
        "key": config.LICENSE_KEY,
        "valid": valid,
        "checked_at": time.time(),
    }))
    CACHE_PATH.chmod(0o600)  # contains the license key — not secret, but no reason to leave it world-readable


def _verify_with_lemonsqueezy() -> bool | None:
    try:
        resp = requests.post(
            "https://api.lemonsqueezy.com/v1/licenses/validate",
            headers={"Accept": "application/json"},
            data={"license_key": config.LICENSE_KEY},
            timeout=10,
        )
        data = resp.json()
        return bool(data.get("valid"))
    except (requests.RequestException, ValueError):
        return None  # network/parse failure, distinct from "invalid key"


def is_licensed() -> bool:
    if not config.LICENSE_REQUIRED:
        return True  # licensing not enabled — personal/dev instance, no gate

    if not config.LICENSE_KEY:
        return False

    cache = _read_cache()
    now = time.time()

    if cache and cache.get("key") == config.LICENSE_KEY:
        age = now - cache.get("checked_at", 0)
        if cache.get("valid") and age < RECHECK_SECONDS:
            return True

    result = _verify_with_lemonsqueezy()

    if result is True:
        _write_cache(True)
        return True

    if result is False:
        _write_cache(False)
        return False

    # result is None: network failed. Fall back to grace period on a
    # previously-valid cached key so a temporary outage doesn't lock out a paying user.
    if cache and cache.get("key") == config.LICENSE_KEY and cache.get("valid"):
        age = now - cache.get("checked_at", 0)
        return age < OFFLINE_GRACE_SECONDS

    return False
