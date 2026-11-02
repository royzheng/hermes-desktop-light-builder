export const RELEASE_REPO = 'royzheng/hermes-desktop-light-builder'
export const RELEASE_URL = `https://github.com/${RELEASE_REPO}/releases`

export interface LightRelease {
  tag_name: string
  draft: boolean
  prerelease: boolean
  assets: { name: string; browser_download_url: string }[]
}

export function releaseDetails(release: LightRelease, currentVersion: string) {
  const match = /^v(\d+\.\d+\.\d+)(?:-unsigned\.\d+)?$/.exec(release.tag_name)
  if (!match || release.draft || release.prerelease) throw new Error('Invalid Hermes Light release')
  const version = match[1]
  const asset = (name: string): string => {
    const matches = release.assets.filter(item => item.name === name)
    const expected = `${RELEASE_URL}/download/${release.tag_name}/${name}`
    if (matches.length !== 1 || matches[0].browser_download_url !== expected) {
      throw new Error(`Missing or untrusted release asset: ${name}`)
    }
    return expected
  }
  const current = currentVersion.split('.').map(Number)
  if (current.length !== 3 || current.some(n => !Number.isSafeInteger(n))) throw new Error('Invalid app version')
  const next = version.split('.').map(Number)
  const difference = next.map((n, i) => n - current[i]).find(n => n !== 0) ?? 0
  const name = `HermesLight-${version}-mac-arm64.dmg`
  return { version, name, available: difference > 0, dmg: asset(name), sums: asset('SHA256SUMS.txt') }
}

export function expectedDigest(text: string, name: string): string {
  const matches = text.split('\n').map(line => /^([a-fA-F0-9]{64})\s+\*?(.+)$/.exec(line))
    .filter(match => match?.[2] === name)
  if (matches.length !== 1) throw new Error('Missing or ambiguous DMG checksum')
  return matches[0]![1].toLowerCase()
}
