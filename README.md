# Hermes Desktop Light Builder

**Languages:** English · [简体中文](README.zh.md) · [繁體中文](README.zh-hant.md) · [日本語](README.ja.md) · [العربية](README.ar.md) · [Русский](README.ru.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Español](README.es.md)

This repository builds **Hermes Light**, the remote-only variant of [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)'s desktop app, for Apple Silicon Macs. It contains its own documentation and GitHub Actions workflow, but does not maintain a copy of the upstream Desktop source. Each build checks out one exact upstream `main` commit. These are source snapshot builds, not official upstream releases.

Hermes Light does not bundle the Hermes Python backend or `agent-payload`. On first launch, choose **Connect to existing Hermes**, enter your server URL, test the connection, and sign in through the app. The build does not run upstream `install.sh` or change your server.

## Download and connect

1. Download the Apple Silicon DMG from this repository's [Releases](https://github.com/royzheng/hermes-desktop-light-builder/releases). Releases ending in `-unsigned.1` are unsigned previews for **manual installation**.
2. Drag **Hermes Light.app** into `/Applications` and open it.
3. Choose **Connect to existing Hermes**. Enter your own HTTPS server URL, select **Test connection**, then sign in and apply the connection. The repository and app package contain no server password or personal server address.

An unsigned preview may be blocked by macOS Gatekeeper. After confirming the download source, allow it in **System Settings → Privacy & Security** or remove quarantine from that app with `xattr -cr`.

## Builds and updates

The [build workflow](.github/workflows/build-light.yml) runs daily at **03:17 UTC** (11:17 Beijing time) and can also be started manually in Actions. It resolves the exact upstream `main` commit, builds the Light variant on a macOS Apple Silicon runner, verifies the app identity, Light payload, update configuration, DMG, ZIP, and update manifest, then publishes the artifacts to this repository's Releases. CI may stop publishing if upstream changes break the build or its checks.

The upstream stable tag available when this repository was created did not include the Light packaging configuration, which is why this workflow tracks `main`. Versions are derived from the upstream commit's UTC timestamp in a three-part numeric format; the Release notes identify the exact commit. CI uses Python only as a temporary build tool. The resulting app does not contain a local Python runtime.

The workflow patches the temporary checkout's [macOS feed configuration](scripts/patch_mac_feed.py) so the packaged `app-update.yml` points to `royzheng/hermes-desktop-light-builder`. It does not change upstream. The ZIP and `stable-mac.yml` are produced for the app's `stable` update channel.

**Unsigned previews cannot provide reliable macOS in-app updates.** They are prereleases, so a stable-channel check may report that there is no production Release. macOS auto-update requires a signed app; this workflow's production path also notarizes it. When the first signed Release is available, install it manually over an unsigned preview; only then verify in-app checking, downloading, and relaunching with a subsequent signed Release.

### Enable signed releases

Add all of these GitHub Actions secrets to publish a signed, notarized production Release. If any are missing, the workflow publishes an `-unsigned.1` prerelease instead.

| Secret | Value |
| --- | --- |
| `MACOS_CERTIFICATE_P12` | Base64-encoded Developer ID Application `.p12` |
| `MACOS_CERTIFICATE_PASSWORD` | Password for the `.p12` |
| `APPLE_API_KEY_P8` | App Store Connect API key `.p8` contents |
| `APPLE_API_KEY_ID` | API key ID |
| `APPLE_API_ISSUER` | API issuer ID |

Do not commit certificates, private keys, or Hermes server passwords. GitHub may disable a scheduled workflow after 60 days without repository activity; if daily builds stop, re-enable it in Actions. See [GitHub's schedule documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).

## Attribution

The Desktop source, product name, and Light variant come from [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent), which is [MIT licensed](https://github.com/NousResearch/hermes-agent/blob/main/LICENSE). This is independent build automation and is **not an official Nous Research release**.
