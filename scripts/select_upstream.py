#!/usr/bin/env python3
"""Select a stable upstream tag and resolve it to an immutable commit."""

import json
import os
import re
import sys
from urllib.parse import quote
from urllib.request import Request, urlopen


API = "https://api.github.com/repos/NousResearch/hermes-agent"
TAG_RE = re.compile(r"^v((?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*))$")


def get_json(path):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "hermes-desktop-light-builder",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(API + path, headers=headers), timeout=30) as response:
        return json.load(response)


def newest_tag():
    tags = get_json("/tags?per_page=100")
    stable = [tag["name"] for tag in tags if TAG_RE.fullmatch(tag["name"])]
    if not stable:
        raise RuntimeError("No stable vX.Y.Z tag found in the latest 100 upstream tags")
    return max(stable, key=lambda value: tuple(map(int, value[1:].split("."))))


def resolve_commit(tag):
    ref = get_json("/git/ref/tags/" + quote(tag, safe=""))
    target = ref["object"]
    for _ in range(5):
        if target["type"] == "commit":
            return target["sha"]
        if target["type"] != "tag":
            break
        target = get_json("/git/tags/" + target["sha"])["object"]
    raise RuntimeError(f"Tag {tag} does not resolve to a commit")


def main():
    requested = os.environ.get("REQUESTED_UPSTREAM_TAG", "").strip()
    tag = requested or newest_tag()
    match = TAG_RE.fullmatch(tag)
    if not match:
        raise ValueError("Upstream tag must match vX.Y.Z (stable tags only)")
    sha = resolve_commit(tag)
    values = {"tag": tag, "version": match.group(1), "sha": sha}
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as stream:
            for key, value in values.items():
                stream.write(f"{key}={value}\n")
    print(f"Selected NousResearch/hermes-agent {tag} @ {sha}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"select_upstream: {error}", file=sys.stderr)
        sys.exit(1)
