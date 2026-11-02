import assert from 'node:assert/strict'
import { test } from 'node:test'
import { releaseDetails, expectedDigest, RELEASE_URL } from '../patches/light-release.ts'
const tag = 'v2026.11.1060503-unsigned.4'
const name = 'HermesLight-2026.11.1060503-mac-arm64.dmg'
const fixture = () => ({ tag_name: tag, draft: false, prerelease: false,
  assets: [name, 'SHA256SUMS.txt'].map(name => ({ name, browser_download_url: `${RELEASE_URL}/download/${tag}/${name}` })) })
test('timestamp versions compare numerically and do not downgrade', () => {
  assert.equal(releaseDetails(fixture(), '2026.10.30101549').available, true)
  assert.equal(releaseDetails(fixture(), '2026.11.1060503').available, false)
  assert.equal(releaseDetails(fixture(), '2026.12.1').available, false)
})
test('reject prereleases, missing and foreign download assets', () => {
  for (const mutate of [r => r.prerelease = true, r => r.draft = true,
    r => r.assets.pop(), r => r.assets[0].browser_download_url = 'https://example.com/install.dmg',
    r => r.assets.push(r.assets[0]), r => r.tag_name = '../bad']) {
    const release = fixture(); mutate(release)
    assert.throws(() => releaseDetails(release, '2026.10.1'))
  }
})
test('require exact filename and unambiguous SHA256 checksum', () => {
  const line = `${'a'.repeat(64)}  ${name}`
  assert.equal(expectedDigest(line, name), 'a'.repeat(64))
  assert.throws(() => expectedDigest(line, 'different.dmg'))
  assert.throws(() => expectedDigest(`${line}\n${line}`, name))
  assert.throws(() => expectedDigest(`invalid  ${name}`, name))
})
