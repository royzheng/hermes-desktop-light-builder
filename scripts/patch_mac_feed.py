#!/usr/bin/env python3
"""Route the ephemeral upstream macOS package to this repo's GitHub feed."""

import os
import shutil
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
  const installer = require('node:path').join(__dirname, 'packaging/hermes-light-installer/Install.command')
  if (!require('node:fs').existsSync(installer)) {{
    throw new Error('Missing Install.command')
  }}
  module.exports.dmg = {{
    ...module.exports.dmg,
    title: 'Hermes Light Installer',
    background: null,
    backgroundColor: '#f5f5f7',
    window: {{ width: 640, height: 360 }},
    iconSize: 80,
    contents: [
      {{ x: 170, y: 150, type: 'file' }},
      {{ x: 460, y: 150, type: 'file', path: installer }}
    ]
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
    # Fail closed when upstream integration points change.
    root = config.parent
    main_path = root / 'electron/main.ts'
    ui_path = root / 'src/components/update-status.tsx'
    main_source = main_path.read_text()
    ui_source = ui_path.read_text()
    anchor = 'async function createPackagedUpdateStrategy(): Promise<UpdaterStrategy | null> {'
    notes = "const RELEASE_NOTES_URL = 'https://github.com/NousResearch/hermes-agent/releases'"
    if main_source.count(anchor) != 1 or ui_source.count(notes) != 1:
        raise RuntimeError('Upstream update integration changed; review patch before building')
    main_source = "import { LightInstallerStrategy } from './updater/light-installer'\n" + main_source.replace(
        anchor, anchor + "\n  if (process.platform === 'darwin' && app.isPackaged && isLightVariant()) {\n    return new LightInstallerStrategy(app.getVersion(), emitUpdateProgress)\n  }\n")
    ui_source = ui_source.replace(notes, f"const RELEASE_NOTES_URL = 'https://github.com/{EXPECTED_REPO}/releases/latest'")
    status_anchor = '  const status = useStore(isBackend ? $backendUpdateStatus : $updateStatus)'
    if ui_source.count(status_anchor) != 1:
        raise RuntimeError('Upstream release notes state changed')
    ui_source = ui_source.replace(status_anchor, status_anchor + "\n  const releaseNotesUrl = status?.latestTag ? 'https://github.com/royzheng/hermes-desktop-light-builder/releases/tag/' + encodeURIComponent(status.latestTag) : RELEASE_NOTES_URL")
    ui_source = ui_source.replace('href={RELEASE_NOTES_URL}', 'href={releaseNotesUrl}').replace('openExternal?.(RELEASE_NOTES_URL)', 'openExternal?.(releaseNotesUrl)')
    patches = Path(__file__).resolve().parent.parent / 'patches'
    for name in ('light-installer.ts', 'light-release.ts'):
        shutil.copy2(patches / name, root / 'electron/updater' / name)
    main_path.write_text(main_source)
    ui_path.write_text(ui_source)
    installer_dir = config.parent / 'packaging' / 'hermes-light-installer'
    installer_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__).with_name('Install.command'), installer_dir / 'Install.command')
    config.write_text(source.rstrip() + OVERRIDE)
    print(f"Patched {config} to publish the Hermes Light macOS feed to {EXPECTED_REPO}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"patch_mac_feed: {error}", file=sys.stderr)
        sys.exit(1)
