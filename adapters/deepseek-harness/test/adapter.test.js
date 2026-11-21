import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import test from 'node:test'
import { fileURLToPath } from 'node:url'

import { apply, inject, loadBundledSkill, name } from '../index.js'

const testDirectory = dirname(fileURLToPath(import.meta.url))
const packageRoot = resolve(testDirectory, '..', '..', '..')

test('adapter exposes the expected Cordis identity and dependency', () => {
  assert.equal(name, 'capability-value-test')
  assert.deepEqual(inject, ['skills'])
})

test('adapter loads the unmodified root Skill as a bundled DSH skill', () => {
  const rawSkill = readFileSync(resolve(packageRoot, 'SKILL.md'), 'utf8')
  const skill = loadBundledSkill()

  assert.equal(skill.name, 'capability-value-test')
  assert.match(skill.description, /visual A\/B test/u)
  assert.ok(skill.content.length > 1000)
  assert.ok(rawSkill.endsWith(`${skill.content}\n`) || rawSkill.endsWith(skill.content))
  assert.equal(skill.source, 'bundled')
  assert.equal(skill.path, resolve(packageRoot, 'SKILL.md'))
  assert.deepEqual(skill.resourceBase, { kind: 'directory', path: packageRoot })
})

test('apply registers the skill and returns the registry disposer', () => {
  const disposer = () => undefined
  let registered
  const ctx = {
    skills: {
      register(skill) {
        registered = skill
        return disposer
      },
    },
  }

  assert.equal(apply(ctx), disposer)
  assert.equal(registered.name, 'capability-value-test')
  assert.equal(registered.resourceBase.path, packageRoot)
})
