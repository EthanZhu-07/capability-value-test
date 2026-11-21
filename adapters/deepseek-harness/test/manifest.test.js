import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import test from 'node:test'
import { fileURLToPath } from 'node:url'

const testDirectory = dirname(fileURLToPath(import.meta.url))
const packageRoot = resolve(testDirectory, '..', '..', '..')
const manifest = JSON.parse(readFileSync(resolve(packageRoot, 'package.json'), 'utf8'))

test('package declares an installable DSH bundle', () => {
  assert.equal(manifest.name, 'dsh-capability-value-test')
  assert.equal(
    manifest.dsh.bundle.patch,
    './adapters/deepseek-harness/cordis.patch.yml',
  )
  assert.equal(existsSync(resolve(packageRoot, manifest.dsh.bundle.patch)), true)
})

test('bundle patch mounts the package once', () => {
  const patch = readFileSync(resolve(packageRoot, manifest.dsh.bundle.patch), 'utf8')
  assert.match(patch, /^\s*- insert:/mu)
  assert.match(patch, /^\s+- id: capability-value-test$/mu)
  assert.match(patch, /^\s+name: dsh-capability-value-test$/mu)
})

test('published files include the skill, its resources, and the adapter', () => {
  const published = new Set(manifest.files)
  assert.equal(published.has('SKILL.md'), true)
  assert.equal(published.has('assets/**'), true)
  assert.equal(published.has('scripts/**'), true)
  assert.equal(published.has('adapters/deepseek-harness/index.js'), true)
  assert.equal(published.has('adapters/deepseek-harness/cordis.patch.yml'), true)
})
