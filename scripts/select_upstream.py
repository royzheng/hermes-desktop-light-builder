#!/usr/bin/env python3
"""Pin the current upstream main commit and give it a sortable app version."""

from datetime import datetime, timezone
import json
import os
import re
import sys
from urllib.request import Request, urlopen


API = "https://api.github.com/repos/NousResearch/hermes-agent/commits/main"


def main():
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "hermes-desktop-light-builder",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(API, headers=headers), timeout=30) as response:
        commit = json.load(response)

    sha = commit["sha"]
    if not re.fullmatch(r"[a-f0-9]{40}", sha):
        raise RuntimeError("Upstream API returned an invalid commit SHA")
    committed = datetime.fromisoformat(commit["commit"]["committer"]["date"].replace("Z", "+00:00"))
    committed = committed.astimezone(timezone.utc)
    # SemVer's three numeric components stay ordered as year, month, and
    # day/hour/minute/second within the month. Same commit => same version.
    patch = committed.day * 1_000_000 + committed.hour * 10_000 + committed.minute * 100 + committed.second
    version = f"{committed.year}.{committed.month}.{patch}"
    values = {"version": version, "sha": sha}
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as stream:
            for key, value in values.items():
                stream.write(f"{key}={value}\n")
    print(f"Selected NousResearch/hermes-agent main @ {sha} -> {version}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"select_upstream: {error}", file=sys.stderr)
        sys.exit(1)
