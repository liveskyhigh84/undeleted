#!/usr/bin/env python3
"""Launch-ops status check: dates and public read-only APIs only.

Deliberately does NOT auto-post, auto-comment, or auto-participate anywhere.
Hacker News and Reddit both depend on genuine human participation — a bot
faking that gets accounts banned and defeats the actual point. This script
only tracks the parts that are pure waiting (account-age gates) and reads
public data (HN karma/age), so the remaining manual steps take one glance
instead of a mental calendar.
"""
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from undeleted import monitor

ALTERNATIVETO_CREATED = date(2026, 8, 28)
ALTERNATIVETO_ELIGIBLE_DAYS = 7

HN_USERNAME = "liveskyhigh84"


def _today():
    return datetime.now(tz=timezone.utc).date()


def check_alternativeto():
    days_old = (_today() - ALTERNATIVETO_CREATED).days
    days_left = ALTERNATIVETO_ELIGIBLE_DAYS - days_old
    eligible = days_left <= 0
    if eligible:
        print(f"alternativeto.net: ELIGIBLE — account is {days_old} days old. Submit the listing.")
    else:
        print(f"alternativeto.net: waiting — account is {days_old} days old, {days_left} more to go.")
    return eligible


def check_hn():
    try:
        resp = requests.get(f"https://hacker-news.firebaseio.com/v0/user/{HN_USERNAME}.json", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data is None:
            print(f"hacker news: no such user '{HN_USERNAME}'")
            return
        created = datetime.fromtimestamp(data["created"], tz=timezone.utc).date()
    except requests.RequestException as e:
        print(f"hacker news: couldn't check ({e})")
        return
    age_days = (_today() - created).days
    karma = data.get("karma", 0)
    submitted = len(data.get("submitted", []))
    print(f"hacker news: account is {age_days} days old, {karma} karma, {submitted} submissions.")
    print("  HN doesn't publish an exact bar for Show HN eligibility after the new-account")
    print("  restriction — genuine comments/upvotes over time is the only real path. This is")
    print("  informational, not a signal to automate around.")


def main():
    print("UnDeleted launch-ops status\n")
    alt_eligible = check_alternativeto()
    check_hn()
    print()
    print("Still needs you directly (no API for these):")
    print("  - Verify your email on alternativeto.net (your inbox)")
    print("  - Watch for a reply to the Reddit DM sent to Spirited-Bridge8405")
    print("r/todoist: skipped by decision, not tracked here.")

    if "--notify" in sys.argv and alt_eligible:
        monitor.notify("UnDeleted launch-ops: alternativeto.net account is now 7+ days old — submit the listing.")


if __name__ == "__main__":
    main()
