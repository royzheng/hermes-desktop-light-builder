#!/usr/bin/env python3
"""Route the ephemeral upstream macOS package to this repo's GitHub feed."""

import os
import sys
from pathlib import Path


EXPECTED_REPO = "royzheng/hermes-desktop-light-builder"
MARKER = "// hermes-desktop-light-builder: GitHub update feed"
OVERRIDE = f"""

{MARKER}
if (process.env.HERMES_DESKTOP_VARIANT === 'light') {{
  if (process.env.GITHUB_REPOSITORY !== '{EXPECTED_REPO}') {{
    throw new Error('Hermes Light builder requires GITHUB_REPOSITORY={EXPECTED_REPO}')
  }}
  module.exports.mac.publish = [{{
    // The packaged Light client requests the stable descriptor at runtime.
    provider: 'github', owner: 'royzheng', repo: 'hermes-desktop-light-builder', channel: 'stable'
  }}]
}}
"""


def main():
    if os.environ.get("GITHUB_REPOSITORY") != EXPECTED_REPO:
        raise RuntimeError(f"GITHUB_REPOSITORY must be {EXPECTED_REPO}")
    config = Path(sys.argv[1])
    source = config.read_text()
    if MARKER in source:
        raise RuntimeError("Update feed patch is already present")
    if "module.exports = {" not in source or "mac: {" not in source:
        raise RuntimeError("Upstream Electron Builder config changed; review patch before building")
    config.write_text(source.rstrip() + OVERRIDE)
    print(f"Patched {config} to publish the Hermes Light macOS feed to {EXPECTED_REPO}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"patch_mac_feed: {error}", file=sys.stderr)
        sys.exit(1)
