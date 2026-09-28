#!/usr/bin/env python3
"""Fail before publishing if the package is not the expected remote-only app."""

import json
import os
import plistlib
import re
import sys
from pathlib import Path


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    release = Path(os.environ["RELEASE_DIR"])
    app = release / "mac-arm64" / "Hermes Light.app"
    resources = app / "Contents" / "Resources"
    require(app.is_dir(), f"Missing packaged app: {app}")
    require(not (resources / "agent-payload").exists(), "Local Hermes runtime was bundled")

    stamp = json.loads((resources / "install-stamp.json").read_text())
    require(stamp.get("payload") == "light", "Build stamp is not Light")
    require(stamp.get("updateMechanism") == "electron-updater", "Native updater is disabled")
    require(stamp.get("commit") == os.environ["UPSTREAM_SHA"], "Build stamp has wrong upstream commit")
    require(stamp.get("displayVersion") == os.environ["UPSTREAM_VERSION"], "Build stamp has wrong version")

    info = plistlib.loads((app / "Contents" / "Info.plist").read_bytes())
    require(info.get("CFBundleIdentifier") == "com.nousresearch.hermes-light", "Wrong app identity")

    update = (resources / "app-update.yml").read_text()
    owner, repo = os.environ["GITHUB_REPOSITORY"].split("/", 1)
    for key, value in (("provider", "github"), ("owner", owner), ("repo", repo)):
        require(re.search(rf"(?m)^{key}:\s*['\"]?{re.escape(value)}['\"]?\s*$", update),
                f"Packaged updater does not point to {key}={value}")

    dmgs = sorted(release.glob("HermesLight-*-mac-arm64.dmg"))
    zips = sorted(release.glob("HermesLight-*-mac-arm64.zip"))
    feeds = sorted(release.glob("*-mac.yml"))
    require(len(dmgs) == len(zips) == len(feeds) == 1, "Expected one DMG, ZIP and macOS update feed")
    require(os.environ["UPSTREAM_VERSION"] in dmgs[0].name, "DMG version differs")
    require(os.environ["UPSTREAM_VERSION"] in zips[0].name, "ZIP version differs")
    require(zips[0].name in feeds[0].read_text(), "Update feed does not reference the ZIP")
    print(f"Verified Hermes Light {os.environ['UPSTREAM_VERSION']} ({os.environ['UPSTREAM_SHA']})")
    print(f"Updater: {owner}/{repo}; artifacts: {dmgs[0].name}, {zips[0].name}, {feeds[0].name}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"verify_build: {error}", file=sys.stderr)
        sys.exit(1)
