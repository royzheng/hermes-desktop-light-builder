#!/bin/bash
# Install the app beside this script. No backend or user-data changes.
set -euo pipefail

destination=/Applications
launch=true
pause=true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --destination) [[ $# -ge 2 ]] || exit 2; destination="$2"; shift 2 ;;
    --no-open) launch=false; shift ;;
    --no-pause) pause=false; shift ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; exit 2 ;;
  esac
done

stage=''
committed=false
use_sudo=false
privileged() {
  if [[ "$use_sudo" == true ]]; then /usr/bin/sudo "$@"; else "$@"; fi
}
finish() {
  result=$?
  trap - EXIT
  if [[ -n "$stage" ]]; then
    if [[ "$committed" != true && -d "$stage/previous.app" ]]; then
      if [[ ! -e "$target" && ! -L "$target" ]] && privileged /bin/mv "$stage/previous.app" "$target"; then
        printf 'Previous installation restored.\n'
      else
        printf 'Previous installation retained at: %s/previous.app\n' "$stage" >&2
        stage=''
        result=1
      fi
    fi
    if [[ -n "$stage" ]]; then privileged /bin/rm -rf "$stage" || result=1; fi
  fi
  if [[ "$result" -ne 0 ]]; then printf '\nInstallation failed. See the message above.\n' >&2; fi
  if [[ "$pause" == true && -t 0 ]]; then read -r -p 'Press Return to close this installer. ' unused || true; fi
  exit "$result"
}
trap finish EXIT
fail() { printf '%s\n' "$*" >&2; exit 1; }
[[ "$(uname -s)" == Darwin ]] || fail 'This installer requires macOS.'
[[ "$EUID" -ne 0 ]] || fail 'Run this installer as your normal user; it requests administrator access only if needed.'
script_dir="$(cd -- "$(dirname -- "$0")" && pwd -P)"
source_app="$script_dir/Hermes Light.app"
[[ -d "$destination" && ! -L "$destination" ]] || fail 'Installation directory must exist and must not be a symbolic link.'
destination="$(cd -- "$destination" && pwd -P)"
target="$destination/Hermes Light.app"
[[ "$source_app" != "$target" ]] || fail 'Open Install.command from the mounted installer disk.'
check_app() {
  [[ -d "$1" && ! -L "$1" ]] || fail "Missing app or unexpected symbolic link: $1"
  id=$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$1/Contents/Info.plist")
  [[ "$id" == com.nousresearch.hermes-light ]] || fail "Unexpected application identity: $1"
}
check_app "$source_app"
if [[ -e "$target" || -L "$target" ]]; then check_app "$target"; fi
executable=$(/usr/libexec/PlistBuddy -c 'Print :CFBundleExecutable' "$source_app/Contents/Info.plist")
ensure_app_closed() {
  /usr/bin/pgrep -x "$executable" >/dev/null || return 0
  printf '\nHermes Light 正在运行。是否退出并继续安装？[y/N] '
  answer=''
  if ! read -r answer || [[ "$answer" != y && "$answer" != Y ]]; then
    printf '已取消安装，当前应用保持不变。\n'
    pause=false
    exit 0
  fi
  printf '正在请求 Hermes Light 正常退出…\n'
  if ! osascript -e 'if application id "com.nousresearch.hermes-light" is running then tell application id "com.nousresearch.hermes-light" to quit'; then
    fail '无法退出 Hermes Light。请手动退出后重试，尚未替换应用。'
  fi
  for ((attempt=0; attempt<30; attempt++)); do
    /usr/bin/pgrep -x "$executable" >/dev/null || return 0
    /bin/sleep 1
  done
  fail 'Hermes Light 仍在运行（可能有待确认的对话框）。请手动退出后重试，尚未替换应用。'
}
ensure_app_closed
if [[ ! -w "$destination" || ( -e "$target" && ! -w "$target" ) ]]; then
  printf 'Administrator access is needed to update Applications.\n'
  /usr/bin/sudo -v
  use_sudo=true
fi
printf 'Installing Hermes Light…\n'
stage=$(privileged /usr/bin/mktemp -d "$destination/.hermes-light-install.XXXXXX")
privileged /usr/bin/ditto "$source_app" "$stage/Hermes Light.app"
privileged /usr/bin/xattr -r -s -d com.apple.quarantine "$stage/Hermes Light.app"
ensure_app_closed
if [[ -e "$target" || -L "$target" ]]; then
  check_app "$target"
  privileged /bin/mv "$target" "$stage/previous.app"
fi
privileged /bin/mv "$stage/Hermes Light.app" "$target"
committed=true
printf 'Installed successfully: %s\n' "$target"
if [[ "$launch" == true ]]; then /usr/bin/open "$target"; fi
