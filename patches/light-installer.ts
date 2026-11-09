// Builder-owned updater: use the same installer as a manual DMG installation.
import { net } from 'electron'
import { execFile } from 'node:child_process'
import { createHash } from 'node:crypto'
import { mkdtemp, mkdir, open, readFile, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { promisify } from 'node:util'
import type { UpdaterStrategy, UpdaterStatusWire, UpdaterApplyResultWire } from './index'
import { RELEASE_REPO, releaseDetails, expectedDigest, type LightRelease } from './light-release'

const run = promisify(execFile)
const quote = (value: string): string => "'" + value.replace(/'/g, "'\\''") + "'"

export class LightInstallerStrategy implements UpdaterStrategy {
  readonly mechanism = 'electron-updater' as const
  private busy = false
  constructor(private readonly version: string,
    private readonly progress: (payload: { stage: string; message: string; percent: number | null }) => void) {}

  private async request(url: string): Promise<Response> {
    const response = await net.fetch(url, { signal: AbortSignal.timeout(30 * 60 * 1000) })
    if (!response.ok) throw new Error(`GitHub download failed (${response.status})`)
    return response
  }

  private async latest() {
    const release = await (await this.request(`https://api.github.com/repos/${RELEASE_REPO}/releases/latest`)).json() as LightRelease
    return { release, details: releaseDetails(release, this.version) }
  }

  async check(): Promise<UpdaterStatusWire> {
    if (this.busy) throw new Error('An update is already in progress.')
    const { release, details } = await this.latest()
    return { supported: true, mechanism: this.mechanism, currentVersion: this.version,
      channel: 'stable', latestTag: release.tag_name, updateAvailable: details.available, fetchedAt: Date.now() }
  }

  async apply(): Promise<UpdaterApplyResultWire> {
    if (this.busy) throw new Error('An update is already in progress.')
    this.busy = true
    let directory: string | undefined
    let mount: string | undefined
    let handedOff = false
    try {
      const { details } = await this.latest()
      if (!details.available) return { ok: true, mechanism: this.mechanism }
      directory = await mkdtemp(join(tmpdir(), 'hermes-light-update-'))
      const dmg = join(directory, details.name)
      const digest = expectedDigest(await (await this.request(details.sums)).text(), details.name)
      this.progress({ stage: 'fetch', message: '正在下载 Hermes Light 安装包…', percent: 0 })
      const response = await this.request(details.dmg)
      if (!response.body) throw new Error('Empty DMG response')
      const reader = response.body.getReader()
      const file = await open(dmg, 'wx', 0o600)
      const hash = createHash('sha256')
      const total = Number(response.headers.get('content-length'))
      let bytes = 0
      let lastProgress = 0
      try {
        for (;;) {
          const { done, value } = await reader.read()
          if (done) break
          await file.writeFile(value)
          hash.update(value)
          bytes += value.length
          if (Date.now() - lastProgress > 250) {
            this.progress({ stage: 'fetch', message: '正在下载 Hermes Light 安装包…', percent: total > 0 ? Math.min(99, bytes / total * 100) : null })
            lastProgress = Date.now()
          }
        }
      } finally { await file.close(); await reader.cancel() }
      if (hash.digest('hex') !== digest) throw new Error('DMG SHA-256 verification failed')
      this.progress({ stage: 'prepare', message: '正在打开安装程序…', percent: 100 })
      mount = join(directory, 'volume')
      await mkdir(mount)
      await run('/usr/bin/hdiutil', ['attach', '-readonly', '-nobrowse', '-mountpoint', mount, dmg])
      const installer = join(mount, 'Install.command')
      await readFile(installer)
      const info = join(mount, 'Hermes Light.app/Contents/Info.plist')
      const { stdout } = await run('/usr/libexec/PlistBuddy', ['-c', 'Print :CFBundleIdentifier', info])
      if (stdout.trim() !== 'com.nousresearch.hermes-light') throw new Error('Unexpected app identity')
      // Terminal owns this process, so it survives the old app quitting. The
      // mounted installer asks for consent and performs a normal app quit.
      const launcher = join(directory, 'Update.command')
      await writeFile(launcher, `#!/bin/bash\n/bin/bash ${quote(installer)} --no-pause\nresult=$?\n/usr/sbin/diskutil eject ${quote(mount)} >/dev/null\n/bin/rm -rf ${quote(directory)}\nif [[ "$result" -ne 0 ]]; then\n  language=$(/usr/bin/defaults export NSGlobalDomain - 2>/dev/null | /usr/bin/plutil -extract AppleLanguages.0 raw -o - - 2>/dev/null)\n  case "$language" in zh*) prompt='更新失败，请查看以上信息。按回车退出。' ;; *) prompt='Update failed. See the message above. Press Return to exit. ' ;; esac\n  read -r -p "$prompt" unused\nfi\nexit "$result"\n`, { mode: 0o700 })
      await run('/usr/bin/open', ['-a', 'Terminal', launcher])
      handedOff = true
      this.progress({ stage: 'restart', message: '安装程序已打开，请在终端确认退出并安装。', percent: 100 })
      return { ok: true, bundled: true, handedOff: true, mechanism: this.mechanism }
    } finally {
      this.busy = false
      if (!handedOff && directory) {
        if (mount) await run('/usr/sbin/diskutil', ['eject', mount]).catch(() => {})
        await rm(directory, { recursive: true, force: true })
      }
    }
  }
}
