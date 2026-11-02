// Exercise the real updater with simulated GitHub and macOS boundaries.
const assert = require('node:assert/strict')
const fs = require('node:fs/promises')
const path = require('node:path')
const vm = require('node:vm')
const { createHash } = require('node:crypto')
const ts = require(path.resolve(process.argv[2], 'typescript'))
let responseFor, execute
async function load(name) {
  const source = await fs.readFile(path.join(__dirname, '../patches', name + '.ts'), 'utf8')
  const code = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } }).outputText
  const exports = {}
  const release = name === 'light-installer' ? await load('light-release') : null
  const requireMock = id => {
    if (id === 'electron') return { net: { fetch: (...args) => responseFor(...args) } }
    if (id === './light-release') return release
    if (id === 'node:child_process') {
      const execFile = () => { throw new Error('Use async execFile') }
      execFile[require('node:util').promisify.custom] = async (file, args) => ({ stdout: await execute(file, args), stderr: '' })
      return { execFile }
    }
    return require(id)
  }
  vm.runInNewContext(code, { exports, require: requireMock, Response, AbortSignal, Date, console }, { filename: name })
  return exports
}
;(async () => {
  const { LightInstallerStrategy } = await load('light-installer')
  const tag = 'v2026.11.1060503-unsigned.4'
  const name = 'HermesLight-2026.11.1060503-mac-arm64.dmg'
  const base = `https://github.com/royzheng/hermes-desktop-light-builder/releases/download/${tag}/`
  const bytes = Buffer.from('fixture dmg')
  const checksum = createHash('sha256').update(bytes).digest('hex')
  for (const scenario of ['checksum failure', 'open failure', 'successful handoff']) {
    const commands = []; let directory
    responseFor = async url => {
      if (url.includes('api.github.com')) return Response.json({ tag_name: tag, draft: false, prerelease: false,
        assets: [name, 'SHA256SUMS.txt'].map(name => ({ name, browser_download_url: base + name })) })
      if (url.endsWith('SHA256SUMS.txt')) return new Response(`${scenario === 'checksum failure' ? '0'.repeat(64) : checksum}  ${name}\n`)
      return new Response(bytes)
    }
    execute = async (file, args) => {
      commands.push(file + ' ' + args[0])
      if (file.endsWith('hdiutil') && args[0] === 'attach') {
        const mount = args[4]; directory = path.dirname(mount)
        await fs.writeFile(path.join(mount, 'Install.command'), '#!/bin/bash\n')
      }
      if (file.endsWith('PlistBuddy')) return 'com.nousresearch.hermes-light\n'
      if (file.endsWith('/open') && scenario === 'open failure') throw new Error('Terminal unavailable')
      return ''
    }
    const updater = new LightInstallerStrategy('2026.10.1', () => {})
    assert.equal((await updater.check()).updateAvailable, true)
    if (scenario === 'successful handoff') {
      assert.equal((await updater.apply()).handedOff, true)
      const wrapper = await fs.readFile(path.join(directory, 'Update.command'), 'utf8')
      assert.match(wrapper, /Install.command' --no-pause/)
      assert.match(wrapper, /hdiutil detach/)
      assert(!commands.some(cmd => cmd.endsWith('detach')))
      await fs.rm(directory, { recursive: true })
    } else {
      await assert.rejects(updater.apply(), scenario === 'checksum failure' ? /SHA-256/ : /Terminal unavailable/)
      if (scenario === 'checksum failure') assert.equal(commands.length, 0)
      if (directory) await assert.rejects(fs.access(directory))
    }
    console.log('PASS:', scenario)
  }
})().catch(error => { console.error(error); process.exitCode = 1 })
