#!/bin/bash
# Install the app beside this script. No backend or user-data changes.
set -euo pipefail

# Prefer the macOS UI language over Terminal's locale/region. An explicit
# override also makes unattended installs and tests deterministic.
language=${HERMES_INSTALLER_LANGUAGE:-auto}
if [[ "$language" == auto ]]; then
  language=$(/usr/bin/defaults export NSGlobalDomain - 2>/dev/null | /usr/bin/plutil -extract AppleLanguages.0 raw -o - - 2>/dev/null) || language=${LC_ALL:-${LC_MESSAGES:-${LANG:-en}}}
fi
case "$language" in zh*|ZH*) language=zh ;; *) language=en ;; esac
message() {
  if [[ "$language" == zh ]]; then printf '%s' "$2"; else printf '%s' "$1"; fi
}

destination=/Applications
launch=true
pause=true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --destination) [[ $# -ge 2 ]] || exit 2; destination="$2"; shift 2 ;;
    --no-open) launch=false; shift ;;
    --no-pause) pause=false; shift ;;
    *) printf "$(message 'Unknown option: %s\n' '未知选项：%s\n')" "$1" >&2; exit 2 ;;
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
        printf "$(message 'Previous installation restored.\n' '已恢复原来的安装版本。\n')"
      else
        printf "$(message 'Previous installation retained at: %s/previous.app\n' '原来的安装版本保留在：%s/previous.app\n')" "$stage" >&2
        stage=''
        result=1
      fi
    fi
    if [[ -n "$stage" ]]; then privileged /bin/rm -rf "$stage" || result=1; fi
  fi
  if [[ "$result" -ne 0 ]]; then printf "$(message '\nInstallation failed. See the message above.\n' '\n安装失败，请查看上面的提示。\n')" >&2; fi
  if [[ "$pause" == true && -t 0 ]]; then read -r -p "$(message 'Press Return to close this installer. ' '按回车结束安装程序。')" unused || true; fi
  exit "$result"
}
trap finish EXIT
fail() { printf '%s\n' "$*" >&2; exit 1; }
[[ "$(uname -s)" == Darwin ]] || fail "$(message 'This installer requires macOS.' '此安装程序仅支持 macOS。')"
[[ "$EUID" -ne 0 ]] || fail "$(message 'Run this installer as your normal user; it requests administrator access only if needed.' '请以普通用户身份运行；安装程序仅在需要时请求管理员权限。')"
script_dir="$(cd -- "$(dirname -- "$0")" && pwd -P)"
source_app="$script_dir/Hermes Light.app"
[[ -d "$destination" && ! -L "$destination" ]] || fail "$(message 'Installation directory must exist and must not be a symbolic link.' '安装目录必须存在，且不能是符号链接。')"
destination="$(cd -- "$destination" && pwd -P)"
target="$destination/Hermes Light.app"
[[ "$source_app" != "$target" ]] || fail "$(message 'Open Install.command from the mounted installer disk.' '请从已挂载的安装磁盘中打开 Install.command。')"
check_app() {
  [[ -d "$1" && ! -L "$1" ]] || fail "$(message 'Missing app or unexpected symbolic link:' '应用不存在或是意外的符号链接：') $1"
  id=$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$1/Contents/Info.plist")
  [[ "$id" == com.nousresearch.hermes-light ]] || fail "$(message 'Unexpected application identity:' '应用标识不符合预期：') $1"
}
check_app "$source_app"
if [[ -e "$target" || -L "$target" ]]; then check_app "$target"; fi
executable=$(/usr/libexec/PlistBuddy -c 'Print :CFBundleExecutable' "$source_app/Contents/Info.plist")
ensure_app_closed() {
  /usr/bin/pgrep -x "$executable" >/dev/null || return 0
  printf "$(message '\nHermes Light is running. Quit it and continue installing? [y/N] ' '\nHermes Light 正在运行。是否退出并继续安装？[y/N] ')"
  answer=''
  if ! read -r answer || [[ "$answer" != y && "$answer" != Y ]]; then
    printf "$(message 'Installation cancelled. The current app is unchanged.\n' '已取消安装，当前应用保持不变。\n')"
    pause=false
    exit 0
  fi
  printf "$(message 'Requesting Hermes Light to quit normally…\n' '正在请求 Hermes Light 正常退出…\n')"
  if ! osascript -e 'if application id "com.nousresearch.hermes-light" is running then tell application id "com.nousresearch.hermes-light" to quit'; then
    fail "$(message 'Could not quit Hermes Light. Quit it manually and try again; the app has not been replaced.' '无法退出 Hermes Light。请手动退出后重试，尚未替换应用。')"
  fi
  for ((attempt=0; attempt<30; attempt++)); do
    /usr/bin/pgrep -x "$executable" >/dev/null || return 0
    /bin/sleep 1
  done
  fail "$(message 'Hermes Light is still running (a dialog may need confirmation). Quit it manually and try again; the app has not been replaced.' 'Hermes Light 仍在运行（可能有待确认的对话框）。请手动退出后重试，尚未替换应用。')"
}
ensure_app_closed
if [[ ! -w "$destination" || ( -e "$target" && ! -w "$target" ) ]]; then
  printf "$(message 'Administrator access is needed to update Applications.\n' '更新应用程序目录需要管理员权限。\n')"
  /usr/bin/sudo -v
  use_sudo=true
fi
printf "$(message 'Installing Hermes Light…\n' '正在安装 Hermes Light…\n')"
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
printf "$(message 'Installed successfully: %s\n' '安装成功：%s\n')" "$target"
if [[ "$launch" == true ]]; then /usr/bin/open "$target"; fi
